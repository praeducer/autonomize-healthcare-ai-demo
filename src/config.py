"""Environment configuration.

Loads settings from environment variables (or .env file) using Pydantic
or os.environ. All external service URLs and credentials are configured here.

Implementation: Phase 1.
"""

import os


def get_database_url() -> str:
    """Get PostgreSQL connection URL from environment."""
    # TODO Phase 1: Use pydantic-settings for typed config
    return os.environ.get(
        "DATABASE_URL",
        "postgresql://pa_user:pa_dev_password@localhost:5432/pa_demo",
    )


def get_kafka_bootstrap_servers() -> str:
    """Get Kafka bootstrap servers from environment."""
    return os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")


def get_bedrock_model_id() -> str:
    """Get Amazon Bedrock model ID from environment."""
    return os.environ.get("BEDROCK_MODEL_ID", "anthropic.claude-sonnet-4-6-20260320")


def get_auto_approve_threshold() -> float:
    """Get confidence threshold for auto-approval."""
    return float(os.environ.get("PA_AUTO_APPROVE_THRESHOLD", "0.85"))
