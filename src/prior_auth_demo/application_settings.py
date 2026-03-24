"""Application configuration via environment variables.

Uses pydantic-settings BaseSettings to load from .env file or environment.
All external URLs, credentials, and thresholds are configured here.
"""

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class ApplicationSettings(BaseSettings):
    """Central configuration for the prior authorization demo.

    Loads from environment variables or .env file. ANTHROPIC_API_KEY is
    the only required value — all others have sensible defaults.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Anthropic
    anthropic_api_key: SecretStr = Field(..., description="Anthropic API key for Claude access")
    claude_model_id: str = Field(
        default="claude-sonnet-4-6",
        description="Claude model identifier",
    )

    # Application
    log_level: str = Field(default="INFO", description="Logging level")

    # Confidence thresholds
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
