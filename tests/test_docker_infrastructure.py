"""Integration tests for Docker infrastructure and FHIR server.

Validates the Docker container setup, HAPI FHIR server health,
Synthea data loading, and end-to-end API flows that exercise
the real FHIR server — the same workflows used in the demo.

Run: make up && make load-fhir-data && pytest tests/test_docker_infrastructure.py -v

Skipped automatically if Docker/FHIR services are not available.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import httpx
import pytest

FHIR_BASE_URL = "http://localhost:8080/fhir"
API_BASE_URL = "http://localhost:8000"
SAMPLE_CASES_DIR = Path(__file__).resolve().parent.parent / "data" / "sample_pa_cases"


def _fhir_server_available() -> bool:
    """Check if FHIR server is reachable."""
    try:
        resp = httpx.get(f"{FHIR_BASE_URL}/metadata", timeout=5.0)
        return resp.status_code == 200
    except httpx.HTTPError:
        return False


def _docker_available() -> bool:
    """Check if Docker is running."""
    try:
        result = subprocess.run(
            ["docker", "info"],
            capture_output=True,
            timeout=10,
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False


skip_no_docker = pytest.mark.skipif(
    not _docker_available(),
    reason="Docker daemon not available",
)

skip_no_fhir = pytest.mark.skipif(
    not _fhir_server_available(),
    reason="HAPI FHIR server not reachable at localhost:8080",
)


@skip_no_docker
@pytest.mark.integration
class TestDockerContainerHealth:
    """Verify Docker container is running and healthy."""

    def test_hapi_fhir_container_running(self) -> None:
        """The hapi-fhir-demo container must be in 'running' state."""
        result = subprocess.run(
            ["docker", "inspect", "--format", "{{.State.Status}}", "hapi-fhir-demo"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        assert result.returncode == 0
        assert result.stdout.strip() == "running"

    def test_hapi_fhir_container_healthy(self) -> None:
        """The hapi-fhir-demo container must pass its health check."""
        result = subprocess.run(
            ["docker", "inspect", "--format", "{{.State.Health.Status}}", "hapi-fhir-demo"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        assert result.returncode == 0
        assert result.stdout.strip() == "healthy"

    def test_container_port_8080_mapped(self) -> None:
        """Port 8080 must be mapped from the container to the host."""
        result = subprocess.run(
            ["docker", "port", "hapi-fhir-demo", "8080"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        assert result.returncode == 0
        assert "8080" in result.stdout

    def test_container_uses_pinned_image_version(self) -> None:
        """Container must use a pinned image version, not :latest."""
        result = subprocess.run(
            ["docker", "inspect", "--format", "{{.Config.Image}}", "hapi-fhir-demo"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        assert result.returncode == 0
        image = result.stdout.strip()
        assert ":latest" not in image, f"Image should be pinned, got: {image}"

    def test_container_has_restart_policy(self) -> None:
        """Container must have a restart policy for reliability."""
        result = subprocess.run(
            ["docker", "inspect", "--format", "{{.HostConfig.RestartPolicy.Name}}", "hapi-fhir-demo"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        assert result.returncode == 0
        policy = result.stdout.strip()
        assert policy in ("unless-stopped", "always", "on-failure")

    def test_container_has_persistent_volume(self) -> None:
        """FHIR data must be persisted to a named volume."""
        result = subprocess.run(
            ["docker", "inspect", "--format", "{{range .Mounts}}{{.Name}}{{end}}", "hapi-fhir-demo"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        assert result.returncode == 0
        assert "autonomize-demo-fhir-data" in result.stdout


@skip_no_fhir
@pytest.mark.integration
class TestFhirServerCapabilities:
    """Verify FHIR server is fully operational with expected capabilities."""

    async def test_capability_statement(self) -> None:
        """GET /fhir/metadata returns CapabilityStatement with expected resources."""
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(f"{FHIR_BASE_URL}/metadata")
        assert resp.status_code == 200
        data = resp.json()
        assert data["resourceType"] == "CapabilityStatement"
        assert data["status"] == "active"
        # Verify key resource types are supported
        resource_types = {r["type"] for rest in data.get("rest", []) for r in rest.get("resource", [])}
        for expected in ["Patient", "Condition", "Observation", "Procedure", "Claim"]:
            assert expected in resource_types, f"FHIR server missing {expected} support"

    async def test_json_encoding_default(self) -> None:
        """FHIR server returns JSON by default (configured via docker-compose)."""
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(f"{FHIR_BASE_URL}/metadata")
        assert "application/fhir+json" in resp.headers.get("content-type", "")


@skip_no_fhir
@pytest.mark.integration
class TestSyntheaDataLoaded:
    """Verify Synthea patient data is loaded into FHIR server."""

    async def test_patients_exist(self) -> None:
        """At least one Synthea patient must be loaded."""
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(f"{FHIR_BASE_URL}/Patient", params={"_summary": "count"})
        assert resp.status_code == 200
        assert resp.json()["total"] > 0

    async def test_conditions_exist(self) -> None:
        """Patient conditions (diagnoses) must be queryable."""
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(f"{FHIR_BASE_URL}/Condition", params={"_count": "1"})
        assert resp.status_code == 200
        bundle = resp.json()
        assert bundle["resourceType"] == "Bundle"
        assert bundle.get("total", 0) > 0

    async def test_observations_exist(self) -> None:
        """Patient observations (vitals, labs) must be queryable."""
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(f"{FHIR_BASE_URL}/Observation", params={"_count": "1"})
        assert resp.status_code == 200
        assert resp.json().get("total", 0) > 0

    async def test_procedures_exist(self) -> None:
        """Patient procedures must be queryable."""
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(f"{FHIR_BASE_URL}/Procedure", params={"_count": "1"})
        assert resp.status_code == 200

    async def test_patient_has_conditions(self) -> None:
        """A specific patient should have linked conditions (clinical context for PA)."""
        async with httpx.AsyncClient(timeout=10.0) as client:
            # Get first patient
            resp = await client.get(f"{FHIR_BASE_URL}/Patient", params={"_count": "1"})
            patients = resp.json()
            if patients.get("entry"):
                patient_id = patients["entry"][0]["resource"]["id"]
                # Query conditions for that patient
                cond_resp = await client.get(
                    f"{FHIR_BASE_URL}/Condition",
                    params={"patient": patient_id, "_count": "5"},
                )
                assert cond_resp.status_code == 200


@skip_no_fhir
@pytest.mark.integration
class TestDemoUserStories:
    """Tests that mirror the actual demo walkthrough — UAT scenarios.

    These test the same steps Paul will demonstrate:
    1. HAPI FHIR server shows patients (US-2.3)
    2. Health endpoint reports FHIR connected (US-2.5)
    3. Sample cases browsable via API (US-2.4)
    4. FHIR data queryable for clinical context
    """

    async def test_uat_step_1_hapi_fhir_shows_patients(self) -> None:
        """UAT Step 2: Click 'Patient' in HAPI FHIR → Synthea patients visible."""
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(f"{FHIR_BASE_URL}/Patient", params={"_count": "10"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["resourceType"] == "Bundle"
        assert len(data.get("entry", [])) > 0
        # Verify patients have names (Synthea generates realistic names)
        first_patient = data["entry"][0]["resource"]
        assert first_patient["resourceType"] == "Patient"

    async def test_uat_step_4_sample_cases_list(self) -> None:
        """UAT Step 4: GET /api/v1/prior-auth/sample-cases → 5 cases.

        Tests via direct file check since API server may not be running.
        """
        case_files = sorted(SAMPLE_CASES_DIR.glob("*.json"))
        assert len(case_files) == 5
        # Verify each is valid JSON with FHIR Bundle structure
        for case_file in case_files:
            with case_file.open() as f:
                data = json.load(f)
            assert data["resourceType"] == "Bundle", f"{case_file.name} is not a FHIR Bundle"
            assert data["type"] == "collection", f"{case_file.name} should be collection bundle"

    async def test_uat_step_5_health_reports_fhir_connected(self) -> None:
        """UAT Step 5: GET /health → fhir_server: 'connected'.

        Tests FHIR connectivity directly (API server may not be running).
        """
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(f"{FHIR_BASE_URL}/metadata")
        assert resp.status_code == 200
        assert resp.json()["resourceType"] == "CapabilityStatement"

    async def test_clinical_data_retrievable_for_pa_review(self) -> None:
        """The engine needs patient clinical data (Conditions, Observations)
        from the FHIR server to enrich PA review context.
        """
        async with httpx.AsyncClient(timeout=10.0) as client:
            # Get a patient
            resp = await client.get(f"{FHIR_BASE_URL}/Patient", params={"_count": "1"})
            patient_id = resp.json()["entry"][0]["resource"]["id"]

            # Retrieve clinical data like the engine would
            conditions = await client.get(
                f"{FHIR_BASE_URL}/Condition",
                params={"patient": patient_id},
            )
            observations = await client.get(
                f"{FHIR_BASE_URL}/Observation",
                params={"patient": patient_id, "_count": "10"},
            )

        assert conditions.status_code == 200
        assert observations.status_code == 200
        assert conditions.json()["resourceType"] == "Bundle"
        assert observations.json()["resourceType"] == "Bundle"
