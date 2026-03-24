"""Dashboard routes for the PA review web interface.

Returns HTML via Jinja2 templates. The JSON API at /api/v1/... is separate.
HTMX handles all interactivity — no custom JavaScript.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from prior_auth_demo.clinical_review_engine import review_prior_auth_request

logger = logging.getLogger(__name__)

_TEMPLATE_DIR = Path(__file__).resolve().parent / "templates"
_SAMPLE_CASES_DIR = Path(__file__).resolve().parent.parent.parent.parent / "data" / "sample_pa_cases"

templates = Jinja2Templates(directory=str(_TEMPLATE_DIR))

router = APIRouter(tags=["Dashboard"])

# Case display labels in demo order: approval → missing → ambiguous → urgent → denial
DEMO_CASES = [
    {"filename": "01_lumbar_mri_clear_approval.json", "label": "1 — Lumbar MRI (Clear Approval)"},
    {"filename": "04_humira_missing_documentation.json", "label": "4 — Humira (Missing Documentation)"},
    {"filename": "03_spinal_fusion_complex_review.json", "label": "3 — Spinal Fusion (Complex Review)"},
    {"filename": "05_keytruda_urgent_oncology.json", "label": "5 — Keytruda (Urgent Oncology)"},
    {"filename": "02_cosmetic_rhinoplasty_denial.json", "label": "2 — Rhinoplasty (Cosmetic Denial)"},
]


@router.get("/", response_class=HTMLResponse)
async def dashboard(request: Request) -> HTMLResponse:
    """Render the main dashboard page."""
    return templates.TemplateResponse(
        request=request,
        name="review_dashboard.html",
        context={"cases": DEMO_CASES},
    )


@router.post("/dashboard/review", response_class=HTMLResponse)
async def dashboard_review(request: Request, case_name: str = Form(...)) -> HTMLResponse:
    """Submit a PA case for review and return an HTML result fragment."""
    from fhir.resources.R4B.bundle import Bundle

    from prior_auth_demo.healthcare_api_server import _ensure_initialized

    case_path = _SAMPLE_CASES_DIR / case_name
    if not case_path.exists():
        return HTMLResponse(
            '<article><p style="color:var(--color-denied);">Case file not found.</p></article>',
            status_code=404,
        )

    with case_path.open() as f:
        bundle_data: dict[str, Any] = json.load(f)

    bundle = Bundle.model_validate(bundle_data)

    settings, audit_store = await _ensure_initialized()
    result = await review_prior_auth_request(bundle, settings)

    # Store in audit trail with case name
    await audit_store.store_determination(
        case_name=case_name,
        determination=result.determination,
        confidence_score=result.confidence_score,
        clinical_rationale=result.clinical_rationale,
        guideline_citations=result.guideline_citations,
        processing_time_seconds=result.review_duration_seconds,
        full_request_json=json.dumps(bundle_data),
        full_response_json=result.model_dump_json(),
    )

    return templates.TemplateResponse(
        request=request,
        name="fragments/result_card.html",
        context={
            "determination": result.determination,
            "confidence_score": result.confidence_score,
            "clinical_rationale": result.clinical_rationale,
            "guideline_citations": result.guideline_citations,
            "missing_documentation": result.missing_documentation,
            "review_duration_seconds": result.review_duration_seconds,
        },
    )


@router.get("/dashboard/history", response_class=HTMLResponse)
async def dashboard_history(request: Request) -> HTMLResponse:
    """Return HTML table rows for determination history."""
    from prior_auth_demo.healthcare_api_server import _ensure_initialized

    _, audit_store = await _ensure_initialized()
    determinations = await audit_store.list_determinations(limit=20)

    return templates.TemplateResponse(
        request=request,
        name="fragments/history_row.html",
        context={"determinations": determinations},
    )
