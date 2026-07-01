"""Tests for owui_kb_setup.py (mocked HTTP — no live Open WebUI required)."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

import owui_kb_setup

BASE = "http://localhost:3000"
KB_NAME = owui_kb_setup.KB_NAME


def _response(json_value) -> MagicMock:
    mock = MagicMock()
    mock.json.return_value = json_value
    mock.raise_for_status = MagicMock()
    return mock


def test_kb_name_is_ai_job_market() -> None:
    assert KB_NAME == "AI Job Market Intelligence Dataset"


def test_find_knowledge_by_name_returns_id() -> None:
    with patch(
        "owui_kb_setup.requests.get",
        return_value=_response([{"name": KB_NAME, "id": "kb-123"}]),
    ):
        assert owui_kb_setup.find_knowledge_by_name(BASE, "sk-test", KB_NAME) == "kb-123"


def test_find_knowledge_by_name_missing() -> None:
    with patch(
        "owui_kb_setup.requests.get",
        return_value=_response([{"name": "Other", "id": "kb-999"}]),
    ):
        assert owui_kb_setup.find_knowledge_by_name(BASE, "sk-test", KB_NAME) is None


def test_create_knowledge_reuses_existing() -> None:
    with patch("owui_kb_setup.find_knowledge_by_name", return_value="kb-existing"):
        assert owui_kb_setup.create_knowledge(BASE, "sk-test", KB_NAME, "d") == "kb-existing"


def test_create_knowledge_creates_new() -> None:
    with (
        patch("owui_kb_setup.find_knowledge_by_name", return_value=None),
        patch("owui_kb_setup.requests.post", return_value=_response({"id": "kb-new"})),
    ):
        assert owui_kb_setup.create_knowledge(BASE, "sk-test", KB_NAME, "d") == "kb-new"


def test_get_token_prefers_api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OWUI_API_KEY", "sk-from-env")
    assert owui_kb_setup.get_token(BASE) == "sk-from-env"


def test_get_token_signs_in_with_email(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("OWUI_API_KEY", raising=False)
    monkeypatch.setenv("OWUI_EMAIL", "user@example.com")
    monkeypatch.setenv("OWUI_PASSWORD", "secret")
    with patch("owui_kb_setup.requests.post", return_value=_response({"token": "jwt-abc"})):
        assert owui_kb_setup.get_token(BASE) == "jwt-abc"


def test_get_token_missing_credentials(monkeypatch: pytest.MonkeyPatch) -> None:
    for var in ("OWUI_API_KEY", "OWUI_EMAIL", "OWUI_PASSWORD"):
        monkeypatch.delenv(var, raising=False)
    with pytest.raises(RuntimeError, match="credentials"):
        owui_kb_setup.get_token(BASE)


def test_wait_for_file_processed_completes() -> None:
    pending = _response({"data": {"status": "pending"}})
    done = _response({"data": {"status": "completed", "content": "csv text"}})
    with (
        patch("owui_kb_setup.requests.get", side_effect=[pending, done]),
        patch("owui_kb_setup.time.sleep"),
    ):
        status = owui_kb_setup.wait_for_file_processed(BASE, "sk-test", "file-1")
    assert status == "completed"


def test_wait_for_file_processed_failure_raises() -> None:
    failed = _response({"data": {"status": "failed"}})
    with patch("owui_kb_setup.requests.get", return_value=failed):
        with pytest.raises(RuntimeError, match="failed to process"):
            owui_kb_setup.wait_for_file_processed(BASE, "sk-test", "file-1")


def test_upsert_env_updates_and_appends(tmp_path: Path) -> None:
    env = tmp_path / ".env"
    env.write_text("OWUI_URL=http://localhost:3000\nOWUI_KNOWLEDGE_ID=old\n", encoding="utf-8")
    owui_kb_setup.upsert_env(env, {"OWUI_KNOWLEDGE_ID": "kb-new", "OWUI_FILE_ID": "f-1"})
    text = env.read_text(encoding="utf-8")
    assert "OWUI_KNOWLEDGE_ID=kb-new" in text
    assert "OWUI_FILE_ID=f-1" in text
    assert "OWUI_URL=http://localhost:3000" in text
    assert "old" not in text
