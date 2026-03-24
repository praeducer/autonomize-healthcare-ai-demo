# Coding Standards

## Python

- Python 3.12+ with type hints on ALL function signatures and return types
- Pydantic v2 models for all data structures — never use raw dicts for API I/O
- `pydantic-settings` for all configuration (`application_settings.py`)
- Async FastAPI endpoints (`async def`) for all route handlers
- Use `httpx.AsyncClient` for all HTTP calls
- Import ordering: stdlib → third-party → local (enforced by ruff `I` rule)

## FHIR R4B Imports

Always import from the R4B subpackage — the root package defaults to R5:

```python
# Correct — R4B
from fhir.resources.R4B.claim import Claim
from fhir.resources.R4B.claimresponse import ClaimResponse
from fhir.resources.R4B.patient import Patient

# WRONG — this imports R5 models
from fhir.resources.claim import Claim
```

## Configuration

- Use `pydantic-settings` BaseSettings in `application_settings.py`
- All external URLs, credentials, thresholds come from environment variables
- Never hardcode connection strings, model IDs, or thresholds in business logic

## Naming

- Snake_case for functions, variables, modules
- PascalCase for classes and Pydantic models
- UPPER_SNAKE_CASE for constants and environment variable names

## Error Handling

- FastAPI `HTTPException` for API errors with meaningful status codes and detail messages
- Never catch bare `Exception` — catch specific exception types
- Log errors with structured context (request_id, member_id, step name)

## Testing

- Every test function has a clear docstring explaining what it verifies
- Use `pytest.mark.asyncio` for all async tests
- Use `polyfactory` to generate test data from Pydantic/FHIR models
- Mock external services in unit tests; use real services in integration/e2e tests
- No real PHI in test data — all synthetic
- Markers: `@pytest.mark.unit`, `@pytest.mark.integration`, `@pytest.mark.e2e`
