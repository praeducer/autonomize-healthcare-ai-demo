# UAT Log — AI-Driven Prior Authorization Demo

> **Owner**: Paul Prae | **Last Updated**: 2026-03-24
> **Scope**: Build Steps 1-3 (local demo — CLI, API, Dashboard)
> **Prerequisites**: `make install`, `.env` file with `ANTHROPIC_API_KEY`

This document tracks manual user acceptance testing for each build step. Check off items as you complete them. Automated tests supplement but do not replace this UAT — these exercises verify the demo experience, not just code correctness.

---

## Build Step 1: Core CLI Engine (v0.1.0) ✅ Implemented

**What to test**: CLI tool reviews 5 PA cases via Claude with tool use. Color-coded output.
**Prerequisites**: `ANTHROPIC_API_KEY` in `.env`

| # | Test | Command / Action | Expected Result | Pass? |
|---|------|-----------------|-----------------|-------|
| 1.1 | Single case review | `make review` | Case 1: green APPROVED badge, confidence >= 80%, mentions "conservative treatment" or "radiculopathy", completes < 60s | |
| 1.2 | All cases review | `make review-all` | 5 cases: approvals (1,5), denial (2), pended (3,4). Summary table at end. | |
| 1.3 | Denial rationale | Read Case 2 output | Mentions "cosmetic" AND "diagnosis mismatch" or "no functional indication" | |
| 1.4 | Complex pend rationale | Read Case 3 output | PENDED_FOR_REVIEW (not DENIED). Mentions PT gap, no ESI, BMI, or A1C. | |
| 1.5 | Missing info specificity | Read Case 4 output | missing_documentation lists 2+ specific items (methotrexate dose, labs, DAS28) | |
| 1.6 | Urgent oncology | Read Case 5 output | APPROVED with confidence >= 80%. Mentions NCCN, PD-L1, or oncology. Notes urgency. | |
| 1.7 | FHIR data integrity | Open `data/sample_pa_cases/01_lumbar_mri_clear_approval.json` | Valid JSON, `use: "preauthorization"`, ICD-10 codes visible | |
| 1.8 | Timing | Observe each case during `make review-all` | Each case completes in < 60 seconds | |
| 1.9 | CLI still works after Step 2/3 | `make review` (after Step 2/3 implemented) | Same behavior as 1.1 — CLI is independent of API/dashboard | |

### Step 1 Notes
- LLM outputs are non-deterministic. If a case gives unexpected results, re-run once. Consistent wrong results = bug.
- The CLI always works standalone — it does not depend on Docker, FHIR server, or the API.

---

## Build Step 2: REST API + FHIR Server (v0.2.0) 🔲 Not Yet Implemented

**What to test**: FastAPI REST API, HAPI FHIR server with Synthea data, SQLite audit trail, Swagger UI.
**Prerequisites**: `make up && make load-fhir-data`, `make dev` running

| # | Test | Command / Action | Expected Result | Pass? |
|---|------|-----------------|-----------------|-------|
| 2.1 | HAPI FHIR server | Open `http://localhost:8080` | HAPI FHIR welcome page | |
| 2.2 | Synthea patients loaded | Click "Patient" in HAPI FHIR UI | Synthea patients visible (synthetic names) | |
| 2.3 | Swagger UI | Open `http://localhost:8000/docs` | Swagger UI with all endpoints documented | |
| 2.4 | Sample cases endpoint | GET `/api/v1/prior-auth/sample-cases` | JSON list of 5 case filenames | |
| 2.5 | Health check | GET `/health` | `{"status": "healthy", "fhir_server": "connected", "version": "0.2.0"}` | |
| 2.6 | Submit PA review via API | POST `/api/v1/prior-auth/review` with Case 1 | APPROVED within 60s with confidence, rationale, citations | |
| 2.7 | Retrieve determination | GET `/api/v1/prior-auth/determinations` | List containing case from 2.6 | |
| 2.8 | Complex case via API | POST Case 3 (spinal fusion) | PENDED_FOR_REVIEW, mentions clinical gaps | |
| 2.9 | Audit trail persistence | `sqlite3 data/audit_trail.db "SELECT determination, confidence_score FROM determinations;"` | Both determinations from 2.6 and 2.8 visible | |
| 2.10 | Invalid input handling | POST malformed JSON to review endpoint | 422 with meaningful error message | |
| 2.11 | CLI still works | `make review` (with Docker services running) | Same CLI output as Step 1 — completely independent | |
| 2.12 | CLI works WITHOUT Docker | `make down` then `make review` | CLI still works — does not depend on FHIR server | |

### Step 2 Notes
- The API and CLI are independent entry points to the same engine. Both must work at all times.
- The audit store is append-only. There are no update or delete operations by design.
- FHIR server data is synthetic (Synthea). No real PHI.

---

## Build Step 3: Web Dashboard (v0.3.0) 🔲 Not Yet Implemented

**What to test**: Jinja2 + HTMX + Pico CSS dashboard at localhost:8000, presentation readiness.
**Prerequisites**: `make up && make load-fhir-data`, `make dev` running

| # | Test | Command / Action | Expected Result | Pass? |
|---|------|-----------------|-----------------|-------|
| 3.1 | Dashboard loads | Open `http://localhost:8000` | Dashboard with case selector, no console errors | |
| 3.2 | Submit clear approval | Select "Lumbar MRI" → Submit | Loading spinner → green APPROVED, confidence >= 80%, rationale, citations | |
| 3.3 | Rationale quality | Read Case 1 result | Professional, clinical language. Mentions "conservative treatment failure" or "radiculopathy". | |
| 3.4 | Missing info case | Submit Case 4 (Humira) | Yellow PENDED. Missing docs list: methotrexate dose, labs, DAS28. | |
| 3.5 | Complex pend case | Submit Case 3 (Spinal Fusion) | Yellow PENDED_FOR_REVIEW. Identifies specific clinical gaps. | |
| 3.6 | Urgent oncology | Submit Case 5 (Keytruda) | Green APPROVED. Mentions NCCN, PD-L1, or urgency. | |
| 3.7 | Denial case | Submit Case 2 (Rhinoplasty) | Red DENIED. Mentions "cosmetic", "diagnosis mismatch". | |
| 3.8 | History panel | After submitting all 5 cases | All 5 determinations listed with case name, determination, confidence, timestamp. | |
| 3.9 | Projector readability | Fullscreen browser at 1920x1080 | All text readable, badges visible, no horizontal scrolling. | |
| 3.10 | Swagger still works | Open `http://localhost:8000/docs` | Swagger UI intact alongside dashboard. | |
| 3.11 | API still works | GET `/api/v1/prior-auth/sample-cases` | JSON response (not HTML). API endpoints unaffected by dashboard. | |
| 3.12 | CLI still works | `make review` in a terminal | Same CLI output — completely independent of dashboard. | |
| 3.13 | Demo walkthrough | Submit all 5 cases in order: 1→4→3→5→2 | Full demo completes in 5-6 minutes. Professional, interview-ready. | |

### Step 3 Notes
- This is the interview demo surface. Rehearse the full walkthrough (3.13) at least twice.
- LLM outputs vary — if a case gives unexpected results during demo, re-submit once. That's normal.
- The recommended demo order (1→4→3→5→2) tells a clinical story: clear approval → missing docs → ambiguous → urgent approval → denial.
- All three entry points (CLI, API/Swagger, Dashboard) must work simultaneously.

---

## Cross-Step Regression Tests

These verify that new functionality doesn't break previous steps.

| # | Test | After Step | Command / Action | Expected Result | Pass? |
|---|------|-----------|-----------------|-----------------|-------|
| R.1 | CLI after API | 2 | `make review-all` | Same results as Step 1 | |
| R.2 | CLI without Docker | 2 | `make down && make review` | CLI works without FHIR server | |
| R.3 | CLI after Dashboard | 3 | `make review-all` | Same results as Step 1 | |
| R.4 | Swagger after Dashboard | 3 | Open `/docs` | Swagger UI renders correctly | |
| R.5 | API after Dashboard | 3 | POST to `/api/v1/prior-auth/review` | API returns JSON (not HTML) | |
| R.6 | Unit tests | All | `make test-unit` | All unit tests pass | |
| R.7 | Data quality | All | `make test-data-quality` | All data quality tests pass | |

---

## Test Results Summary

| Step | Automated Tests | UAT Items | Status |
|------|----------------|-----------|--------|
| Step 1 (CLI) | 60 (35 unit + 25 e2e) | 9 items | 🔲 Pending UAT |
| Step 2 (API) | TBD | 12 items | 🔲 Not Implemented |
| Step 3 (Dashboard) | TBD | 13 items | 🔲 Not Implemented |
| Regression | 7 items | 7 items | 🔲 Pending |
