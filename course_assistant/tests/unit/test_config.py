"""Phase 1 smoke tests: the package imports and settings behave as designed."""

from __future__ import annotations

import importlib

import pytest

from course_assistant.config import (
    LLMProvider,
    Settings,
    VectorStoreBackend,
    get_settings,
)


def _blank_settings(**overrides: object) -> Settings:
    """Build Settings ignoring any ambient .env, with explicit overrides."""
    return Settings(_env_file=None, **overrides)  # type: ignore[call-arg]


def test_package_imports() -> None:
    """The top-level package and its subpackages import without side effects."""
    for module in (
        "course_assistant",
        "course_assistant.config",
        "course_assistant.rag",
        "course_assistant.tools",
        "course_assistant.drive",
        "course_assistant.agent",
        "course_assistant.interface",
    ):
        assert importlib.import_module(module) is not None


def test_defaults_match_mvp_decisions() -> None:
    """Defaults reflect the locked decisions: Claude Sonnet + local Chroma."""
    settings = _blank_settings()
    assert settings.llm_provider is LLMProvider.ANTHROPIC
    assert settings.llm_model == "claude-sonnet-4-6"
    assert settings.vector_store is VectorStoreBackend.CHROMA


def test_admin_ids_parsed_from_csv_string() -> None:
    """Comma-separated env value parses into a list of ints; blank -> empty."""
    assert _blank_settings(admin_telegram_ids="11, 22 ,33").admin_telegram_ids == [11, 22, 33]
    assert _blank_settings(admin_telegram_ids="").admin_telegram_ids == []


def test_require_llm_key_raises_when_missing() -> None:
    """Requesting the LLM key with none configured fails loudly (never at import)."""
    settings = _blank_settings(llm_provider=LLMProvider.ANTHROPIC, anthropic_api_key=None)
    with pytest.raises(RuntimeError, match="No API key configured"):
        settings.require_llm_key()


def test_require_llm_key_returns_secret_for_provider() -> None:
    """The key for the configured provider is returned and stays secret."""
    settings = _blank_settings(
        llm_provider=LLMProvider.OPENAI,
        openai_api_key="sk-test-123",
    )
    secret = settings.require_llm_key()
    assert secret.get_secret_value() == "sk-test-123"
    assert "sk-test-123" not in repr(settings)


def test_get_settings_is_cached() -> None:
    """get_settings returns a cached singleton."""
    assert get_settings() is get_settings()
