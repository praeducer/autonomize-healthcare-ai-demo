"""Data quality tests for sample PA cases and reference data.

Validates that all FHIR bundles are structurally correct, use proper
coding systems, and contain no real PHI. These tests run without
any API keys or external services.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest
from fhir.resources.R4B.bundle import Bundle

EXPECTED_CASE_FILES = [
    "01_lumbar_mri_clear_approval.json",
    "02_cosmetic_rhinoplasty_denial.json",
    "03_spinal_fusion_complex_review.json",
    "04_humira_missing_documentation.json",
    "05_keytruda_urgent_oncology.json",
]


def _load_all_bundles(cases_dir: Path) -> list[tuple[str, Bundle]]:
    """Load all PA case files as FHIR Bundles."""
    results = []
    for filename in EXPECTED_CASE_FILES:
        filepath = cases_dir / filename
        assert filepath.exists(), f"Missing case file: {filename}"
        with filepath.open() as f:
            data = json.load(f)
        bundle = Bundle.model_validate(data)
        results.append((filename, bundle))
    return results


def _get_resources_by_type(bundle: Bundle, resource_type: str) -> list[dict]:
    """Extract resources of a given type from a Bundle."""
    resources = []
    if bundle.entry:
        for entry in bundle.entry:
            if entry.resource and entry.resource.get_resource_type() == resource_type:
                resources.append(entry.resource.model_dump(exclude_none=True))
    return resources


@pytest.mark.unit
class TestAllSampleCasesExist:
    """All 5 expected PA case files must exist."""

    def test_all_case_files_present(self, sample_cases_dir: Path) -> None:
        """All 5 sample PA case JSON files exist in data/sample_pa_cases/."""
        for filename in EXPECTED_CASE_FILES:
            filepath = sample_cases_dir / filename
            assert filepath.exists(), f"Missing: {filename}"


@pytest.mark.unit
class TestFhirBundleValidity:
    """All PA cases must parse as valid FHIR R4 Bundles."""

    def test_all_sample_cases_parse_as_valid_fhir_bundles(self, sample_cases_dir: Path) -> None:
        """Every case file loads and validates as a FHIR Bundle."""
        bundles = _load_all_bundles(sample_cases_dir)
        assert len(bundles) == 5

    def test_all_bundles_are_collection_type(self, sample_cases_dir: Path) -> None:
        """All bundles must have type 'collection'."""
        for filename, bundle in _load_all_bundles(sample_cases_dir):
            assert bundle.type == "collection", f"{filename}: type is {bundle.type}"


@pytest.mark.unit
class TestClaimPreauthorization:
    """All Claims must use 'preauthorization' per Da Vinci PAS."""

    def test_all_claims_have_preauthorization_use(self, sample_cases_dir: Path) -> None:
        """Every Claim resource has use='preauthorization'."""
        for filename, bundle in _load_all_bundles(sample_cases_dir):
            claims = _get_resources_by_type(bundle, "Claim")
            assert len(claims) >= 1, f"{filename}: no Claim found"
            for claim in claims:
                assert claim["use"] == "preauthorization", f"{filename}: Claim use is '{claim['use']}'"


@pytest.mark.unit
class TestDiagnosisCodes:
    """All diagnosis codes must be valid ICD-10-CM codes in our reference data."""

    def test_all_diagnosis_codes_are_valid_icd10(self, sample_cases_dir: Path, reference_data_dir: Path) -> None:
        """Every diagnosis code in Claims matches the local ICD-10 reference file."""
        from prior_auth_demo.clinical_review_engine import lookup_icd10_code

        tsv_path = reference_data_dir / "icd10cm_codes_2026.tsv"

        for filename, bundle in _load_all_bundles(sample_cases_dir):
            claims = _get_resources_by_type(bundle, "Claim")
            for claim in claims:
                for dx in claim.get("diagnosis", []):
                    concept = dx.get("diagnosisCodeableConcept", {})
                    for coding in concept.get("coding", []):
                        if coding.get("system") == "http://hl7.org/fhir/sid/icd-10-cm":
                            code = coding["code"]
                            result = lookup_icd10_code(code, tsv_path)
                            assert result is not None, f"{filename}: ICD-10 code '{code}' not in reference data"


@pytest.mark.unit
class TestRequiredResources:
    """Each bundle must contain Patient, Practitioner, Coverage, and Condition."""

    def test_all_bundles_contain_required_resources(self, sample_cases_dir: Path) -> None:
        """Every bundle has at least one of each required resource type."""
        required_types = ["Claim", "Patient", "Practitioner", "Coverage", "Condition"]

        for filename, bundle in _load_all_bundles(sample_cases_dir):
            for rtype in required_types:
                resources = _get_resources_by_type(bundle, rtype)
                assert len(resources) >= 1, f"{filename}: missing required resource type '{rtype}'"


@pytest.mark.unit
class TestNoPhiInData:
    """No real PHI should appear in any data file."""

    SSN_PATTERN = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")

    def test_no_phi_in_data_files(self, sample_cases_dir: Path) -> None:
        """No SSN patterns (NNN-NN-NNNN) appear in PA case files."""
        for filename in EXPECTED_CASE_FILES:
            filepath = sample_cases_dir / filename
            if filepath.exists():
                content = filepath.read_text()
                ssn_matches = self.SSN_PATTERN.findall(content)
                assert len(ssn_matches) == 0, f"{filename}: found SSN-like pattern(s): {ssn_matches}"


@pytest.mark.unit
class TestNpiFormat:
    """Practitioner NPI identifiers must be valid 10-digit numbers."""

    def test_all_practitioners_have_valid_npi_format(self, sample_cases_dir: Path) -> None:
        """Every Practitioner has a 10-digit NPI identifier."""
        for filename, bundle in _load_all_bundles(sample_cases_dir):
            practitioners = _get_resources_by_type(bundle, "Practitioner")
            for pract in practitioners:
                npi_found = False
                for ident in pract.get("identifier", []):
                    if ident.get("system") == "http://hl7.org/fhir/sid/us-npi":
                        npi = ident["value"]
                        assert len(npi) == 10, f"{filename}: NPI '{npi}' is not 10 digits"
                        assert npi.isdigit(), f"{filename}: NPI '{npi}' contains non-digits"
                        npi_found = True
                assert npi_found, f"{filename}: Practitioner has no NPI identifier"
