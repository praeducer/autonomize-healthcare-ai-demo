# Coding Standards

## Python

- Python 3.12+ with type hints on ALL function signatures and return types
- Pydantic v2 models for all data structures — never use raw dicts for API I/O
- Async FastAPI endpoints (`async def`) for all route handlers
- Use `httpx.AsyncClient` for all HTTP calls (to mock services, Bedrock, etc.)
- Import ordering: stdlib → third-party → local (enforced by ruff `I` rule)

## Naming

- Snake_case for functions, variables, modules
- PascalCase for classes and Pydantic models
- UPPER_SNAKE_CASE for constants and environment variable names
- Prefix mock service endpoints with the service name (e.g., `facets_router`, `fhir_router`)

## Error Handling

- FastAPI `HTTPException` for API errors with meaningful status codes and detail messages
- Never catch bare `Exception` — catch specific exception types
- Log errors with structured context (request_id, member_id, step name)

## Database

- Parameterized queries only — never string-format SQL
- All timestamps in UTC
- Use `uuid4` for primary keys on PA requests and determinations

## Kafka

- JSON serialization for all messages
- Include `request_id`, `timestamp`, and `event_type` in every message
- Consumer error handling: log and continue, don't crash the consumer loop

## Testing

- Every test function has a clear docstring explaining what it verifies
- Use `pytest.mark.asyncio` for all async tests
- Mock external services (Bedrock, Kafka) in unit tests; use real services in e2e tests
- No real PHI in test data — all synthetic
