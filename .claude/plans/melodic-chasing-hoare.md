# Build Step 3: Web Dashboard — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add an interview-ready web dashboard at `localhost:8000` using Jinja2 + HTMX + Pico CSS — no npm, no build step.

**Architecture:** Dashboard routes return HTML (not JSON). `POST /dashboard/review` calls the engine, renders an HTML result fragment, and returns it via HTMX swap. The existing JSON API (`/api/v1/...`) and Swagger (`/docs`) are untouched. CLI continues to work independently.

**Tech Stack:** Jinja2 templates, HTMX (CDN), Pico CSS (CDN), FastAPI HTMLResponse

---

## Context

Step 2 (v0.2.0) delivered the REST API with Swagger, FHIR server, and audit trail. Step 3 adds the interview demo surface — a single-page dashboard where Paul can submit PA cases and show results on a projector. This is the final pre-cloud step.

**Critical constraints:**
- Dashboard routes are ADDITIVE — `/api/v1/*`, `/docs`, `/health`, and CLI all keep working
- No npm, no JS build step — HTMX and Pico CSS via CDN
- All dynamic content Jinja2-escaped (no XSS)
- Readable at 1920x1080 on a projector

**Dependencies already installed:** `jinja2`, `python-multipart` (in pyproject.toml since Step 0)

---

## Files to Create

| File | Purpose |
|------|---------|
| `src/prior_auth_demo/web_dashboard/templates/review_dashboard.html` | Main dashboard page |
| `src/prior_auth_demo/web_dashboard/templates/fragments/result_card.html` | HTMX result fragment |
| `src/prior_auth_demo/web_dashboard/templates/fragments/history_row.html` | HTMX history fragment |
| `src/prior_auth_demo/web_dashboard/dashboard_routes.py` | Dashboard FastAPI router |
| `tests/test_web_dashboard.py` | Dashboard tests |

## Files to Modify

| File | Change |
|------|--------|
| `src/prior_auth_demo/healthcare_api_server.py` | Mount dashboard router, configure Jinja2, update version to 0.3.0 |

## Key Design Decisions

1. **Dashboard routes return HTML, API routes return JSON.** HTMX expects HTML fragments. The dashboard has its own `POST /dashboard/review` endpoint that calls the engine and returns a rendered HTML fragment. The JSON API is untouched.
2. **Three template files:** One full page (`review_dashboard.html`), two fragments (`result_card.html` for review results, `history_row.html` for history table rows). Fragments are what HTMX swaps in.
3. **No inline JavaScript.** HTMX attributes handle all interactivity. Pico CSS handles all styling. Zero custom JS.
4. **Case selector uses descriptive names** not filenames. Map: "Lumbar MRI — Clear Approval" → `01_lumbar_mri_clear_approval.json`.
5. **Demo order in dropdown:** 1→4→3→5→2 (clear approval → missing docs → ambiguous → urgent → denial). Tells a clinical story.

---

## Task 1: Dashboard Routes

**Files:**
- Create: `src/prior_auth_demo/web_dashboard/dashboard_routes.py`
- Create: `tests/test_web_dashboard.py`

**Step 1:** Write tests (`@pytest.mark.unit`). Use `httpx.ASGITransport`:
- `test_dashboard_root_returns_200_html` — GET `/` → 200 with `text/html` content type
- `test_dashboard_contains_case_selector` — HTML contains all 5 case names
- `test_dashboard_contains_htmx_attributes` — HTML contains `hx-post`, `hx-target`
- `test_swagger_still_accessible` — GET `/docs` → 200
- `test_api_health_still_works` — GET `/health` → 200 with JSON
- `test_api_sample_cases_still_works` — GET `/api/v1/prior-auth/sample-cases` → 200 with JSON list

**Step 2:** Run tests — FAIL

**Step 3:** Implement `dashboard_routes.py`:
- FastAPI `APIRouter` with `tags=["Dashboard"]`
- `GET /` → renders `review_dashboard.html` with case list context
- `POST /dashboard/review` → accepts form data (case_name), loads bundle, calls `review_prior_auth_request()`, stores in audit, renders `result_card.html` fragment
- `GET /dashboard/history` → queries audit store, renders `history_row.html` fragments for each determination

**Step 4:** Mount on API server — modify `healthcare_api_server.py`:
- Add `from fastapi.templating import Jinja2Templates`
- Add `from starlette.staticfiles import StaticFiles` (if needed)
- Configure Jinja2 template directory
- Include dashboard router
- Update version to `0.3.0`

**Step 5:** Run tests — PASS

**Step 6:** Commit: `feat: add dashboard routes with HTMX endpoints`

---

## Task 2: Dashboard HTML Template

**Files:**
- Create: `src/prior_auth_demo/web_dashboard/templates/review_dashboard.html`
- Create: `src/prior_auth_demo/web_dashboard/templates/fragments/result_card.html`
- Create: `src/prior_auth_demo/web_dashboard/templates/fragments/history_row.html`

**Step 1:** Create main template (`review_dashboard.html`):

Layout (single page, Pico CSS semantic HTML):
- `<header>`: "Prior Authorization Review — AI-Driven Clinical Decision Support"
- `<main>` with two-column grid:
  - **Left column**: Case selector form
    - `<select>` with 5 cases (descriptive names, values = filenames)
    - "Submit for Review" button
    - `hx-post="/dashboard/review"` with `hx-target="#result-panel"` `hx-swap="innerHTML"`
    - `hx-indicator="#spinner"` for loading state
  - **Right column**: `<div id="result-panel">` (empty initially, filled by HTMX)
- `<section>`: History table
  - `hx-get="/dashboard/history"` with `hx-trigger="load, every 15s"` `hx-target="#history-body"`
  - Table headers: Case, Determination, Confidence, Time, Date
- `<footer>`: "Phase 0 Demo | Autonomize AI"
- CDN links: Pico CSS, HTMX (pinned versions)

**Step 2:** Create result fragment (`fragments/result_card.html`):
- Determination badge: `<mark>` with data attribute for color (green/red/yellow)
- Confidence: `<progress>` element with percentage label
- Clinical rationale: `<blockquote>`
- Guideline citations: `<ul>`
- Missing documentation (if pended): highlighted `<ul>`
- Processing time: small text

**Step 3:** Create history fragment (`fragments/history_row.html`):
- One `<tr>` per determination
- Columns: case_name, determination (with color), confidence %, processing time, timestamp

**Step 4:** Verify dashboard renders: `make dev` → open `http://localhost:8000`

**Step 5:** Commit: `feat: add dashboard HTML with HTMX and Pico CSS`

---

## Task 3: Presentation Polish

**Files:**
- Modify: templates as needed

**Step 1:** Style adjustments for projector readability:
- Minimum font size 16px for body text
- Large determination badges (24px+ bold)
- High contrast colors: green `#2ecc40`, red `#e74c3c`, yellow/amber `#f39c12`
- Confidence bar uses Pico `<progress>` with color matching determination
- Max-width container (1200px) centered
- No horizontal scroll at 1920x1080

**Step 2:** Demo flow order in dropdown: Cases appear as:
1. "1 — Lumbar MRI (Clear Approval)"
2. "4 — Humira (Missing Documentation)"
3. "3 — Spinal Fusion (Complex Review)"
4. "5 — Keytruda (Urgent Oncology)"
5. "2 — Rhinoplasty (Cosmetic Denial)"

**Step 3:** Add loading spinner (HTMX `hx-indicator` with Pico CSS `aria-busy`)

**Step 4:** Commit: `feat: polish dashboard for projector presentation`

---

## Task 4: Verification & Commit Gate

**Step 1:** Run full verification:
```bash
ruff check src/ tests/ && mypy src/prior_auth_demo/
pytest tests/ -m unit -v
make review          # CLI still works
```

**Step 2:** Manual check: `make dev` → open `http://localhost:8000`:
- Dashboard loads with case selector
- Swagger at `/docs` still works
- API at `/api/v1/prior-auth/sample-cases` still returns JSON

**Step 3:** Update `pyproject.toml` version to `0.3.0`

**Step 4:** Commit gate:
```bash
git tag -a v0.3.0 -m "Step 3: Web dashboard — interview-ready local demo"
git checkout -b release/step-3-web-dashboard
git checkout main
git push origin main --tags
git push origin release/step-3-web-dashboard
```

---

## Verification

| Command | Expected |
|---------|----------|
| `make lint` | Clean |
| `make test-unit` | All pass (49 existing + ~6 new dashboard tests) |
| `make review` | CLI works exactly as Steps 1-2 |
| `http://localhost:8000` | Dashboard with case selector |
| `http://localhost:8000/docs` | Swagger UI still works |
| `GET /health` | JSON with status, version 0.3.0, fhir_server |
| `GET /api/v1/prior-auth/sample-cases` | JSON list (not HTML) |

## Regression Checks

| Check | Why |
|-------|-----|
| `make review` works without Docker | CLI independence |
| `/docs` renders Swagger UI | API not shadowed by dashboard |
| `/api/v1/...` returns JSON | API not converted to HTML |
| All Step 1+2 tests pass | No breaking changes |

## Execution Batches

| Batch | Tasks |
|-------|-------|
| 1 | Task 1 (routes + tests) + Task 2 (templates) — can be parallel |
| 2 | Task 3 (polish) |
| 3 | Task 4 (verification + commit gate) |
