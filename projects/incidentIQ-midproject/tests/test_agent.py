"""Tests for triage orchestration, session memory, and follow-up reuse."""
from __future__ import annotations

import pytest

from app.local_agent import LocalRagClient
from app.services import session_memory
from app.services.triage_service import DEMO_ALERT, run_follow_up, run_triage


@pytest.fixture(autouse=True)
def _clean_sessions():
    session_memory.reset()
    yield
    session_memory.reset()


def _ask():
    client = LocalRagClient()
    return lambda q: client.ask(q)


def test_run_triage_returns_full_contract():
    card = run_triage(dict(DEMO_ALERT), ask_fn=_ask())
    for key in (
        "answer", "citations", "recommended_steps", "suspect_deploys",
        "owner", "impact", "similar_incidents", "session_id", "memory_used", "mode",
    ):
        assert key in card, f"missing contract key: {key}"
    assert card["mode"] == "local"
    assert card["memory_used"] is False
    assert card["citations"][0]["document"] == "RB-007-postgres-cpu-high.md"
    assert card["owner"]["owner_team"] == "platform-dba"
    assert card["impact"]["cost_per_15min"] == 30000
    assert card["similar_incidents"]


def test_triage_persists_session():
    card = run_triage(dict(DEMO_ALERT), ask_fn=_ask())
    stored = session_memory.get_session(card["session_id"])
    assert stored is not None
    assert stored["triage_card"]["matched_runbook"] == "RB-007-postgres-cpu-high.md"
    assert "lookup_owner_and_escalation" in stored["tool_outputs"]


def test_follow_up_owner_uses_memory():
    card = run_triage(dict(DEMO_ALERT), ask_fn=_ask())
    res = run_follow_up(card["session_id"], "who do I escalate to?", ask_fn=_ask())
    assert res is not None
    assert res["memory_used"] is True
    assert res["kind"] == "owner"
    assert "dba-oncall" in res["answer"]


def test_follow_up_impact_uses_memory():
    card = run_triage(dict(DEMO_ALERT), ask_fn=_ask())
    res = run_follow_up(card["session_id"], "what is the business impact?", ask_fn=_ask())
    assert res["memory_used"] is True
    assert res["kind"] == "impact"


def test_follow_up_general_does_fresh_lookup():
    card = run_triage(dict(DEMO_ALERT), ask_fn=_ask())
    res = run_follow_up(card["session_id"], "show me the SQL again", ask_fn=_ask())
    assert res["memory_used"] is False
    assert res["kind"] == "sql"


def test_follow_up_unknown_session_returns_none():
    assert run_follow_up("does-not-exist", "anything", ask_fn=_ask()) is None


def test_followup_history_is_recorded():
    card = run_triage(dict(DEMO_ALERT), ask_fn=_ask())
    run_follow_up(card["session_id"], "who owns this?", ask_fn=_ask())
    stored = session_memory.get_session(card["session_id"])
    assert len(stored["followups"]) == 1
