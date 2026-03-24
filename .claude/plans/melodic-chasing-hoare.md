# Build Step 1: Core Clinical Review Engine — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a CLI-based prior authorization review engine that uses Claude with tool use to evaluate 5 PA cases and produce structured clinical determinations.

**Architecture:** Anthropic SDK tool use loop — the engine sends a FHIR Claim Bundle to Claude with 4 tools (NPI validation, ICD-10 lookup, CMS coverage criteria, clinical data retrieval). Claude calls tools iteratively, then returns a structured determination. The engine applies confidence routing and wraps the result in a FHIR ClaimResponse.

**Tech Stack:** Python 3.12+, Anthropic SDK (direct), fhir.resources R4B, pydantic-settings, polyfactory (tests)

---

## Context

This is Build Step 1 of a progressive demo for an Autonomize AI interview. It proves the core AI determination works via CLI. Later steps add REST API (Step 2), web dashboard (Step 3), and Azure deployment (Steps 4-5). Each step is independently demo-able.

The repo scaffolding exists (pyproject.toml, Makefile, conftest.py, __init__.py stubs, ICD-10 reference data with 131 codes). No implementation code or PA case files exist yet.

---

## Files to Create

| File | Purpose |
|------|---------|
| `src/prior_auth_demo/application_settings.py` | Pydantic BaseSettings (env vars) |
| `src/prior_auth_demo/clinical_review_engine.py` | Core AI engine: model, tools, Claude loop, routing |
| `src/prior_auth_demo/command_line_demo.py` | CLI entry point (argparse, color output) |
| `data/reference/cms_coverage_criteria.json` | Local coverage criteria for 5 demo procedures |
| `data/sample_pa_cases/01_lumbar_mri_clear_approval.json` | PA case: APPROVED |
| `data/sample_pa_cases/02_cosmetic_rhinoplasty_denial.json` | PA case: DENIED |
| `data/sample_pa_cases/03_spinal_fusion_complex_review.json` | PA case: PENDED_FOR_REVIEW |
| `data/sample_pa_cases/04_humira_missing_documentation.json` | PA case: PENDED_MISSING_INFO |
| `data/sample_pa_cases/05_keytruda_urgent_oncology.json` | PA case: APPROVED (urgent) |
| `tests/test_data_quality.py` | FHIR bundle validation tests |
| `tests/test_clinical_review_engine.py` | Engine unit tests (~25 tests) |
| `tests/test_e2e_clinical_review.py` | E2E tests with real Claude API (~15 tests) |

## Existing Files to Reuse

| File | What it provides |
|------|-----------------|
| `data/reference/icd10cm_codes_2026.tsv` | 131 ICD-10-CM codes (all 5 cases' codes verified present) |
| `tests/conftest.py` | `sample_cases_dir` and `reference_data_dir` fixtures |
| `pyproject.toml` | Dependencies, pytest config (asyncio_mode=auto, markers) |
| `Makefile` | All make targets already defined |
| `.env.example` | Config template (ANTHROPIC_API_KEY, thresholds, model ID) |

---

## Key Design Decisions

1. **CMS coverage criteria = local JSON file** (not runtime MCP calls). MCP servers are a Claude Code protocol, not available to the Python app at runtime. A curated JSON file with criteria for our 5 procedures ensures demo reliability and deterministic behavior.

2. **NPI validation = local Luhn-10 check**. No API call needed — validates format and check digit per CMS 45 CFR 162.406.

3. **Bundle type = "collection"** (not "transaction"). We're reading from files, not POSTing to a FHIR server.

4. **Claude drives all analysis via tool use loop**. The engine dispatches tool calls and returns results. Claude reasons iteratively until producing a final structured JSON determination.

5. **Confidence routing preserves explicit clinical determinations**. DENIED, PENDED_MISSING_INFO, PENDED_FOR_REVIEW are always preserved. Only APPROVED is subject to confidence thresholds (>= 0.85 auto-approve, else route to human review). Never auto-deny.

6. **Three-layer JSON parsing fallback** for Claude responses: code-block JSON → raw JSON regex → brace-matching → safe default (PENDED_FOR_REVIEW).

---

## Task 1: Application Settings

**Files:**
- Create: `src/prior_auth_demo/application_settings.py`
- Create: `tests/test_clinical_review_engine.py` (initial file with settings tests)

**Step 1:** Write failing tests in `tests/test_clinical_review_engine.py`:
- `TestApplicationSettings.test_settings_loads_defaults` — construct with `ANTHROPIC_API_KEY="test-key"`, assert `claude_model_id == "claude-sonnet-4-6"`, thresholds 0.85/0.60, log_level "INFO"
- `TestApplicationSettings.test_settings_requires_api_key` — construct with no args, expect `ValidationError`

**Step 2:** Run: `pytest tests/test_clinical_review_engine.py::TestApplicationSettings -v`
Expected: FAIL (ImportError)

**Step 3:** Implement `application_settings.py`:
- `BaseSettings` with `SettingsConfigDict(env_file=".env", case_sensitive=False)`
- `anthropic_api_key: SecretStr` (required, never logged)
- `claude_model_id: str` (default: `claude-sonnet-4-6`)
- `log_level: str` (default: `INFO`)
- `auto_approve_confidence_threshold: float` (default: 0.85, ge=0.0, le=1.0)
- `human_review_confidence_threshold: float` (default: 0.60, ge=0.0, le=1.0)
- `fhir_server_url: str` (default: `http://localhost:8080/fhir`)

**Step 4:** Run: `pytest tests/test_clinical_review_engine.py::TestApplicationSettings -v`
Expected: PASS (2 tests)

**Step 5:** Commit: `feat: add application settings with pydantic-settings`

---

## Task 2: ClinicalReviewResult Model

**Files:**
- Create: `src/prior_auth_demo/clinical_review_engine.py` (stub with model only)
- Modify: `tests/test_clinical_review_engine.py`

**Step 1:** Add tests to `tests/test_clinical_review_engine.py`:
- `TestClinicalReviewResultModel.test_model_validates_with_all_fields` — construct with valid ClaimResponse
- `TestClinicalReviewResultModel.test_model_rejects_invalid_determination` — "MAYBE" → ValidationError
- `TestClinicalReviewResultModel.test_model_rejects_confidence_out_of_range` — 1.5 → ValidationError
- `TestClinicalReviewResultModel.test_model_with_polyfactory` — ModelFactory builds valid instance (pre-build ClaimResponse since polyfactory can't auto-generate FHIR models)

**Step 2:** Run: `pytest tests/test_clinical_review_engine.py::TestClinicalReviewResultModel -v`
Expected: FAIL (ImportError)

**Step 3:** Create `clinical_review_engine.py` with:
```python
class ClinicalReviewResult(BaseModel):
    determination: Literal["APPROVED", "DENIED", "PENDED_FOR_REVIEW", "PENDED_MISSING_INFO"]
    confidence_score: float = Field(ge=0.0, le=1.0)
    clinical_rationale: str
    guideline_citations: list[str]
    missing_documentation: list[str] | None = None
    fhir_claim_response: ClaimResponse
    review_duration_seconds: float = Field(ge=0.0)
```

**Step 4:** Run: `pytest tests/test_clinical_review_engine.py::TestClinicalReviewResultModel -v`
Expected: PASS (4 tests)

**Step 5:** Commit: `feat: add ClinicalReviewResult pydantic model`

---

## Task 3: ICD-10 Lookup Function

**Files:**
- Modify: `src/prior_auth_demo/clinical_review_engine.py`
- Modify: `tests/test_clinical_review_engine.py`

**Step 1:** Add tests:
- `TestIcd10Lookup.test_lookup_returns_correct_description` — M54.5 → "Low back pain"
- `TestIcd10Lookup.test_lookup_returns_none_for_invalid_code` — ZZ99.99 → None
- `TestIcd10Lookup.test_lookup_finds_oncology_code` — C34.11 → "upper lobe"
- `TestIcd10Lookup.test_lookup_finds_rheumatoid_arthritis_code` — M05.79 → "rheumatoid"

Uses `reference_data_dir` fixture from conftest.py.

**Step 2:** Run: `pytest tests/test_clinical_review_engine.py::TestIcd10Lookup -v`
Expected: FAIL (ImportError)

**Step 3:** Add `lookup_icd10_code(code, tsv_path)` to engine. Reads TSV with csv.DictReader, returns `{"code": ..., "description": ...}` or None.

**Step 4:** Run: `pytest tests/test_clinical_review_engine.py::TestIcd10Lookup -v`
Expected: PASS (4 tests)

**Step 5:** Commit: `feat: add ICD-10 code lookup from local TSV`

---

## Task 4: CMS Coverage Criteria Reference Data

**Files:**
- Create: `data/reference/cms_coverage_criteria.json`

**Step 1:** Create JSON file with coverage criteria for 5 procedure codes: `72148` (MRI lumbar), `30400` (rhinoplasty), `22612` (spinal fusion), `J0135` (adalimumab), `J9271` (pembrolizumab).

Each entry has: `procedure_code`, `procedure_description`, `coding_system`, `coverage_requirements[]`, `auto_approve_criteria[]`, `denial_criteria[]`, `references[]`.

References use real CMS LCD/NCD identifiers (L35028, NCD 160.16, L37950, L33822, NCD 110.17) and clinical guideline sources (ACR, NASS, ACR, NCCN).

**Step 2:** Validate: `python -c "import json; json.load(open('data/reference/cms_coverage_criteria.json')); print('Valid JSON')"`

**Step 3:** Commit: `feat: add CMS coverage criteria reference data`

---

## Task 5: Five PA Case FHIR Bundles

**Files:**
- Create: 5 JSON files in `data/sample_pa_cases/`

Each is a FHIR Bundle (type: "collection") with entries: Claim (use: "preauthorization"), Patient, Practitioner (with NPI), Coverage, Condition(s).

| Case | Expected | Key Clinical Signal |
|------|----------|-------------------|
| 01 | APPROVED | Conservative tx failure + radiculopathy |
| 02 | DENIED | Cosmetic + L57.0/30400 dx-procedure mismatch |
| 03 | PENDED_FOR_REVIEW | Only 8 PT sessions (below 12), no ESI, A1C 8.2%, BMI 34 |
| 04 | PENDED_MISSING_INFO | "Failed methotrexate" but no dose/duration/labs/DAS28 |
| 05 | APPROVED (urgent) | PD-L1 >= 50%, no EGFR/ALK, ECOG 1, NCCN Category 1 |

NPI values must pass Luhn-10 validation. Verify each with the algorithm before writing.

All ICD-10 codes confirmed present in `icd10cm_codes_2026.tsv`: M54.5, M54.41, L57.0, M47.816, M48.06, E11.9, M05.79, C34.11, C77.1.

**Step 1:** Create all 5 JSON files with valid FHIR structure

**Step 2:** Validate each parses: `python -c "from fhir.resources.R4B.bundle import Bundle; import json; Bundle.model_validate(json.load(open('data/sample_pa_cases/01_lumbar_mri_clear_approval.json')))"`

**Step 3:** Commit: `feat: add 5 sample PA cases as FHIR R4 Bundles`

---

## Task 6: Data Quality Tests

**Files:**
- Create: `tests/test_data_quality.py`

**Step 1:** Write tests (all @pytest.mark.unit):
- `TestAllSampleCasesExist.test_all_case_files_present` — 5 files exist
- `TestFhirBundleValidity.test_all_sample_cases_parse_as_valid_fhir_bundles` — all parse as Bundle
- `TestFhirBundleValidity.test_all_bundles_are_collection_type`
- `TestClaimPreauthorization.test_all_claims_have_preauthorization_use`
- `TestDiagnosisCodes.test_all_diagnosis_codes_are_valid_icd10` — cross-validates against TSV
- `TestRequiredResources.test_all_bundles_contain_required_resources` — Claim, Patient, Practitioner, Coverage, Condition
- `TestNoPhiInData.test_no_phi_in_data_files` — scan for SSN patterns (NNN-NN-NNNN)
- `TestNpiFormat.test_all_practitioners_have_valid_npi_format` — 10-digit numeric NPI

**Step 2:** Run: `pytest tests/test_data_quality.py -v`
Expected: PASS (8 tests)

**Step 3:** Commit: `test: add FHIR data quality tests for PA cases`

---

## Task 7: Clinical Review Engine (Core AI)

**Files:**
- Modify: `src/prior_auth_demo/clinical_review_engine.py` (add full implementation)
- Modify: `tests/test_clinical_review_engine.py` (add routing + NPI tests)

**Step 1:** Add tests:

`TestConfidenceRouting` (6 tests):
- 0.90 APPROVED → APPROVED (auto-approve)
- 0.95 DENIED → DENIED (preserved)
- 0.70 APPROVED → PENDED_FOR_REVIEW (below threshold)
- 0.40 APPROVED → PENDED_FOR_REVIEW (never auto-deny)
- 0.90 PENDED_MISSING_INFO → PENDED_MISSING_INFO (preserved)
- 0.85 APPROVED → APPROVED (exact threshold)

`TestNpiValidation` (4 tests):
- "1234567893" → valid
- "1234567890" → invalid check digit
- "12345" → wrong length
- "123456789A" → non-numeric

`TestCmsCoverageLookup` (3 tests):
- "72148" → found with requirements
- "99999" → None
- "J9271" → found, references include "NCCN"

`TestRetrieveClinicalData` (2 tests):
- Bundle extraction finds patients, conditions, supporting_info
- Claim details have use="preauthorization"

**Step 2:** Run: `pytest tests/test_clinical_review_engine.py -v -m unit` (new tests fail)

**Step 3:** Implement in `clinical_review_engine.py`:
- `validate_npi(npi: str) -> dict` — Luhn-10 with 80840 prefix
- `check_cms_coverage(procedure_code, json_path) -> dict | None` — reads local JSON
- `retrieve_clinical_data(bundle: Bundle) -> dict` — extracts resources from Bundle
- `apply_confidence_routing(raw_determination, confidence, thresholds) -> str`
- `TOOL_DEFINITIONS` — 4 tool schemas for Claude
- `SYSTEM_PROMPT` — clinical reviewer instructions
- `review_prior_auth_request(bundle, settings) -> ClinicalReviewResult` — main async function with tool use loop
- `_dispatch_tool()`, `_parse_determination()`, `_build_claim_response()` — helpers

**Step 4:** Run: `pytest tests/test_clinical_review_engine.py -v -m unit`
Expected: PASS (~25 tests)

**Step 5:** Commit: `feat: implement clinical review engine with Claude tool use`

---

## Task 8: CLI Demo

**Files:**
- Create: `src/prior_auth_demo/command_line_demo.py`

**Step 1:** Add basic tests:
- `TestCliModule.test_module_is_importable`
- `TestCliModule.test_format_determination_badge` — APPROVED/DENIED/PENDED produce correct strings

**Step 2:** Implement CLI:
- `--case <path>` (single case) and `--all` (all 5 cases) via argparse mutually exclusive group
- `format_determination_badge()` — ANSI color codes (green/red/yellow)
- `print_result()` — pretty-print determination, confidence, rationale, citations, missing docs, timing
- `review_single_case()` / `review_all_cases()` — async functions
- `main()` — entry point using `asyncio.run()`
- Summary table after `--all` run

**Step 3:** Run: `pytest tests/test_clinical_review_engine.py::TestCliModule -v -m unit`
Expected: PASS

**Step 4:** Commit: `feat: add CLI demo with color-coded output`

---

## Task 9: E2E Tests

**Files:**
- Create: `tests/test_e2e_clinical_review.py`

All tests marked `@pytest.mark.e2e`, skip if no ANTHROPIC_API_KEY.

**Step 1:** Write E2E tests:

Per-case tests:
- Case 1: determination == APPROVED, confidence >= 0.70, rationale mentions conservative/radiculopathy
- Case 2: determination == DENIED, rationale mentions cosmetic/mismatch
- Case 3: determination in (PENDED_FOR_REVIEW, PENDED_MISSING_INFO)
- Case 4: determination in (PENDED_MISSING_INFO, PENDED_FOR_REVIEW), missing_documentation >= 2 items if PENDED_MISSING_INFO
- Case 5: determination == APPROVED, rationale mentions NCCN/PD-L1/oncology

Cross-cutting parametrized tests (all 5 cases):
- `test_all_cases_return_within_60_seconds`
- `test_all_cases_have_nonempty_guideline_citations`
- `test_all_cases_have_valid_fhir_claim_response`

**Step 2:** Run: `pytest tests/test_e2e_clinical_review.py -v --timeout=300`
Expected: ~90%+ pass (AI non-determinism)

**Step 3:** Commit: `test: add E2E tests for all 5 PA cases`

---

## Task 10: Verification & Commit Gate

**Step 1:** Run full verification:
```bash
make lint
make test-data-quality
make test-unit
make test-e2e
```

**Step 2:** Fix any failures

**Step 3:** Manual UAT:
```bash
make review      # Case 1: green APPROVED
make review-all  # All 5 cases with expected determinations
```

**Step 4:** Commit gate:
```bash
git add -A && git commit -m "Step 1: Core clinical review engine with CLI demo"
git tag -a v0.1.0 -m "Step 1: Core clinical review engine — CLI demo-able"
git checkout -b release/step-1-core-engine
git checkout main
```

---

## Verification

After all tasks complete:

| Command | Expected |
|---------|----------|
| `make lint` | Clean (ruff check + format + mypy) |
| `make test-data-quality` | 8 tests pass |
| `make test-unit` | ~25 tests pass |
| `make test-e2e` | ~15 tests pass (needs ANTHROPIC_API_KEY) |
| `make review` | Case 1: APPROVED, confidence >= 80%, mentions conservative treatment |
| `make review-all` | 5 cases: 2 approved, 1 denied, 2 pended |

## User Stories Coverage

| US | Story | Covered By |
|----|-------|-----------|
| US-1.1 | Submit PA → get determination within 60s | E2E: `test_all_cases_return_within_60_seconds` |
| US-1.2 | Evidence-backed reasoning | E2E: `test_all_cases_have_nonempty_guideline_citations` + rationale tests |
| US-1.3 | Ambiguous cases route to review | Unit: `TestConfidenceRouting` (6 tests) |
| US-1.4 | Denials include reasons | E2E: `TestCase02.test_rationale_mentions_cosmetic_or_mismatch` |
| US-1.5 | Missing-info lists what's needed | E2E: `TestCase04.test_missing_documentation_is_nonempty` |

## Test Summary

| Test File | Marker | Count | API Key? |
|-----------|--------|-------|----------|
| `test_data_quality.py` | unit | ~8 | No |
| `test_clinical_review_engine.py` | unit | ~25 | No |
| `test_e2e_clinical_review.py` | e2e | ~15 | Yes |
| **Total** | | **~48** | |
