# Architecture Rules

## Event-Driven Pattern

- All PA processing is asynchronous via Kafka
- POST `/pa/submit` publishes to `pa-requests` topic and returns immediately with request_id
- PA processor consumes from `pa-requests`, orchestrates the pipeline, publishes to `pa-determinations`
- Response service consumes from `pa-determinations` and updates the database

## Service Boundaries

- `src/main.py` — FastAPI app, HTTP endpoints only. No business logic.
- `src/pa_processor.py` — Core pipeline orchestration. Calls mock services and Bedrock.
- `src/bedrock_client.py` — Bedrock integration only. Prompt construction and response parsing.
- `src/mock_services/` — Each mock service is a self-contained FastAPI router.
- `src/database.py` — Database connection and queries only. No HTTP or Kafka logic.
- `src/kafka_utils.py` — Kafka producer/consumer helpers only.

## Configuration

- All external URLs, credentials, and thresholds come from environment variables
- Use `src/config.py` as the single source of truth for configuration
- Never hardcode connection strings, model IDs, or thresholds in business logic

## Demo Constraints

- Docker Compose only — no cloud deployment
- Single Kafka partition per topic (demo scale)
- PostgreSQL without connection pooling (demo scale)
- No TLS, no auth, no encryption (this is a demo)
