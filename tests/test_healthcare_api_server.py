"""Tests for the FastAPI healthcare API server.

Unit tests use httpx ASGITransport (no server startup needed).
Integration tests require Docker services.
"""

from __future__ import annotations

import httpx
import pytest


@pytest.fixture()
async def client():
    """Async HTTP client for testing the FastAPI app in-process."""
    from prior_auth_demo.healthcare_api_server import app

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app),
        base_url="http://test",
    ) as c:
        yield c


@pytest.mark.unit
class TestHealthEndpoint:
    """Tests for GET /health."""

    async def test_health_returns_200(self, client: httpx.AsyncClient) -> None:
        """GET /health returns 200 with status, version, and fhir_server fields."""
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "version" in data
        assert "fhir_server" in data
        assert data["version"]  # version field exists and is non-empty


@pytest.mark.unit
class TestSampleCasesEndpoints:
    """Tests for sample case browsing."""

    async def test_sample_cases_returns_5(self, client: httpx.AsyncClient) -> None:
        """GET /api/v1/prior-auth/sample-cases returns 5 case filenames."""
        response = await client.get("/api/v1/prior-auth/sample-cases")
        assert response.status_code == 200
        cases = response.json()
        assert len(cases) == 5
        assert any("lumbar" in c["name"] for c in cases)

    async def test_sample_case_returns_valid_json(self, client: httpx.AsyncClient) -> None:
        """GET /api/v1/prior-auth/sample-cases/{name} returns valid FHIR Bundle JSON."""
        response = await client.get("/api/v1/prior-auth/sample-cases/01_lumbar_mri_clear_approval.json")
        assert response.status_code == 200
        data = response.json()
        assert data["resourceType"] == "Bundle"
        assert data["type"] == "collection"

    async def test_sample_case_not_found_returns_404(self, client: httpx.AsyncClient) -> None:
        """GET /api/v1/prior-auth/sample-cases/nonexistent.json returns 404."""
        response = await client.get("/api/v1/prior-auth/sample-cases/nonexistent.json")
        assert response.status_code == 404


@pytest.mark.unit
class TestReviewEndpoint:
    """Tests for POST /api/v1/prior-auth/review input validation."""

    async def test_invalid_review_input_returns_422(self, client: httpx.AsyncClient) -> None:
        """POST with malformed JSON returns 422."""
        response = await client.post(
            "/api/v1/prior-auth/review",
            json={"bad": "data"},
        )
        assert response.status_code == 422


@pytest.mark.unit
class TestSwaggerDocs:
    """Tests for API documentation."""

    async def test_swagger_docs_accessible(self, client: httpx.AsyncClient) -> None:
        """GET /docs returns 200 (Swagger UI)."""
        response = await client.get("/docs")
        assert response.status_code == 200


@pytest.mark.unit
class TestDeterminationsEndpoints:
    """Tests for determination retrieval."""

    async def test_determinations_list_returns_200(self, client: httpx.AsyncClient) -> None:
        """GET /api/v1/prior-auth/determinations returns 200 with list."""
        response = await client.get("/api/v1/prior-auth/determinations")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    async def test_determination_not_found_returns_404(self, client: httpx.AsyncClient) -> None:
        """GET /api/v1/prior-auth/determinations/{id} with bad ID returns 404."""
        response = await client.get("/api/v1/prior-auth/determinations/nonexistent-uuid")
        assert response.status_code == 404
