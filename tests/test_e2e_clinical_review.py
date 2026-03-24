"""End-to-end tests for the clinical review engine.

These tests call the real Anthropic API (Claude) and validate that
each PA case produces the expected determination. Requires
ANTHROPIC_API_KEY environment variable.

Run with: pytest tests/test_e2e_clinical_review.py -v --timeout=300
"""

from __future__ import annotations

import json
import os
from pathlib import Path

import pytest
from fhir.resources.R4B.bundle import Bundle

from prior_auth_demo.application_settings import ApplicationSettings
from prior_auth_demo.clinical_review_engine import ClinicalReviewResult, review_prior_auth_request

CASES_DIR = Path(__file__).resolve().parent.parent / "data" / "sample_pa_cases"


def _has_api_key() -> bool:
    """Check if ANTHROPIC_API_KEY is available via env var or .env file."""
    if os.environ.get("ANTHROPIC_API_KEY"):
        return True
    env_file = Path(__file__).resolve().parent.parent / ".env"
    if env_file.exists():
        for line in env_file.read_text().splitlines():
            if line.startswith("ANTHROPIC_API_KEY=") and not line.endswith("=your-key-here"):
                return True
    return False


# Skip all E2E tests if no API key is set
pytestmark = [
    pytest.mark.e2e,
    pytest.mark.skipif(
        not _has_api_key(),
        reason="ANTHROPIC_API_KEY not set — skipping E2E tests",
    ),
]


def _load_bundle(filename: str) -> Bundle:
    """Load a PA case file as a FHIR Bundle."""
    filepath = CASES_DIR / filename
    with filepath.open() as f:
        data = json.load(f)
    return Bundle.model_validate(data)


# Cache results per session to minimize API calls across parametrized tests
_result_cache: dict[str, ClinicalReviewResult] = {}


async def _get_result(filename: str, settings: ApplicationSettings) -> ClinicalReviewResult:
    """Get a cached review result, calling the API only once per case."""
    if filename not in _result_cache:
        bundle = _load_bundle(filename)
        _result_cache[filename] = await review_prior_auth_request(bundle, settings)
    return _result_cache[filename]


@pytest.fixture()
def settings() -> ApplicationSettings:
    """Application settings loaded from environment."""
    return ApplicationSettings()


class TestCase01LumbarMri:
    """Case 1: Lumbar MRI with conservative treatment failure."""

    async def test_returns_approved(self, settings: ApplicationSettings) -> None:
        """Lumbar MRI case should return APPROVED determination."""
        result = await _get_result("01_lumbar_mri_clear_approval.json", settings)
        assert result.determination == "APPROVED"

    async def test_confidence_above_threshold(self, settings: ApplicationSettings) -> None:
        """Lumbar MRI case should have confidence >= 0.70."""
        result = await _get_result("01_lumbar_mri_clear_approval.json", settings)
        assert result.confidence_score >= 0.70

    async def test_rationale_mentions_conservative_treatment(self, settings: ApplicationSettings) -> None:
        """Rationale should reference conservative treatment or radiculopathy."""
        result = await _get_result("01_lumbar_mri_clear_approval.json", settings)
        rationale_lower = result.clinical_rationale.lower()
        assert any(term in rationale_lower for term in ["conservative", "radiculopathy", "physical therapy", "failed"])


class TestCase02CosmeticRhinoplasty:
    """Case 2: Cosmetic rhinoplasty with diagnosis mismatch."""

    async def test_returns_denied(self, settings: ApplicationSettings) -> None:
        """Cosmetic rhinoplasty should return DENIED determination."""
        result = await _get_result("02_cosmetic_rhinoplasty_denial.json", settings)
        assert result.determination == "DENIED"

    async def test_rationale_mentions_cosmetic_or_mismatch(self, settings: ApplicationSettings) -> None:
        """Rationale should mention cosmetic nature or diagnosis mismatch."""
        result = await _get_result("02_cosmetic_rhinoplasty_denial.json", settings)
        rationale_lower = result.clinical_rationale.lower()
        assert any(
            term in rationale_lower for term in ["cosmetic", "mismatch", "no medical necessity", "no functional"]
        )


class TestCase03SpinalFusion:
    """Case 3: Complex spinal fusion with ambiguous criteria."""

    async def test_returns_pended(self, settings: ApplicationSettings) -> None:
        """Spinal fusion case should return PENDED_FOR_REVIEW or PENDED_MISSING_INFO."""
        result = await _get_result("03_spinal_fusion_complex_review.json", settings)
        assert result.determination in ("PENDED_FOR_REVIEW", "PENDED_MISSING_INFO")


class TestCase04HumiraMissingDocs:
    """Case 4: Humira with missing step therapy documentation."""

    async def test_returns_pended(self, settings: ApplicationSettings) -> None:
        """Humira case should return PENDED_MISSING_INFO or PENDED_FOR_REVIEW."""
        result = await _get_result("04_humira_missing_documentation.json", settings)
        assert result.determination in ("PENDED_MISSING_INFO", "PENDED_FOR_REVIEW")

    async def test_missing_documentation_listed(self, settings: ApplicationSettings) -> None:
        """Humira case should list specific missing documents if PENDED_MISSING_INFO."""
        result = await _get_result("04_humira_missing_documentation.json", settings)
        if result.determination == "PENDED_MISSING_INFO":
            assert result.missing_documentation is not None
            assert len(result.missing_documentation) >= 2


class TestCase05KeytrudaUrgent:
    """Case 5: Keytruda for lung cancer — urgent oncology."""

    async def test_returns_approved(self, settings: ApplicationSettings) -> None:
        """Keytruda case should return APPROVED determination."""
        result = await _get_result("05_keytruda_urgent_oncology.json", settings)
        assert result.determination == "APPROVED"

    async def test_rationale_mentions_oncology_guidelines(self, settings: ApplicationSettings) -> None:
        """Rationale should reference NCCN, PD-L1, or oncology."""
        result = await _get_result("05_keytruda_urgent_oncology.json", settings)
        rationale_lower = result.clinical_rationale.lower()
        assert any(term in rationale_lower for term in ["nccn", "pd-l1", "oncology", "pembrolizumab", "lung cancer"])


ALL_CASE_FILES = [
    "01_lumbar_mri_clear_approval.json",
    "02_cosmetic_rhinoplasty_denial.json",
    "03_spinal_fusion_complex_review.json",
    "04_humira_missing_documentation.json",
    "05_keytruda_urgent_oncology.json",
]


class TestAllCasesGeneral:
    """Cross-cutting tests for all PA cases."""

    @pytest.mark.parametrize("filename", ALL_CASE_FILES)
    async def test_all_cases_return_within_60_seconds(self, filename: str, settings: ApplicationSettings) -> None:
        """Every case should complete review within 60 seconds."""
        result = await _get_result(filename, settings)
        assert result.review_duration_seconds < 60.0

    @pytest.mark.parametrize("filename", ALL_CASE_FILES)
    async def test_all_cases_have_nonempty_guideline_citations(
        self, filename: str, settings: ApplicationSettings
    ) -> None:
        """Every case should have at least one guideline citation."""
        result = await _get_result(filename, settings)
        assert len(result.guideline_citations) >= 1

    @pytest.mark.parametrize("filename", ALL_CASE_FILES)
    async def test_all_cases_have_valid_fhir_claim_response(self, filename: str, settings: ApplicationSettings) -> None:
        """Every result should contain a valid FHIR ClaimResponse."""
        result = await _get_result(filename, settings)
        assert result.fhir_claim_response is not None
        assert result.fhir_claim_response.get_resource_type() == "ClaimResponse"
