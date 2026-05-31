"""Tests for production SPA + JSON API (FORCE_LEGACY_UI off)."""
from __future__ import annotations

from pathlib import Path

import pytest

from app import create_app
from app.bedrock_client import Citation, RagAnswer
from app.config import Config

SPA_INDEX = Path(__file__).resolve().parents[1] / "app" / "static" / "spa" / "index.html"


def _fake_answer():
    return RagAnswer(
        answer="Grounded answer.",
        citations=[
            Citation(
                snippet="snippet",
                source_uri="s3://b/runbook.md",
                source_label="runbook.md",
                index=1,
            )
        ],
        session_id="sess-follow",
        grounded=True,
        latency_ms=50,
        matched_runbook="runbook.md",
    )


@pytest.fixture
def spa_client(fake_config, fake_bedrock):
    if not SPA_INDEX.is_file():
        pytest.skip("SPA build missing — run: cd frontend && npm run build")
    app = create_app(fake_config)
    app.config.update(
        TESTING=True,
        WTF_CSRF_ENABLED=False,
        FORCE_LEGACY_UI=False,
    )
    app.extensions["bedrock_client"] = fake_bedrock
    return app.test_client()


def test_spa_home_serves_index(spa_client):
    response = spa_client.get("/")
    assert response.status_code == 200
    body = response.get_data(as_text=True)
    assert 'id="root"' in body or "root" in body


def test_get_ask_returns_405_in_spa_mode(spa_client):
    assert spa_client.get("/ask").status_code == 405


def test_bootstrap_example_groups_is_dict(spa_client):
    data = spa_client.get("/api/bootstrap").get_json()
    assert data["ok"] is True
    assert isinstance(data["example_groups"], dict)
    assert len(data["example_groups"]) >= 1


def test_ask_accepts_session_id(spa_client, fake_bedrock):
    fake_bedrock.next_response = _fake_answer()
    response = spa_client.post(
        "/ask",
        json={"question": "How do I triage an authentication service incident?", "session_id": "sess-abc"},
    )
    assert response.status_code == 200
    assert fake_bedrock.last_session_id == "sess-abc"
    data = response.get_json()
    assert data["session_id"] == "sess-follow"


def test_health_deep(spa_client):
    data = spa_client.get("/health?deep=1").get_json()
    assert data["status"] in {"ok", "degraded"}
    assert "checks" in data
