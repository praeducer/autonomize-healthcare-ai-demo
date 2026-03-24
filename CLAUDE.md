# AI-Driven Prior Authorization Demo

## Project Context

Interview exercise for Autonomize AI demonstrating AI-driven prior authorization automation using Claude, FHIR R4, and evidence-based clinical guidelines. This is a **demo-scope prototype** — not the full enterprise architecture.

**Full architecture**: `docs/architecture/solution-architecture.md`
**Implementation spec**: `.claude/plans/demo-implementation-prompt.md`
**Design doc**: `docs/plans/2026-03-24-demo-implementation-design.md`

**Owner**: Paul Prae — Modular Earth LLC (www.paulprae.com)

## Tech Stack

| Layer | Technology | Version |
|-------|-----------|---------|
| Language | Python | 3.12+ |
| AI Provider | Anthropic SDK (direct) | Latest |
| LLM | Claude Sonnet 4.6 | claude-sonnet-4-6-20260320 |
| FHIR Models | `fhir.resources` R4B | 8.2.0 |
| API Framework | FastAPI | Latest |
| FHIR Server | HAPI FHIR (Docker) | Latest |
| Clinical Data | Synthea FHIR R4 | 10-patient bulk |
| PA Data Model | Da Vinci PAS IG | STU 2.0.1 |
| Test Fixtures | `polyfactory` | Latest |
| Web UI | Jinja2 + HTMX + Pico CSS | Latest (CDN) |
| Audit Store | SQLite | Built-in |
| Config | `pydantic-settings` | Latest |

## Build & Run

```bash
make install           # Install deps + pre-commit hooks
make review            # Run single PA review (CLI)
make review-all        # Run all 5 PA cases
make dev               # Start FastAPI dev server
make test              # Run all tests
make lint              # Ruff check + format check + mypy
make download-synthea  # Download Synthea FHIR patients
```

## Project Structure

```
src/prior_auth_demo/
├── __init__.py
├── clinical_review_engine.py         # Core AI: Claude + tool use → determination
├── command_line_demo.py              # CLI entry point (argparse)
├── healthcare_api_server.py          # FastAPI REST API
├── application_settings.py           # Pydantic Settings (env vars)
├── determination_audit_store.py      # SQLite audit trail
├── mock_healthcare_services/
│   ├── __init__.py
│   └── member_eligibility.py         # Mock: FHIR CoverageEligibilityResponse
└── web_dashboard/
    ├── __init__.py
    ├── dashboard_routes.py           # FastAPI Jinja2 template routes
    └── templates/
        └── review_dashboard.html     # HTMX + Pico CSS
```

## Implementation Phases

| Phase | Deliverable | Tag |
|-------|------------|-----|
| 0 | Repo prep (this state) | v0.0.1 |
| 1 | CLI review engine + 5 PA cases | v0.1.0 |
| 2 | FastAPI + HAPI FHIR + audit store | v0.2.0 |
| 3 | Web dashboard (Jinja2 + HTMX) | v0.3.0 |
| 4 | Docker + Azure deployment | v0.4.0 |
| 5 | Azure-native services | v0.5.0 |

## Coding Standards

- Python 3.12 with type hints on all function signatures
- Pydantic v2 models for all data structures
- `pydantic-settings` for configuration (`application_settings.py`)
- Async FastAPI endpoints
- Ruff for linting and formatting (`ruff check`, `ruff format`)
- Module docstrings on every file explaining purpose
- No commented-out code — delete or implement
- FHIR R4B imports: `from fhir.resources.R4B.<resource> import <Resource>` (NOT root package, which is R5)

## Testing

```bash
make test              # Run all tests
pytest tests/ -v       # Verbose output
pytest -m unit         # Unit tests only
pytest -m integration  # Integration tests (require Docker)
pytest -m e2e          # End-to-end tests (require API key)
```

- `polyfactory` for generating test data from Pydantic/FHIR models
- All test data is synthetic — no real PHI
- Every test function has a docstring explaining what it verifies

## MCP Tools Available

- **cms-coverage-db**: CMS Coverage Database — LCD/NCD lookups for coverage determinations
- **npi-registry**: NPI Registry — provider validation, specialty, practice info
- **docker-mcp**: Docker management for HAPI FHIR server

## Demo Scope

This demo proves the enterprise architecture is implementable. It does NOT include:
- Fax ingestion / OCR
- X12 278 EDI processing
- Legacy database connectors
- Multi-LOB configuration
- Production security hardening
