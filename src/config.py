"""
Centralized configuration via Pydantic Settings.

All env vars listed here are the project's single source of truth.
Defaults are D:-drive-safe per the global disk policy.

Test harness overrides via env-var patching or `Settings.model_validate({...})`.
"""

from functools import lru_cache
from typing import Any, Literal

from pydantic import Field, ValidationInfo, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment + .env file."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ---- Application ----
    app_env: Literal["development", "production", "test"] = "development"
    app_version: str = "0.1.0"
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    secret_key: str = Field(..., min_length=32)

    # ---- Database ----
    database_url: str = "postgresql+psycopg://lc:lc@localhost:5432/life_companion"
    database_pool_size: int = 10
    database_max_overflow: int = 20
    duckdb_temp_dir: str = "D:/test 2/Life Companion/data/cache/duckdb_temp"

    # ---- Redis ----
    redis_url: str = "redis://localhost:6379/0"
    redis_token_ttl_seconds: int = 900

    # ---- Firebase ----
    firebase_project_id: str = ""
    firebase_service_account_path: str = ""

    # ---- LLM ----
    gemini_api_key: str = ""
    gemini_model_primary: str = "gemini-3.1-pro-preview"
    gemini_model_fallback: str = "gemini-2.5-flash"
    anthropic_api_key: str = ""
    claude_model: str = "claude-sonnet-4-6"
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    llm_max_retries: int = 3
    llm_retry_wait_min_s: float = 2.0
    llm_retry_wait_max_s: float = 30.0

    # ---- Encryption ----
    # Phase 1 = passthrough; Phase 4 wires real KMS/Vault provider.
    encryption_key_stub: str = "stub-key-replace-in-phase4"

    # ---- Crisis ----
    crisis_regex_enabled: bool = True
    crisis_llm_enabled: bool = False  # Phase 2 flips this on
    crisis_llm_cache_ttl_s: int = 3600

    # ---- Payments (Phase 5 declared early so config is single source) ----
    stripe_secret_key: str = ""
    stripe_webhook_secret: str = ""
    yookassa_shop_id: str = ""
    yookassa_secret_key: str = ""

    # ---- Observability ----
    otel_enabled: bool = False
    otel_exporter_endpoint: str = ""
    sentry_dsn: str = ""

    # ---- Paths (D:-only per global rule) ----
    log_dir: str = "D:/test 2/Life Companion/logs"
    data_dir: str = "D:/test 2/Life Companion/data"

    # ---- CORS ----
    cors_origins: list[str] = Field(
        default_factory=lambda: ["http://localhost:3000", "http://localhost:8000"]
    )

    # ---- Test infra ----
    postgresql_bin: str = "D:/PostgreSQL/16/bin"

    @field_validator("log_dir", "data_dir", "duckdb_temp_dir")
    @classmethod
    def reject_c_drive_paths(cls, v: str) -> str:
        """Enforce D:-drive-only policy on path settings."""
        normalized = v.replace("\\", "/").strip().lower()
        if normalized.startswith("c:/") or normalized.startswith("c:\\"):
            raise ValueError(
                f"Refusing C:-drive path '{v}'. Use D:/ per global disk policy."
            )
        return v

    @field_validator("encryption_key_stub")
    @classmethod
    def reject_stub_key_in_production(cls, v: str, info: ValidationInfo) -> str:
        """Refuse to start in production with the stub encryption key."""
        data: dict[str, Any] = info.data or {}
        if data.get("app_env") == "production" and v == "stub-key-replace-in-phase4":
            raise ValueError(
                "ENCRYPTION_KEY_STUB must be replaced with a real KMS/Vault "
                "reference before production deployment."
            )
        return v

    @field_validator("cors_origins")
    @classmethod
    def reject_localhost_cors_in_production(
        cls, v: list[str], info: ValidationInfo
    ) -> list[str]:
        data: dict[str, Any] = info.data or {}
        if data.get("app_env") == "production":
            for origin in v:
                if "localhost" in origin or "127.0.0.1" in origin:
                    raise ValueError(
                        f"Localhost CORS origin '{origin}' not permitted in production."
                    )
        return v

    @property
    def is_test(self) -> bool:
        return self.app_env == "test"

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return the singleton settings instance. Cached for the process lifetime."""
    return Settings()  # type: ignore[call-arg]
