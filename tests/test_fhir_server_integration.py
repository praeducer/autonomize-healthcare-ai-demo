"""Integration tests for HAPI FHIR server connectivity.

These tests require a running HAPI FHIR server with Synthea data loaded.
Run: make up && make load-fhir-data

Skipped automatically if the FHIR server is not reachable.
"""

from __future__ import annotations

import httpx
import pytest

FHIR_BASE_URL = "http://localhost:8080/fhir"


def _fhir_server_available() -> bool:
    """Check if FHIR server is reachable."""
    try:
        resp = httpx.get(f"{FHIR_BASE_URL}/metadata", timeout=5.0)
        return resp.status_code == 200
    except httpx.HTTPError:
        return False


pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(
        not _fhir_server_available(),
        reason="HAPI FHIR server not reachable at localhost:8080",
    ),
]


class TestFhirServerConnectivity:
    """Tests for FHIR server availability and data loading."""

    async def test_fhir_server_is_reachable(self) -> None:
        """GET /fhir/metadata returns 200 with CapabilityStatement."""
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(f"{FHIR_BASE_URL}/metadata")
        assert resp.status_code == 200
        assert resp.json()["resourceType"] == "CapabilityStatement"

    async def test_synthea_patients_loaded(self) -> None:
        """FHIR server has Synthea patients loaded."""
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(f"{FHIR_BASE_URL}/Patient", params={"_summary": "count"})
        assert resp.status_code == 200
        assert resp.json()["total"] > 0

    async def test_fhir_conditions_queryable(self) -> None:
        """Conditions are queryable from the FHIR server."""
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(f"{FHIR_BASE_URL}/Condition", params={"_count": "5"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["resourceType"] == "Bundle"

    async def test_fhir_observations_queryable(self) -> None:
        """Observations are queryable from the FHIR server."""
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(f"{FHIR_BASE_URL}/Observation", params={"_count": "5"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["resourceType"] == "Bundle"
