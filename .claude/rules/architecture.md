# Architecture Rules

## Service Boundaries

| File | Responsibility |
|------|---------------|
| `clinical_review_engine.py` | Core AI: receives PA request, orchestrates Claude tool use, returns determination |
| `command_line_demo.py` | CLI entry point: loads PA cases from JSON, calls engine, prints results |
| `healthcare_api_server.py` | FastAPI REST API: receives FHIR Claims, calls engine, returns ClaimResponses |
| `application_settings.py` | Pydantic Settings: all config from environment variables |
| `determination_audit_store.py` | SQLite: append-only audit trail of every determination |
| `mock_healthcare_services/member_eligibility.py` | Mock: returns FHIR CoverageEligibilityResponse |
| `web_dashboard/dashboard_routes.py` | Jinja2 template routes for the review dashboard |

## Phased Architecture

The demo builds progressively — each phase is independently demo-able:
1. **Phase 1 (CLI):** `command_line_demo.py` → `clinical_review_engine.py` → Claude
2. **Phase 2 (API):** `healthcare_api_server.py` → engine + HAPI FHIR + audit store
3. **Phase 3 (Dashboard):** `web_dashboard/` → API → engine

## Data Flow

```
PA Request (FHIR Claim) → Clinical Review Engine → Claude (with tool use)
  ├── Tool: Retrieve patient clinical history (HAPI FHIR)
  ├── Tool: Check member eligibility (mock service)
  ├── Tool: Look up coverage criteria (CMS Coverage DB via MCP)
  ├── Tool: Validate provider NPI (NPI Registry via MCP)
  └── Tool: Validate ICD-10 codes (local CDC data)
→ ClinicalReviewResult (determination + rationale + evidence)
→ Audit Store (append-only SQLite)
→ FHIR ClaimResponse
```

## Configuration

- All external URLs, credentials, and thresholds come from environment variables
- Use `src/prior_auth_demo/application_settings.py` with `pydantic-settings` as the single source of truth
- Never hardcode connection strings, model IDs, or thresholds in business logic

## Data Model

- PA Request = FHIR `Claim` with `use: "preauthorization"` (Da Vinci PAS)
- PA Response = FHIR `ClaimResponse` with determination, reasoning, evidence
- Use `fhir.resources.R4B` Pydantic models directly — do not invent custom models for FHIR domain objects
- Application-specific models (e.g., `ClinicalReviewResult`) wrap FHIR models with demo-specific fields

## Audit Trail

- SQLite database (`determination_audit_store.py`)
- Append-only: never update, never delete
- Every determination records: request, response, confidence, rationale, citations, timestamps
