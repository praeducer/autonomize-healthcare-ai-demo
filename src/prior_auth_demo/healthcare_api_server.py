"""FastAPI REST API for prior authorization review.

Provides endpoints for submitting PA requests, viewing determinations,
browsing sample cases, and checking system health.
"""

from __future__ import annotations

import json
import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

import httpx
from fastapi import Body, FastAPI, HTTPException, Query
from fastapi.responses import RedirectResponse
from fhir.resources.R4B.bundle import Bundle
from pydantic import ValidationError

from prior_auth_demo.application_settings import ApplicationSettings
from prior_auth_demo.clinical_review_engine import review_prior_auth_request
from prior_auth_demo.determination_audit_store import DeterminationAuditStore
from prior_auth_demo.mock_healthcare_services.member_eligibility import router as eligibility_router

logger = logging.getLogger(__name__)

_SAMPLE_CASES_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "sample_pa_cases"

# Module-level state (initialized in lifespan or lazily on first request)
_settings: ApplicationSettings | None = None
_audit_store: DeterminationAuditStore | None = None

# --- Example payloads for Swagger UI ---

_REVIEW_EXAMPLE_VALUE = {
    "resourceType": "Bundle",
    "id": "pa-bundle-01-lumbar-mri-clear-approval",
    "type": "collection",
    "timestamp": "2026-03-24T10:00:00Z",
    "entry": [
        {
            "fullUrl": "urn:uuid:claim-01",
            "resource": {
                "resourceType": "Claim",
                "id": "claim-01",
                "status": "active",
                "type": {
                    "coding": [
                        {
                            "system": "http://terminology.hl7.org/CodeSystem/claim-type",
                            "code": "professional",
                            "display": "Professional",
                        }
                    ]
                },
                "use": "preauthorization",
                "patient": {"reference": "Patient/pat-01"},
                "created": "2026-03-24",
                "provider": {"reference": "Practitioner/pract-01"},
                "priority": {
                    "coding": [
                        {
                            "system": "http://terminology.hl7.org/CodeSystem/processpriority",
                            "code": "normal",
                            "display": "Normal",
                        }
                    ]
                },
                "insurance": [{"sequence": 1, "focal": True, "coverage": {"reference": "Coverage/cov-01"}}],
                "diagnosis": [
                    {
                        "sequence": 1,
                        "diagnosisCodeableConcept": {
                            "coding": [
                                {
                                    "system": "http://hl7.org/fhir/sid/icd-10-cm",
                                    "code": "M54.5",
                                    "display": "Low back pain",
                                }
                            ]
                        },
                    },
                    {
                        "sequence": 2,
                        "diagnosisCodeableConcept": {
                            "coding": [
                                {
                                    "system": "http://hl7.org/fhir/sid/icd-10-cm",
                                    "code": "M54.41",
                                    "display": "Lumbago with sciatica, right side",
                                }
                            ]
                        },
                    },
                ],
                "item": [
                    {
                        "sequence": 1,
                        "productOrService": {
                            "coding": [
                                {
                                    "system": "http://www.ama-assn.org/go/cpt",
                                    "code": "72148",
                                    "display": "MRI lumbar spine without contrast",
                                }
                            ]
                        },
                    }
                ],
                "supportingInfo": [
                    {
                        "sequence": 1,
                        "category": {
                            "coding": [
                                {
                                    "system": "http://terminology.hl7.org/CodeSystem/claiminformationcategory",
                                    "code": "info",
                                    "display": "Information",
                                }
                            ]
                        },
                        "valueString": (
                            "Patient is a 52-year-old male presenting with chronic low back pain "
                            "and right-sided radiculopathy. Symptoms began 10 weeks ago after "
                            "lifting injury. Pain rated 7/10 on VAS. Positive straight leg raise "
                            "test at 40 degrees on the right."
                        ),
                    },
                    {
                        "sequence": 2,
                        "category": {
                            "coding": [
                                {
                                    "system": "http://terminology.hl7.org/CodeSystem/claiminformationcategory",
                                    "code": "info",
                                    "display": "Information",
                                }
                            ]
                        },
                        "valueString": (
                            "Conservative treatment history: Physical therapy x 12 sessions over "
                            "8 weeks — minimal improvement. NSAIDs x 6 weeks — partial relief. "
                            "Failed conservative treatment per ACR Appropriateness Criteria."
                        ),
                    },
                ],
            },
        },
        {
            "fullUrl": "urn:uuid:pat-01",
            "resource": {
                "resourceType": "Patient",
                "id": "pat-01",
                "identifier": [
                    {
                        "type": {
                            "coding": [
                                {
                                    "system": "http://terminology.hl7.org/CodeSystem/v2-0203",
                                    "code": "MR",
                                    "display": "Medical Record Number",
                                }
                            ]
                        },
                        "value": "MBR-2026-001",
                    }
                ],
                "name": [{"use": "official", "family": "Thompson", "given": ["Robert", "J"]}],
                "gender": "male",
                "birthDate": "1974-03-15",
            },
        },
        {
            "fullUrl": "urn:uuid:pract-01",
            "resource": {
                "resourceType": "Practitioner",
                "id": "pract-01",
                "identifier": [{"system": "http://hl7.org/fhir/sid/us-npi", "value": "1234567893"}],
                "name": [{"family": "Chen", "given": ["David"], "prefix": ["Dr."]}],
                "qualification": [
                    {
                        "code": {
                            "coding": [
                                {
                                    "system": "http://terminology.hl7.org/CodeSystem/v2-0360",
                                    "code": "MD",
                                    "display": "Doctor of Medicine",
                                }
                            ],
                            "text": "Orthopedic Surgery",
                        }
                    }
                ],
            },
        },
        {
            "fullUrl": "urn:uuid:cov-01",
            "resource": {
                "resourceType": "Coverage",
                "id": "cov-01",
                "status": "active",
                "type": {
                    "coding": [
                        {
                            "system": "http://terminology.hl7.org/CodeSystem/v3-ActCode",
                            "code": "PPO",
                            "display": "Preferred Provider Organization",
                        }
                    ]
                },
                "subscriber": {"reference": "Patient/pat-01"},
                "beneficiary": {"reference": "Patient/pat-01"},
                "payor": [{"reference": "Organization/insurer-01", "display": "Acme Health Insurance"}],
            },
        },
    ],
}


async def _ensure_initialized() -> tuple[ApplicationSettings, DeterminationAuditStore]:
    """Lazy initialization — handles both lifespan and test environments."""
    global _settings, _audit_store  # noqa: PLW0603
    if _settings is None:
        _settings = ApplicationSettings()  # type: ignore[call-arg]
    if _audit_store is None:
        _audit_store = DeterminationAuditStore()
        await _audit_store.init_db()
    return _settings, _audit_store


@asynccontextmanager
async def lifespan(application: FastAPI) -> AsyncIterator[None]:
    """Initialize and clean up application resources."""
    await _ensure_initialized()
    logger.info(
        "\n"
        "╔══════════════════════════════════════════════════════════════╗\n"
        "║  Prior Authorization Review — Server Ready                  ║\n"
        "║                                                            ║\n"
        "║  Dashboard:  http://localhost:8000/dashboard                ║\n"
        "║  Swagger UI: http://localhost:8000/docs                    ║\n"
        "║  ReDoc:      http://localhost:8000/redoc                   ║\n"
        "║  Health:     http://localhost:8000/health                  ║\n"
        "╚══════════════════════════════════════════════════════════════╝"
    )
    yield
    if _audit_store:
        await _audit_store.close()


_APP_DESCRIPTION = """\
AI-driven prior authorization clinical review using Claude and FHIR R4.

## Quick Start

1. **Check health** — `GET /health` to verify the server is running
2. **Browse cases** — `GET /api/v1/prior-auth/sample-cases` to see the 5 test cases
3. **Get a case payload** — `GET /api/v1/prior-auth/sample-cases/{name}` to retrieve the full FHIR Bundle
4. **Submit for review** — `POST /api/v1/prior-auth/review` with that Bundle (an example is pre-filled below)
5. **View audit trail** — `GET /api/v1/prior-auth/determinations` to see all past reviews

## Web Dashboard

For a visual interface, visit [the dashboard](/dashboard).

## Demo Cases

| # | Case | Expected Outcome |
|---|------|-----------------|
| 1 | Lumbar MRI | Approved |
| 2 | Cosmetic Rhinoplasty | Denied |
| 3 | Spinal Fusion | Pended for Review |
| 4 | Humira | Pended Missing Info |
| 5 | Keytruda (Urgent) | Approved |
"""

app = FastAPI(
    title="Prior Authorization Review API",
    description=_APP_DESCRIPTION,
    version="0.3.0",
    lifespan=lifespan,
)

app.include_router(eligibility_router, prefix="/mock/eligibility")

# Dashboard routes — HTML responses for web UI (additive, does not affect API routes)
from prior_auth_demo.web_dashboard.dashboard_routes import router as dashboard_router  # noqa: E402

app.include_router(dashboard_router)


# --- Dashboard alias ---


@app.get("/dashboard", include_in_schema=False)
async def dashboard_redirect() -> RedirectResponse:
    """Redirect /dashboard to the root dashboard page."""
    return RedirectResponse(url="/", status_code=301)


# --- API Endpoints ---


@app.get(
    "/health",
    tags=["1. Health"],
    summary="Check system health",
    description=(
        "Returns server status and FHIR server connectivity. Call this first to verify the system is running."
    ),
    response_description="Health status with FHIR server connectivity info",
)
async def health_check() -> dict[str, Any]:
    """System health check with FHIR server connectivity status."""
    settings, _ = await _ensure_initialized()
    fhir_url = settings.fhir_server_url
    fhir_status = "unknown"
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(f"{fhir_url}/metadata")
            fhir_status = "connected" if resp.status_code == 200 else "error"
    except httpx.HTTPError:
        fhir_status = "unavailable"

    return {
        "status": "healthy",
        "fhir_server": fhir_status,
        "version": app.version,
    }


@app.get(
    "/api/v1/prior-auth/sample-cases",
    tags=["2. Sample Cases"],
    summary="List all sample PA cases",
    description=(
        "Returns the filenames of the 5 built-in test cases. "
        "Use a filename from this list with the GET endpoint below to retrieve "
        "the full FHIR Bundle, which you can then POST to /review."
    ),
    response_description="Array of case filenames",
)
async def list_sample_cases() -> list[dict[str, str]]:
    """List available sample PA case files."""
    cases = []
    for f in sorted(_SAMPLE_CASES_DIR.glob("*.json")):
        cases.append({"name": f.name})
    return cases


@app.get(
    "/api/v1/prior-auth/sample-cases/{name}",
    tags=["2. Sample Cases"],
    summary="Get a sample case's FHIR Bundle",
    description=(
        "Retrieve the full FHIR Bundle for a sample case by filename. "
        "Copy the response body and paste it into POST /api/v1/prior-auth/review to run an AI review.\n\n"
        "**Try it:** Use `01_lumbar_mri_clear_approval.json` as the name."
    ),
    response_description="Complete FHIR Bundle ready to submit for review",
)
async def get_sample_case(name: str) -> dict[str, Any]:
    """Get a sample PA case by filename."""
    case_path = (_SAMPLE_CASES_DIR / name).resolve()
    if (
        not case_path.is_relative_to(_SAMPLE_CASES_DIR.resolve())
        or not case_path.exists()
        or case_path.suffix != ".json"
    ):
        raise HTTPException(status_code=404, detail=f"Case not found: {name}")
    with case_path.open() as f:
        data: dict[str, Any] = json.load(f)
    return data


@app.post(
    "/api/v1/prior-auth/review",
    tags=["3. Review"],
    summary="Submit a PA request for AI clinical review",
    description=(
        "Submit a FHIR Bundle containing a Claim (use=preauthorization), Patient, "
        "Practitioner, Coverage, and Conditions. Claude analyzes the clinical data "
        "using 4 tools (clinical data extraction, NPI validation, ICD-10 lookup, "
        "CMS coverage criteria) and returns a determination with confidence score "
        "and clinical rationale.\n\n"
        "**Quick path:** Click 'Try it out', the example payload is pre-filled — just click Execute.\n\n"
        "**From sample cases:** GET a case from /api/v1/prior-auth/sample-cases/{name}, "
        "copy the response, paste it here.\n\n"
        "**Takes 15-30 seconds** — Claude is performing a full clinical review."
    ),
    response_description="AI determination with confidence score, rationale, citations, and FHIR ClaimResponse",
)
async def review_pa_request(
    request_body: dict[str, Any] = Body(
        examples=[_REVIEW_EXAMPLE_VALUE],
    ),
) -> dict[str, Any]:
    """Submit a PA request (FHIR Bundle) for AI clinical review."""
    # Validate as FHIR Bundle
    try:
        bundle = Bundle.model_validate(request_body)
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=f"Invalid FHIR Bundle: {e}") from e

    # Check for Claim with use=preauthorization
    has_claim = False
    if bundle.entry:
        for entry in bundle.entry:
            if entry.resource and entry.resource.get_resource_type() == "Claim":
                has_claim = True
                break
    if not has_claim:
        raise HTTPException(status_code=422, detail="Bundle must contain a Claim resource")

    # Run clinical review
    settings, audit_store = await _ensure_initialized()
    result = await review_prior_auth_request(bundle, settings)

    # Store in audit trail
    det_id = await audit_store.store_determination(
        case_name=None,
        determination=result.determination,
        confidence_score=result.confidence_score,
        clinical_rationale=result.clinical_rationale,
        guideline_citations=result.guideline_citations,
        processing_time_seconds=result.review_duration_seconds,
        full_request_json=json.dumps(request_body),
        full_response_json=result.model_dump_json(),
    )

    response = result.model_dump(mode="json")
    response["audit_id"] = det_id
    return response


@app.get(
    "/api/v1/prior-auth/determinations",
    tags=["4. Audit Trail"],
    summary="List past determinations",
    description=(
        "Returns all stored determinations from the append-only audit trail. "
        "Each entry includes the determination, confidence score, rationale, "
        "and timestamps. Run a review first, then call this to see the result in the audit log."
    ),
    response_description="Array of determination records (most recent first)",
)
async def list_determinations(
    limit: int = Query(default=50, ge=1, le=200, description="Max records to return"),
    offset: int = Query(default=0, ge=0, description="Number of records to skip"),
) -> list[dict[str, Any]]:
    """List stored determinations from the audit trail."""
    _, audit_store = await _ensure_initialized()
    return await audit_store.list_determinations(limit=limit, offset=offset)


@app.get(
    "/api/v1/prior-auth/determinations/{det_id}",
    tags=["4. Audit Trail"],
    summary="Get a single determination by ID",
    description=(
        "Retrieve the full details of a specific determination. "
        "The det_id is returned in the response of POST /review as the 'audit_id' field."
    ),
    response_description="Full determination record including request and response payloads",
)
async def get_determination(det_id: str) -> dict[str, Any]:
    """Get a single stored determination by ID."""
    _, audit_store = await _ensure_initialized()
    result = await audit_store.get_determination(det_id)
    if result is None:
        raise HTTPException(status_code=404, detail=f"Determination not found: {det_id}")
    return result
