"""Typed application settings, loaded from environment variables / ``.env``.

All configuration — including every secret — flows through :class:`Settings`.
Nothing is hardcoded; secrets are held as :class:`~pydantic.SecretStr` so they are
redacted from logs and ``repr`` output.
"""

from __future__ import annotations

from enum import StrEnum
from functools import lru_cache

from pydantic import Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class LLMProvider(StrEnum):
    """Supported chat-model providers (configurable; default Anthropic)."""

    ANTHROPIC = "anthropic"
    OPENAI = "openai"


class VectorStoreBackend(StrEnum):
    """Supported vector-store backends. Local Chroma by default, Pinecone swappable."""

    CHROMA = "chroma"
    PINECONE = "pinecone"


class Settings(BaseSettings):
    """Application settings sourced from environment variables / ``.env``.

    Grouped by the build phase that introduces each value. Phase 1 needs nothing
    mandatory to import; downstream phases validate their own requirements at the
    point of use so the scaffold and tests run without live credentials.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # --- Core / LLM (Phase 1 & 4) -------------------------------------------
    llm_provider: LLMProvider = LLMProvider.ANTHROPIC
    llm_model: str = "claude-sonnet-4-6"
    anthropic_api_key: SecretStr | None = None
    openai_api_key: SecretStr | None = None

    # --- Telegram interface (Phase 5) --------------------------------------
    telegram_bot_token: SecretStr | None = None
    admin_telegram_ids: list[int] = Field(default_factory=list)

    # --- Google Drive (Phase 2) --------------------------------------------
    google_oauth_client_id: str | None = None
    google_oauth_client_secret: SecretStr | None = None
    google_oauth_refresh_token: SecretStr | None = None
    drive_root_folder_id: str | None = None

    # --- RAG / vector store (Phase 3) --------------------------------------
    vector_store: VectorStoreBackend = VectorStoreBackend.CHROMA
    chroma_dir: str = "./data/chroma"
    embedding_model: str = "text-embedding-3-small"
    pinecone_api_key: SecretStr | None = None
    pinecone_index: str | None = None

    # --- Homework submission (Phase 4) -------------------------------------
    hw_to_email: str | None = None
    hw_cc_email: str | None = None

    # --- Misc --------------------------------------------------------------
    log_level: str = "INFO"

    @field_validator("admin_telegram_ids", mode="before")
    @classmethod
    def _parse_admin_ids(cls, value: object) -> object:
        """Accept a comma-separated string (env form) or an already-parsed list."""
        if value is None or value == "":
            return []
        if isinstance(value, str):
            return [int(part.strip()) for part in value.split(",") if part.strip()]
        return value

    def require_llm_key(self) -> SecretStr:
        """Return the API key for the configured provider, or raise if missing.

        Call this at the point an LLM request is actually made — never at import.
        """
        key = (
            self.anthropic_api_key
            if self.llm_provider is LLMProvider.ANTHROPIC
            else self.openai_api_key
        )
        if key is None:
            raise RuntimeError(
                f"No API key configured for LLM_PROVIDER={self.llm_provider.value}. "
                "Set the matching *_API_KEY in your environment."
            )
        return key


@lru_cache
def get_settings() -> Settings:
    """Return a cached :class:`Settings` instance (read once per process)."""
    return Settings()
