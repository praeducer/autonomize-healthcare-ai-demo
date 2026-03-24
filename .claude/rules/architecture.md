# Architecture Rules

## Configuration

- All external URLs, credentials, and thresholds come from environment variables
- Use `src/config.py` as the single source of truth for configuration
- Never hardcode connection strings, model IDs, or thresholds in business logic
