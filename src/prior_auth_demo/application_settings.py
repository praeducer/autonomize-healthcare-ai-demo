"""Application configuration via environment variables.

Uses pydantic-settings BaseSettings to load values from a .env file or
the shell environment. This is the single source of truth for all external
URLs, credentials, and tunable thresholds.

See README.md § 3 "Configuration Layer" for a walkthrough of the patterns used here.
"""

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class ApplicationSettings(BaseSettings):
    """Central configuration — loaded once, passed to every subsystem.

    Instantiate with ``ApplicationSettings()`` — pydantic-settings reads
    env vars and .env automatically. ANTHROPIC_API_KEY is the only
    required value (``Field(...)`` means required); everything else has
    a sensible default.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # --- Anthropic ---
    # SecretStr wraps the key so it won't leak in logs or .model_dump() output.
    # Access the raw value with .get_secret_value() when calling the API.
    anthropic_api_key: SecretStr = Field(..., description="Anthropic API key for Claude access")
    claude_model_id: str = Field(
        default="claude-sonnet-4-6",
        description="Claude model identifier",
    )

    # Application
    log_level: str = Field(default="INFO", description="Logging level")

    # --- Confidence Thresholds ---
    # Drive the routing logic in clinical_review_engine.apply_confidence_routing().
    # ge/le constraints are validated by Pydantic at construction time.
    auto_approve_confidence_threshold: float = Field(
        default=0.85,
        ge=0.0,
        le=1.0,
        description="Minimum confidence for auto-approval",
    )
    human_review_confidence_threshold: float = Field(
        default=0.60,
        ge=0.0,
        le=1.0,
        description="Minimum confidence before routing to human review",
    )

    # FHIR Server (used in Step 2+)
    fhir_server_url: str = Field(
        default="http://localhost:8080/fhir",
        description="HAPI FHIR server base URL",
    )
