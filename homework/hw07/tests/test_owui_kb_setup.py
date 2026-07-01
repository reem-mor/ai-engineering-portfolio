"""Tests for owui_kb_setup.py (mocked HTTP — no live Open WebUI required)."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import requests

import owui_kb_setup


def test_find_knowledge_by_name_returns_id() -> None:
    mock_response = MagicMock()
    mock_response.json.return_value = [{"name": "CVE Intelligence", "id": "kb-123"}]
    mock_response.raise_for_status = MagicMock()

    with patch("owui_kb_setup.requests.get", return_value=mock_response):
        kid = owui_kb_setup.find_knowledge_by_name(
            "http://localhost:3000", "sk-test", "CVE Intelligence"
        )

    assert kid == "kb-123"


def test_find_knowledge_by_name_missing() -> None:
    mock_response = MagicMock()
    mock_response.json.return_value = [{"name": "Other", "id": "kb-999"}]
    mock_response.raise_for_status = MagicMock()

    with patch("owui_kb_setup.requests.get", return_value=mock_response):
        kid = owui_kb_setup.find_knowledge_by_name(
            "http://localhost:3000", "sk-test", "CVE Intelligence"
        )

    assert kid is None


def test_create_knowledge_reuses_existing() -> None:
    with patch("owui_kb_setup.find_knowledge_by_name", return_value="kb-existing"):
        kid = owui_kb_setup.create_knowledge(
            "http://localhost:3000", "sk-test", "CVE Intelligence", "desc"
        )
    assert kid == "kb-existing"


def test_create_knowledge_creates_new() -> None:
    mock_response = MagicMock()
    mock_response.json.return_value = {"id": "kb-new"}
    mock_response.raise_for_status = MagicMock()

    with (
        patch("owui_kb_setup.find_knowledge_by_name", return_value=None),
        patch("owui_kb_setup.requests.post", return_value=mock_response),
    ):
        kid = owui_kb_setup.create_knowledge(
            "http://localhost:3000", "sk-test", "CVE Intelligence", "desc"
        )

    assert kid == "kb-new"


def test_main_missing_api_key(tmp_path, monkeypatch) -> None:
    csv_path = tmp_path / "test.csv"
    csv_path.write_text("cve_id,cvss\nCVE-2020-1,5.0\n", encoding="utf-8")
    monkeypatch.delenv("OWUI_API_KEY", raising=False)
    monkeypatch.setattr(
        "sys.argv",
        ["owui_kb_setup.py", "--csv", str(csv_path), "--name", "Test KB"],
    )
    assert owui_kb_setup.main() == 2


def test_main_missing_csv(monkeypatch) -> None:
    monkeypatch.setenv("OWUI_API_KEY", "sk-test")
    monkeypatch.setattr(
        "sys.argv",
        [
            "owui_kb_setup.py",
            "--csv",
            "/nonexistent/file.csv",
            "--name",
            "Test",
        ],
    )
    assert owui_kb_setup.main() == 2


def test_main_http_error(tmp_path, monkeypatch) -> None:
    csv_path = tmp_path / "test.csv"
    csv_path.write_text("cve_id\nCVE-2020-1\n", encoding="utf-8")
    mock_response = MagicMock()
    mock_response.text = "Unauthorized"
    http_error = requests.HTTPError(response=mock_response)

    monkeypatch.setattr(
        "sys.argv",
        [
            "owui_kb_setup.py",
            "--csv",
            str(csv_path),
            "--name",
            "Test",
            "--api-key",
            "sk-test",
        ],
    )
    with patch("owui_kb_setup.create_knowledge", side_effect=http_error):
        assert owui_kb_setup.main() == 1
