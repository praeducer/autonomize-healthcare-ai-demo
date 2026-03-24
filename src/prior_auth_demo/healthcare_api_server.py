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
from fastapi import FastAPI, HTTPException
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
    yield
    if _audit_store:
        await _audit_store.close()


app = FastAPI(
    title="Prior Authorization Review API",
    description="AI-driven prior authorization clinical review using Claude and FHIR R4",
    version="0.2.0",
    lifespan=lifespan,
)

app.include_router(eligibility_router, prefix="/mock/eligibility")


@app.get("/health")
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
        "version": "0.2.0",
    }


@app.get("/api/v1/prior-auth/sample-cases")
async def list_sample_cases() -> list[dict[str, str]]:
    """List available sample PA case files."""
    cases = []
    for f in sorted(_SAMPLE_CASES_DIR.glob("*.json")):
        cases.append({"name": f.name})
    return cases


@app.get("/api/v1/prior-auth/sample-cases/{name}")
async def get_sample_case(name: str) -> dict[str, Any]:
    """Get a sample PA case by filename."""
    case_path = _SAMPLE_CASES_DIR / name
    if not case_path.exists() or not case_path.suffix == ".json":
        raise HTTPException(status_code=404, detail=f"Case not found: {name}")
    with case_path.open() as f:
        data: dict[str, Any] = json.load(f)
    return data


@app.post("/api/v1/prior-auth/review")
async def review_pa_request(request_body: dict[str, Any]) -> dict[str, Any]:
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


@app.get("/api/v1/prior-auth/determinations")
async def list_determinations(limit: int = 50, offset: int = 0) -> list[dict[str, Any]]:
    """List stored determinations from the audit trail."""
    _, audit_store = await _ensure_initialized()
    return await audit_store.list_determinations(limit=limit, offset=offset)


@app.get("/api/v1/prior-auth/determinations/{det_id}")
async def get_determination(det_id: str) -> dict[str, Any]:
    """Get a single stored determination by ID."""
    _, audit_store = await _ensure_initialized()
    result = await audit_store.get_determination(det_id)
    if result is None:
        raise HTTPException(status_code=404, detail=f"Determination not found: {det_id}")
    return result
