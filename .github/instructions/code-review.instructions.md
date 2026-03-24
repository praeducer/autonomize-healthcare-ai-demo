---
applyTo: "**/*"
---

# Code Review Rules — Prior Auth Demo

## Required

- Type hints on all function signatures and return types
- No bare `except` — catch specific exception types
- No hardcoded secrets, API keys, or connection strings
- FHIR R4B models (`fhir.resources.R4B.*`), not raw dicts for clinical data
- Audit trail is append-only — no updates, no deletes
- No real PHI — all test data must be synthetic
- Configuration through `application_settings.py` (pydantic-settings), not raw `os.environ`

## Style

- Module docstrings on every file
- Docstrings on all public functions
- Import ordering: stdlib, third-party, local
- snake_case functions, PascalCase classes, UPPER_SNAKE_CASE constants
