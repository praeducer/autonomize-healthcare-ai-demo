# Copilot Instructions — Prior Auth Demo

AI-driven prior authorization demo using Claude, FHIR R4, and evidence-based clinical guidelines.

## Package Structure

```
src/prior_auth_demo/          # Main package
├── clinical_review_engine.py # Core AI review logic
├── application_settings.py   # pydantic-settings config
├── healthcare_api_server.py  # FastAPI REST API
├── command_line_demo.py      # CLI entry point
├── determination_audit_store.py # SQLite audit trail
├── mock_healthcare_services/ # Mock payer services
└── web_dashboard/            # Jinja2 + HTMX UI
```

## Python Conventions

- Python 3.12+ with type hints on all signatures
- Pydantic v2 models for all data structures
- `pydantic-settings` for configuration
- `httpx.AsyncClient` for HTTP calls
- `async def` for all FastAPI route handlers

## FHIR R4B Imports

Always use R4B subpackage (root is R5):
```python
from fhir.resources.R4B.claim import Claim
from fhir.resources.R4B.patient import Patient
```

## Testing

- `polyfactory` for test data generation
- `pytest.mark.unit`, `pytest.mark.integration`, `pytest.mark.e2e` markers
- All test data is synthetic — no real PHI

## Naming

- snake_case: functions, variables, modules
- PascalCase: classes, Pydantic models
- UPPER_SNAKE_CASE: constants, env vars
