# Build Step 2: REST API + FHIR Server + Audit Trail — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add a FastAPI REST API with Swagger docs, HAPI FHIR server (Docker) with Synthea patients, SQLite audit trail, and mock eligibility service — all while preserving CLI independence.

**Architecture:** The API is a thin wrapper around the existing engine. Three independent components (audit store, eligibility mock, FHIR loader) can be built in parallel. The engine gains optional FHIR server enrichment that falls back gracefully.

**Tech Stack:** FastAPI, uvicorn, httpx (async FHIR client), aiosqlite, HAPI FHIR (Docker), Synthea NDJSON data

---

## Context

Step 1 (v0.1.0) delivered a working CLI engine with 60 tests. Step 2 wraps it in a REST API and adds real FHIR data, an audit trail, and a mock eligibility service. The API is demo-able via Swagger UI at `localhost:8000/docs`.

**Critical constraint:** The CLI (`make review`, `make review-all`) must continue to work exactly as before — with or without Docker running. The engine is the shared core; the API and CLI are independent entry points.

---

## Files to Create

| File | Purpose |
|------|---------|
| `docker-compose.yml` | HAPI FHIR server container |
| `src/prior_auth_demo/mock_healthcare_services/load_fhir_data.py` | Load Synthea NDJSON into HAPI FHIR |
| `src/prior_auth_demo/determination_audit_store.py` | SQLite append-only audit trail |
| `src/prior_auth_demo/mock_healthcare_services/member_eligibility.py` | Mock eligibility FastAPI router |
| `src/prior_auth_demo/healthcare_api_server.py` | FastAPI REST API |
| `tests/test_determination_audit_store.py` | Audit store unit tests |
| `tests/test_healthcare_api_server.py` | API tests (unit + integration) |
| `tests/test_fhir_server_integration.py` | FHIR server integration tests |
| `tests/test_e2e_api_review.py` | Full API flow E2E tests |

## Files to Modify

| File | Change |
|------|--------|
| `src/prior_auth_demo/clinical_review_engine.py` | Add `retrieve_fhir_clinical_data()` — optional FHIR server enrichment with graceful fallback |

## Existing Files to Reuse (DO NOT MODIFY unless specified)

| File | Reuse |
|------|-------|
| `clinical_review_engine.py` | `review_prior_auth_request()`, `ClinicalReviewResult` — API calls these directly |
| `application_settings.py` | `fhir_server_url` field already exists |
| `data/synthea_fhir_patients/raw/*.ndjson` | 13 patients, already downloaded |
| `pyproject.toml` | Dependencies already include fastapi, uvicorn, httpx, aiosqlite |
| `Makefile` | `up`, `down`, `dev`, `load-fhir-data` targets already defined |

---

## Key Design Decisions

1. **Audit store is a class** (`DeterminationAuditStore`) with `init_db()`, `store_determination()`, `get_determination()`, `list_determinations()`. No update/delete methods exist.
2. **FastAPI lifespan** initializes settings and audit store. Module-level state avoids circular imports.
3. **Health endpoint** checks FHIR server connectivity via `GET /fhir/metadata` with a 5s timeout. Returns `"unavailable"` if Docker isn't running — not an error.
4. **API tests use `httpx.ASGITransport`** — no server startup needed for unit/integration tests.
5. **FHIR enrichment is opt-in**: New `retrieve_fhir_clinical_data(patient_id, fhir_server_url)` function tries FHIR server, returns empty dict on failure. Engine merges with bundle data.
6. **Eligibility mock** is a FastAPI router mounted at `/mock/eligibility`. Returns FHIR `CoverageEligibilityResponse`. All 5 demo members are eligible.
7. **FHIR data loader** reads NDJSON, POSTs to HAPI FHIR in dependency order (Organization → Patient → everything else).

---

## Task 1: Docker Compose + FHIR Data Loader

**Files:**
- Create: `docker-compose.yml`
- Create: `src/prior_auth_demo/mock_healthcare_services/load_fhir_data.py`

**Step 1:** Create `docker-compose.yml` with HAPI FHIR service (port 8080, JSON encoding).

**Step 2:** Verify: `docker compose up -d && curl http://localhost:8080/fhir/metadata | head -5`

**Step 3:** Create `load_fhir_data.py` — async script that reads `data/synthea_fhir_patients/raw/*.ndjson`, skips `log.ndjson`, POSTs each resource to HAPI FHIR. Uses `httpx.AsyncClient`. Loads in dependency order. Reports counts.

**Step 4:** Verify: `python -m prior_auth_demo.mock_healthcare_services.load_fhir_data` loads resources. `curl http://localhost:8080/fhir/Patient?_summary=count` shows count.

**Step 5:** Commit: `feat: add docker-compose and FHIR data loader`

---

## Task 2: Audit Store

**Files:**
- Create: `src/prior_auth_demo/determination_audit_store.py`
- Create: `tests/test_determination_audit_store.py`

**Step 1:** Write tests (`@pytest.mark.unit`, all use `tmp_path` for temp SQLite):
- `test_init_creates_database_file` — init_db creates file + table
- `test_store_and_retrieve_by_id` — store returns UUID, get returns matching record
- `test_list_returns_stored_results` — list_determinations returns all stored, newest first
- `test_list_supports_pagination` — limit and offset work correctly
- `test_no_update_or_delete_methods` — class has no update/delete attrs (append-only guarantee)

**Step 2:** Run tests — all FAIL (module doesn't exist)

**Step 3:** Implement `DeterminationAuditStore` class:
- `__init__(db_path)` — defaults to `data/audit_trail.db`
- `init_db()` — creates table with: id (TEXT PK), created_at, case_name, determination, confidence_score, clinical_rationale, guideline_citations (JSON string), processing_time_seconds, full_request_json, full_response_json
- `store_determination(...)` — INSERT, returns UUID
- `get_determination(id)` — SELECT by id, returns dict
- `list_determinations(limit, offset)` — SELECT ORDER BY created_at DESC
- `close()` — close connection
- NO update or delete methods

**Step 4:** Run tests — all PASS

**Step 5:** Verify existing tests still pass: `pytest tests/ -m unit -q --tb=no`

**Step 6:** Commit: `feat: add SQLite audit store (append-only)`

---

## Task 3: Mock Eligibility Service

**Files:**
- Create: `src/prior_auth_demo/mock_healthcare_services/member_eligibility.py`

**Step 1:** Implement FastAPI router:
- `POST /check` — accepts `{"member_id": str}`, returns FHIR CoverageEligibilityResponse
- All 5 demo member IDs (MBR-2026-001 through MBR-2026-005) return eligible
- Unknown members return eligible with generic PPO (demo always approves eligibility)
- ~30-40 lines. Keep minimal.

**Step 2:** Commit: `feat: add mock member eligibility service`

---

## Task 4: FastAPI Server

**Files:**
- Create: `src/prior_auth_demo/healthcare_api_server.py`
- Create: `tests/test_healthcare_api_server.py`

**Step 1:** Write tests (`tests/test_healthcare_api_server.py`). Use `httpx.ASGITransport(app=app)` for in-process testing:

Unit tests (no Docker needed):
- `test_health_returns_200` — GET /health → 200 with status, version, fhir_server fields
- `test_sample_cases_returns_5` — GET /api/v1/prior-auth/sample-cases → 5 filenames
- `test_sample_case_returns_valid_json` — GET /api/v1/prior-auth/sample-cases/01_lumbar_mri_clear_approval.json → valid FHIR Bundle JSON
- `test_sample_case_not_found_returns_404` — GET /api/v1/prior-auth/sample-cases/nonexistent.json → 404
- `test_invalid_review_input_returns_422` — POST /api/v1/prior-auth/review with `{"bad": "data"}` → 422
- `test_swagger_docs_accessible` — GET /docs → 200

**Step 2:** Run tests — FAIL (module doesn't exist)

**Step 3:** Implement `healthcare_api_server.py`:
- FastAPI app with lifespan (init settings + audit store)
- `GET /health` — checks FHIR server connectivity, returns status/version
- `GET /api/v1/prior-auth/sample-cases` — lists JSON files from `data/sample_pa_cases/`
- `GET /api/v1/prior-auth/sample-cases/{name}` — returns case JSON
- `POST /api/v1/prior-auth/review` — accepts FHIR Bundle JSON, calls `review_prior_auth_request()`, stores in audit, returns result
- `GET /api/v1/prior-auth/determinations` — lists from audit store
- `GET /api/v1/prior-auth/determinations/{id}` — gets single determination
- Include eligibility router: `app.include_router(eligibility_router, prefix="/mock/eligibility")`

**Step 4:** Run tests — PASS

**Step 5:** Verify CLI still works: `make review` (should work identically to Step 1)

**Step 6:** Commit: `feat: add FastAPI REST API with Swagger docs`

---

## Task 5: Engine FHIR Server Enrichment

**Files:**
- Modify: `src/prior_auth_demo/clinical_review_engine.py`

**Step 1:** Add unit test to `tests/test_clinical_review_engine.py`:
- `test_retrieve_fhir_clinical_data_returns_empty_on_connection_error` — calling with unreachable URL returns empty dict (graceful fallback)

**Step 2:** Run test — FAIL

**Step 3:** Add `retrieve_fhir_clinical_data(patient_id, fhir_server_url)` function:
- Uses `httpx.AsyncClient` to GET Conditions, Observations, Procedures for patient
- Returns dict with `fhir_conditions`, `fhir_observations`, `fhir_procedures` lists
- On ANY httpx error → returns empty dict (graceful fallback)
- Update `_dispatch_tool()` to merge FHIR server data into `retrieve_clinical_data` response when available

**Step 4:** Run ALL tests — PASS (existing 60 + new ones). CLI still works.

**Step 5:** Commit: `feat: add optional FHIR server clinical data enrichment`

---

## Task 6: FHIR Server Integration Tests

**Files:**
- Create: `tests/test_fhir_server_integration.py`

All tests `@pytest.mark.integration` — skip if FHIR server not reachable.

**Step 1:** Write tests:
- `test_fhir_server_is_reachable` — GET /fhir/metadata returns 200
- `test_synthea_patients_loaded` — GET /fhir/Patient returns count > 0
- `test_fhir_conditions_queryable` — GET /fhir/Condition returns entries
- `test_fhir_observations_queryable` — GET /fhir/Observation returns entries

**Step 2:** Run with Docker: `make up && make load-fhir-data && pytest tests/test_fhir_server_integration.py -v`

**Step 3:** Commit: `test: add FHIR server integration tests`

---

## Task 7: E2E API Tests

**Files:**
- Create: `tests/test_e2e_api_review.py`

All tests `@pytest.mark.e2e` — skip if no API key or FHIR server.

**Step 1:** Write tests:
- `test_full_review_flow_via_api` — POST case 1 → APPROVED → GET determinations → verify stored
- `test_all_5_cases_via_api` — POST all 5 cases, verify expected determinations
- `test_audit_trail_contains_all_reviewed_cases` — after reviewing cases, all appear in GET /determinations

**Step 2:** Run: `pytest tests/test_e2e_api_review.py -v --timeout=300`

**Step 3:** Commit: `test: add E2E API review flow tests`

---

## Task 8: Verification & Commit Gate

**Step 1:** Run full verification:
```bash
ruff check src/ tests/ && mypy src/prior_auth_demo/
pytest tests/ -m unit -v
make up && make load-fhir-data
pytest tests/ -m integration -v
pytest tests/ -m e2e -v --timeout=300
make review          # CLI still works
make review-all      # CLI still works
```

**Step 2:** Update `pyproject.toml` version to `0.2.0`

**Step 3:** Commit gate:
```bash
git tag -a v0.2.0 -m "Step 2: REST API — demo-able via Swagger UI"
git checkout -b release/step-2-api-service
git checkout main
```

---

## Verification

| Command | Expected |
|---------|----------|
| `make lint` | Clean |
| `make test-unit` | All pass (Step 1 + audit store + API unit tests) |
| `make test-integration` | All pass (FHIR server + API endpoints) |
| `make test-e2e` | All pass (CLI E2E + API E2E) |
| `make review` | CLI works exactly as Step 1 |
| `make review-all` | CLI works exactly as Step 1 |
| `http://localhost:8000/docs` | Swagger UI with all endpoints |
| `http://localhost:8080` | HAPI FHIR welcome page |

## Regression Checks

| Check | Why |
|-------|-----|
| `make review` works without Docker | CLI independence |
| `make down && make review` | Engine falls back to bundle data |
| All 60 Step 1 tests still pass | No breaking changes |
| `/get-pa-cases` skill still works | Skills unaffected |

## Execution Batches

| Batch | Tasks | Parallelizable? |
|-------|-------|----------------|
| 1 | Tasks 1-3 (infra, audit, eligibility) | Yes — all independent |
| 2 | Task 4 (API server) | Sequential — depends on 2, 3 |
| 3 | Task 5 (engine enrichment) | Sequential — depends on 1 |
| 4 | Tasks 6-7 (integration + E2E tests) | Yes — independent test files |
| 5 | Task 8 (verification + commit gate) | Sequential |
