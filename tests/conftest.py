"""Shared test fixtures for prior authorization demo tests.

Markers:
    unit: Unit tests with no external dependencies (mocked services)
    integration: Integration tests requiring Docker services (HAPI FHIR)
    e2e: End-to-end tests requiring ANTHROPIC_API_KEY (full Claude calls)
"""

from pathlib import Path

import pytest


@pytest.fixture()
def sample_cases_dir() -> Path:
    """Path to the sample PA case JSON files."""
    return Path(__file__).resolve().parent.parent / "data" / "sample_pa_cases"


@pytest.fixture()
def reference_data_dir() -> Path:
    """Path to reference data (ICD-10 codes, etc.)."""
    return Path(__file__).resolve().parent.parent / "data" / "reference"
