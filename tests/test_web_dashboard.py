"""Tests for the web dashboard.

Validates dashboard renders correctly and existing API routes
are not affected by the dashboard addition.
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
class TestDashboardRenders:
    """Tests for dashboard HTML rendering."""

    async def test_dashboard_root_returns_200_html(self, client: httpx.AsyncClient) -> None:
        """GET / returns 200 with HTML content."""
        response = await client.get("/")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]

    async def test_dashboard_contains_case_selector(self, client: httpx.AsyncClient) -> None:
        """Dashboard HTML includes all 5 PA case names."""
        response = await client.get("/")
        html = response.text
        assert "Lumbar MRI" in html
        assert "Rhinoplasty" in html
        assert "Spinal Fusion" in html
        assert "Humira" in html
        assert "Keytruda" in html

    async def test_dashboard_contains_htmx_attributes(self, client: httpx.AsyncClient) -> None:
        """Dashboard HTML includes HTMX attributes for interactivity."""
        response = await client.get("/")
        html = response.text
        assert "hx-post" in html
        assert "hx-target" in html
        assert "hx-get" in html


@pytest.mark.unit
class TestDashboardAlias:
    """Tests for /dashboard redirect alias."""

    async def test_dashboard_alias_redirects_to_root(self, client: httpx.AsyncClient) -> None:
        """GET /dashboard returns 302 redirect to /."""
        response = await client.get("/dashboard", follow_redirects=False)
        assert response.status_code == 302
        assert response.headers["location"] == "/"

    async def test_dashboard_alias_follows_to_html(self, client: httpx.AsyncClient) -> None:
        """GET /dashboard with follow_redirects returns the dashboard HTML."""
        response = await client.get("/dashboard", follow_redirects=True)
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
        assert "Prior Authorization Review" in response.text


@pytest.mark.unit
class TestDashboardCrossLinks:
    """Tests for cross-links between dashboard and Swagger UI."""

    async def test_dashboard_footer_links_to_swagger(self, client: httpx.AsyncClient) -> None:
        """Dashboard footer includes link to /docs (Swagger UI)."""
        response = await client.get("/")
        html = response.text
        assert 'href="/docs"' in html

    async def test_dashboard_footer_links_to_redoc(self, client: httpx.AsyncClient) -> None:
        """Dashboard footer includes link to /redoc."""
        response = await client.get("/")
        html = response.text
        assert 'href="/redoc"' in html

    async def test_dashboard_footer_links_to_health(self, client: httpx.AsyncClient) -> None:
        """Dashboard footer includes link to /health."""
        response = await client.get("/")
        html = response.text
        assert 'href="/health"' in html


@pytest.mark.unit
class TestDashboardHistoryRefresh:
    """Tests for HTMX history auto-refresh after review submit."""

    async def test_form_triggers_history_refresh(self, client: httpx.AsyncClient) -> None:
        """Review form includes hx-on attribute to refresh history after submission."""
        response = await client.get("/")
        html = response.text
        assert "hx-on::after-request" in html
        assert "history-body" in html


@pytest.mark.unit
class TestApiNotAffected:
    """Existing API and Swagger routes must still work after dashboard addition."""

    async def test_swagger_still_accessible(self, client: httpx.AsyncClient) -> None:
        """GET /docs still returns Swagger UI."""
        response = await client.get("/docs")
        assert response.status_code == 200

    async def test_api_health_still_works(self, client: httpx.AsyncClient) -> None:
        """GET /health still returns JSON with status."""
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["version"] == "0.3.0"

    async def test_api_sample_cases_still_works(self, client: httpx.AsyncClient) -> None:
        """GET /api/v1/prior-auth/sample-cases still returns JSON list."""
        response = await client.get("/api/v1/prior-auth/sample-cases")
        assert response.status_code == 200
        cases = response.json()
        assert len(cases) == 5
        assert isinstance(cases[0], dict)
