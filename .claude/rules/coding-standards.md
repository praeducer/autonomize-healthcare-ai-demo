# Coding Standards

## Python

- Python 3.12+ with type hints on ALL function signatures and return types
- Pydantic v2 models for all data structures — never use raw dicts for API I/O
- `pydantic-settings` for all configuration (`application_settings.py`)
- Async FastAPI endpoints (`async def`) for all route handlers
- Use `httpx.AsyncClient` for all HTTP calls
- Import ordering: stdlib → third-party → local (enforced by ruff `I` rule)

## FHIR R4B Imports

Always use `from fhir.resources.R4B.<resource> import <Resource>` — the root package defaults to R5. See `healthcare-standards.md` for the full import list.

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
