"""End-to-end tests for the clinical review engine.

Each test calls the real Anthropic API once per case (results are cached).
Focus: correct determination + rationale quality for demo user stories.

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


pytestmark = [
    pytest.mark.e2e,
    pytest.mark.skipif(not _has_api_key(), reason="ANTHROPIC_API_KEY not set"),
]

_result_cache: dict[str, ClinicalReviewResult] = {}


async def _get_result(filename: str) -> ClinicalReviewResult:
    """Get a cached review result, calling the API only once per case."""
    if filename not in _result_cache:
        with (CASES_DIR / filename).open() as f:
            bundle = Bundle.model_validate(json.load(f))
        settings = ApplicationSettings()  # type: ignore[call-arg]
        _result_cache[filename] = await review_prior_auth_request(bundle, settings)
    return _result_cache[filename]


class TestDemoCases:
    """One test per demo case — validates determination, rationale, and citations."""

    async def test_case_1_lumbar_mri_approved(self) -> None:
        """US-1/US-2: Clear approval with conservative treatment rationale."""
        result = await _get_result("01_lumbar_mri_clear_approval.json")
        assert result.determination == "APPROVED"
        assert result.confidence_score >= 0.70
        assert len(result.guideline_citations) >= 1
        rationale = result.clinical_rationale.lower()
        assert any(t in rationale for t in ["conservative", "radiculopathy", "physical therapy"])

    async def test_case_2_rhinoplasty_denied(self) -> None:
        """US-4: Denial with specific clinical reasons."""
        result = await _get_result("02_cosmetic_rhinoplasty_denial.json")
        assert result.determination == "DENIED"
        rationale = result.clinical_rationale.lower()
        assert any(t in rationale for t in ["cosmetic", "mismatch", "no medical necessity"])

    async def test_case_3_spinal_fusion_pended(self) -> None:
        """US-3: Ambiguous case routes to human review, never auto-denied."""
        result = await _get_result("03_spinal_fusion_complex_review.json")
        assert result.determination in ("PENDED_FOR_REVIEW", "PENDED_MISSING_INFO")

    async def test_case_4_humira_missing_info(self) -> None:
        """US-5: Missing-info case lists what's needed."""
        result = await _get_result("04_humira_missing_documentation.json")
        assert result.determination in ("PENDED_MISSING_INFO", "PENDED_FOR_REVIEW")
        if result.determination == "PENDED_MISSING_INFO":
            assert result.missing_documentation is not None
            assert len(result.missing_documentation) >= 2

    async def test_case_5_keytruda_approved_urgent(self) -> None:
        """US-1/US-2: Urgent oncology approval with NCCN rationale."""
        result = await _get_result("05_keytruda_urgent_oncology.json")
        assert result.determination == "APPROVED"
        rationale = result.clinical_rationale.lower()
        assert any(t in rationale for t in ["nccn", "pd-l1", "oncology", "pembrolizumab"])
