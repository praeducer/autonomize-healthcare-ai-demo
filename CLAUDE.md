# AI-Driven Prior Authorization Demo

## Project Context

Interview exercise for Autonomize AI demonstrating AI-driven prior authorization automation. This is a **demo-scope prototype** — not the full enterprise architecture.

**Full architecture**: `../solutions-architecture-agent/outputs/eng-2026-004/proposal.md`
**Implementation spec**: `../solutions-architecture-agent/outputs/eng-2026-004/plans/implementation-prompt.md`

**Owner**: Paul Prae — Modular Earth LLC (www.paulprae.com)

## Tech Stack

| Layer | Technology |
|-------|-----------|
| API | FastAPI (Python 3.12) |
| Event Bus | Apache Kafka (Confluent, KRaft mode) |
| AI | Amazon Bedrock (Claude) |
| Database | PostgreSQL 16 |
| Models | Pydantic v2 |
| Testing | pytest + pytest-asyncio |

## Build & Run

```bash
docker compose up -d          # Start Kafka + PostgreSQL
pip install -e ".[dev]"       # Install dependencies
uvicorn src.main:app --reload --port 8000  # Run the app
```

Or use the Makefile: `make up && make install && make dev`

## Demo Scope

### What this does
PA request flows through: **Portal submission → Eligibility check → Clinical data retrieval → AI determination → Response delivery**

### What this does NOT do
- No fax ingestion or OCR (portal-only)
- No X12 278 EDI processing
- No legacy database connectors (FHIR-only)
- No multi-LOB configuration (single LOB)
- No MLOps pipeline or drift detection
- No production security hardening
- No multi-AZ deployment

## Architecture

```
Provider Portal (FastAPI) → Kafka → PA Processing Service →
  ├── Eligibility Check (mock Facets API)
  ├── Clinical Data (mock FHIR R4 endpoint)
  ├── Guidelines Match (mock InterQual API)
  └── AI Determination (Amazon Bedrock Claude) →
      Kafka → Response Service → API response
```

## Implementation Phases

1. **Project Setup** — FastAPI skeleton, Kafka/PostgreSQL via Docker, DB schema
2. **Mock Services** — Facets eligibility, FHIR R4, InterQual guidelines
3. **Ingestion Pipeline** — POST `/pa/submit`, validation, Kafka producer
4. **PA Processing** — Kafka consumer, orchestrated pipeline, Bedrock integration
5. **Response & Dashboard** — Status API, metrics dashboard
6. **End-to-End Test** — 10 sample PA requests, verification

## Coding Standards

- Python 3.12 with type hints on all function signatures
- Pydantic v2 models for all data structures
- Async FastAPI endpoints
- Ruff for linting and formatting (`ruff check`, `ruff format`)
- Module docstrings on every file explaining purpose
- No commented-out code — delete or implement
- Environment config via pydantic-settings or `os.environ`

## API Endpoints

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/pa/submit` | Submit PA request |
| GET | `/pa/status/{request_id}` | Check PA status |
| GET | `/pa/dashboard` | Processing metrics |
| GET | `/health` | Health check |

## Key Configuration

- `PA_AUTO_APPROVE_THRESHOLD=0.85` — confidence threshold for auto-approval
- `BEDROCK_MODEL_ID=anthropic.claude-sonnet-4-6-20260320`
- See `.env.example` for all environment variables

## Testing

```bash
make test              # Run all tests
pytest tests/ -v       # Verbose output
```
