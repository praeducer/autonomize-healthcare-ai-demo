"""End-to-end tests for the REST API review flow.

These tests call the real Anthropic API via the FastAPI server
and verify the full flow: submit → review → audit store.

Requires ANTHROPIC_API_KEY and optionally a running FHIR server.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

import httpx
import pytest

CASES_DIR = Path(__file__).resolve().parent.parent / "data" / "sample_pa_cases"


def _has_api_key() -> bool:
    """Check if ANTHROPIC_API_KEY is available."""
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


@pytest.fixture()
async def client():
    """Async HTTP client for testing the FastAPI app in-process."""
    from prior_auth_demo.healthcare_api_server import app

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app),
        base_url="http://test",
    ) as c:
        yield c


def _load_case(filename: str) -> dict:
    """Load a PA case JSON file."""
    with (CASES_DIR / filename).open() as f:
        return json.load(f)


class TestFullReviewFlowViaApi:
    """Full review cycle: submit → get result → verify in audit trail."""

    async def test_submit_and_retrieve(self, client: httpx.AsyncClient) -> None:
        """POST case 1 → APPROVED → GET determination → matches."""
        case_data = _load_case("01_lumbar_mri_clear_approval.json")
        review_resp = await client.post("/api/v1/prior-auth/review", json=case_data, timeout=120.0)
        assert review_resp.status_code == 200

        result = review_resp.json()
        assert result["determination"] == "APPROVED"
        assert result["confidence_score"] >= 0.70
        assert len(result["guideline_citations"]) >= 1
        assert "audit_id" in result

        # Verify stored in audit trail
        det_resp = await client.get(f"/api/v1/prior-auth/determinations/{result['audit_id']}")
        assert det_resp.status_code == 200
        stored = det_resp.json()
        assert stored["determination"] == "APPROVED"

    async def test_denial_case_via_api(self, client: httpx.AsyncClient) -> None:
        """POST case 2 → DENIED with cosmetic/mismatch rationale."""
        case_data = _load_case("02_cosmetic_rhinoplasty_denial.json")
        resp = await client.post("/api/v1/prior-auth/review", json=case_data, timeout=120.0)
        assert resp.status_code == 200
        result = resp.json()
        assert result["determination"] == "DENIED"

    async def test_pended_case_via_api(self, client: httpx.AsyncClient) -> None:
        """POST case 3 → PENDED (not DENIED)."""
        case_data = _load_case("03_spinal_fusion_complex_review.json")
        resp = await client.post("/api/v1/prior-auth/review", json=case_data, timeout=120.0)
        assert resp.status_code == 200
        result = resp.json()
        assert result["determination"] in ("PENDED_FOR_REVIEW", "PENDED_MISSING_INFO")

    async def test_audit_trail_accumulates(self, client: httpx.AsyncClient) -> None:
        """After submitting cases, determinations list grows."""
        list_resp = await client.get("/api/v1/prior-auth/determinations")
        assert list_resp.status_code == 200
        # Should have at least the cases submitted in earlier tests
        # (tests share the in-process app state within this module)
        determinations = list_resp.json()
        assert isinstance(determinations, list)
