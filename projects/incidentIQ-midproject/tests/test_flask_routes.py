"""Route tests for the local-first triage API and Bedrock auto-fallback."""
from __future__ import annotations

import pytest

from app import create_app
from app.bedrock_client import Citation, RagAnswer
from app.errors import BedrockError
from app.services import session_memory


@pytest.fixture(autouse=True)
def _clean_sessions():
    session_memory.reset()
    yield
    session_memory.reset()


# --- /health, /api/demo-alert ----------------------------------------------

def test_health_ok(local_client):
    resp = local_client.get("/health")
    assert resp.status_code == 200
    assert resp.get_json()["status"] == "ok"


def test_demo_alert(local_client):
    resp = local_client.get("/api/demo-alert")
    body = resp.get_json()
    assert body["ok"] is True
    assert body["alert"]["service"] == "postgres"
    assert body["alert"]["environment"] == "NJ-DGE"


# --- /api/triage -----------------------------------------------------------

def test_triage_returns_card(local_client):
    alert = local_client.get("/api/demo-alert").get_json()["alert"]
    resp = local_client.post("/api/triage", json=alert)
    assert resp.status_code == 200
    body = resp.get_json()
    assert body["ok"] is True
    assert body["mode"] == "local"
    assert body["grounded"] is True
    assert body["citations"][0]["document"] == "RB-007-postgres-cpu-high.md"
    for key in ("recommended_steps", "owner", "impact", "similar_incidents", "session_id"):
        assert key in body


def test_triage_rejects_incomplete_alert(local_client):
    resp = local_client.post("/api/triage", json={"environment": "NJ-DGE"})
    assert resp.status_code == 400
    assert resp.get_json()["reason"] == "invalid_alert"


# --- /api/follow-up --------------------------------------------------------

def test_follow_up_reuses_session(local_client):
    alert = local_client.get("/api/demo-alert").get_json()["alert"]
    sid = local_client.post("/api/triage", json=alert).get_json()["session_id"]
    resp = local_client.post("/api/follow-up", json={"session_id": sid, "question": "who do I escalate to?"})
    assert resp.status_code == 200
    body = resp.get_json()
    assert body["memory_used"] is True
    assert "dba-oncall" in body["answer"]


def test_follow_up_missing_session(local_client):
    resp = local_client.post("/api/follow-up", json={"question": "hello there"})
    assert resp.status_code == 400
    assert resp.get_json()["reason"] == "missing_session"


def test_follow_up_unknown_session(local_client):
    resp = local_client.post("/api/follow-up", json={"session_id": "nope", "question": "who owns this?"})
    assert resp.status_code == 404
    assert resp.get_json()["reason"] == "unknown_session"


def test_console_page(local_client):
    resp = local_client.get("/console")
    assert resp.status_code == 200
    assert b"AI Incident" in resp.data


# --- Bedrock auto-fallback to local ----------------------------------------

class _FailingClient:
    def ask(self, question, *, session_id=None, session_attributes=None, prompt_session_attributes=None):
        raise BedrockError("Bedrock is down", code="bedrock_error")


def test_ask_falls_back_to_local(fake_config):
    app = create_app(fake_config)
    app.config.update(TESTING=True, WTF_CSRF_ENABLED=False, FORCE_LEGACY_UI=True, LOCAL_FALLBACK=True)
    app.extensions["bedrock_client"] = _FailingClient()
    client = app.test_client()
    resp = client.post("/ask", json={"question": "Postgres CPU is 95% on prod-db-1 — what is the runbook?"})
    assert resp.status_code == 200
    body = resp.get_json()
    assert body["ok"] is True
    assert body["mode"] == "local"
    assert body["citations"][0]["source_label"].startswith("RB-007")


def test_validation_error_not_masked_by_fallback(fake_config):
    app = create_app(fake_config)
    app.config.update(TESTING=True, WTF_CSRF_ENABLED=False, FORCE_LEGACY_UI=True, LOCAL_FALLBACK=True)
    app.extensions["bedrock_client"] = _FailingClient()
    client = app.test_client()
    resp = client.post("/ask", json={"question": "x"})
    assert resp.status_code == 400  # short_question, not a fallback
