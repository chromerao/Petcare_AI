from functools import lru_cache
from typing import Literal

from pydantic import AliasChoices, Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime settings loaded from DOCQA_* environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="DOCQA_",
        extra="ignore",
    )

    app_name: str = "DocQA Lab API"
    environment: str = "local"
    log_level: str = "INFO"
    allowed_origins: list[str] = Field(default_factory=lambda: ["http://localhost:8501"])
    max_upload_mb: int = Field(default=20, ge=1, le=100)
    llm_provider: Literal["openai", "local", "disabled"] = "openai"
    openai_api_key: SecretStr | None = Field(
        default=None,
        validation_alias=AliasChoices("OPENAI_API_KEY", "DOCQA_OPENAI_API_KEY"),
        repr=False,
    )
    openai_model: str = "gpt-4.1-mini"
    openai_max_output_tokens: int = Field(default=800, ge=64, le=2000)
    openai_timeout_seconds: float = Field(default=20.0, ge=1.0, le=120.0)
    openai_max_retries: int = Field(default=1, ge=0, le=2)
    openai_store: bool = False
    llm_max_input_characters: int = Field(default=24_000, ge=1000, le=100_000)
    database_url: SecretStr | None = Field(default=None, repr=False)
    supabase_url: str | None = None
    supabase_publishable_key: SecretStr | None = Field(default=None, repr=False)
    supabase_jwt_secret: SecretStr | None = Field(default=None, repr=False)

    @property
    def openai_configured(self) -> bool:
        return self.openai_api_key is not None and bool(self.openai_api_key.get_secret_value())

    @property
    def database_configured(self) -> bool:
        return self.database_url is not None and bool(self.database_url.get_secret_value())

    @property
    def supabase_auth_configured(self) -> bool:
        jwt_secret_configured = self.supabase_jwt_secret is not None and bool(
            self.supabase_jwt_secret.get_secret_value(),
        )
        remote_auth_configured = (
            self.supabase_url is not None
            and bool(self.supabase_url)
            and self.supabase_publishable_key is not None
            and bool(self.supabase_publishable_key.get_secret_value())
        )
        return jwt_secret_configured or remote_auth_configured

    @property
    def cors_origins(self) -> list[str]:
        origins = list(dict.fromkeys(self.allowed_origins))
        if self.environment != "production":
            origins.extend(
                origin
                for origin in (
                    "http://localhost:5173",
                    "http://127.0.0.1:5173",
                    "http://localhost:8501",
                    "http://127.0.0.1:8501",
                )
                if origin not in origins
            )
        return origins

    @property
    def cors_origin_regex(self) -> str | None:
        if self.environment == "production":
            return None
        return r"^https?://(localhost|127\.0\.0\.1):(517[3-9]|518[0-9]|519[0-9]|850[1-9])$"


@lru_cache
def get_settings() -> Settings:
    return Settings()
