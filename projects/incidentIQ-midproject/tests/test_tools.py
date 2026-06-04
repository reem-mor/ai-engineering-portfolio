"""Spec-aligned tests for the four enrichment tools (happy path + edge cases)."""
from __future__ import annotations

from pathlib import Path

from app.enrichment_tools import (
    correlate_deployments,
    find_similar_incidents,
    lookup_owner_and_escalation,
    score_business_impact,
)

DATA_DIR = Path(__file__).resolve().parents[1] / "data" / "agent_data"
ALERT_TIME = "2026-06-10T09:00:00Z"


# --- Tool 1: correlate_deployments ---------------------------------------

def test_correlate_happy_path_has_suspect_and_reason():
    r = correlate_deployments(service="postgres", environment="NJ-DGE", alert_time=ALERT_TIME, data_dir=DATA_DIR)
    assert r["likely_deploy_correlation"] is True
    assert r["suspect_deployment"]["service"] == "postgres"
    assert "deployed" in r["reason"]
    assert "dependency_hop_explanation" in r


def test_correlate_window_minutes_overrides():
    r = correlate_deployments(
        service="postgres", environment="NJ-DGE", alert_time=ALERT_TIME,
        window_minutes=30, data_dir=DATA_DIR,
    )
    # The postgres deploy was ~75 min before the alert, so a 30-min window drops it.
    assert r["window_minutes"] == 30
    assert all(d["service"] != "postgres" for d in r["deployments"])


def test_correlate_unknown_service():
    r = correlate_deployments(service="nope", environment="NJ-DGE", alert_time=ALERT_TIME, data_dir=DATA_DIR)
    assert "error" in r and r["likely_deploy_correlation"] is False


def test_correlate_invalid_timestamp():
    r = correlate_deployments(service="postgres", environment="NJ-DGE", alert_time="not-a-time", data_dir=DATA_DIR)
    assert "error" in r


def test_correlate_missing_environment():
    r = correlate_deployments(service="postgres", environment="", alert_time=ALERT_TIME, data_dir=DATA_DIR)
    assert "error" in r


# --- Tool 2: lookup_owner_and_escalation ---------------------------------

def test_owner_happy_path():
    r = lookup_owner_and_escalation(service="postgres", severity="P2", data_dir=DATA_DIR)
    assert r["owner_team"] == "platform-dba"
    assert r["primary_on_call"] == "dba-oncall"
    assert r["slack_channel"]
    assert r["escalation_chain"][0] == "platform-dba"
    assert "depends_on" in r["dependencies"]


def test_owner_unknown_service():
    assert "error" in lookup_owner_and_escalation(service="ghost", data_dir=DATA_DIR)


def test_owner_missing_service():
    assert "error" in lookup_owner_and_escalation(service="", data_dir=DATA_DIR)


# --- Tool 3: score_business_impact ---------------------------------------

def test_impact_happy_path_costs():
    r = score_business_impact(service="postgres", environment="NJ-DGE", severity="P2", duration_minutes=60, data_dir=DATA_DIR)
    assert r["revenue_impact_usd_per_hour"] == 120000
    assert r["cost_per_15min"] == 30000
    assert r["estimated_total_cost"] == 120000
    assert r["sla_risk"] == "high"
    assert r["regulatory_risk"] == "high"
    assert r["fallback"] is False


def test_impact_duration_scales_total():
    r = score_business_impact(service="postgres", environment="NJ-DGE", severity="P2", duration_minutes=30, data_dir=DATA_DIR)
    assert r["estimated_total_cost"] == 60000


def test_impact_fallback_when_no_row():
    r = score_business_impact(service="postgres", environment="UNKNOWN", severity="P1", duration_minutes=60, data_dir=DATA_DIR)
    assert r["fallback"] is True
    assert r["revenue_impact_usd_per_hour"] > 0
    assert "fallback estimate" in r["business_explanation"]


def test_impact_invalid_duration_defaults():
    r = score_business_impact(service="postgres", environment="NJ-DGE", severity="P2", duration_minutes="oops", data_dir=DATA_DIR)
    assert r["duration_minutes"] == 60


# --- Tool 4: find_similar_incidents --------------------------------------

def test_similar_happy_path_has_resolution_and_reason():
    r = find_similar_incidents(service="postgres", symptom="CPU > 90%", environment="NJ-DGE", top_k=3)
    assert r["count"] >= 1
    top = r["similar_incidents"][0]
    assert top["resolution"]
    assert top["similarity_reason"]
    assert top["environment"] == "NJ-DGE"


def test_similar_top_k_limits():
    r = find_similar_incidents(service="postgres", symptom="cpu replica lag pool", top_k=1)
    assert r["count"] <= 1


def test_similar_no_match_for_unknown_service():
    r = find_similar_incidents(service="ghost-svc", symptom="cpu", top_k=3)
    assert r["count"] == 0


def test_similar_empty_symptom():
    r = find_similar_incidents(service="postgres", symptom="", top_k=3)
    assert r["count"] == 0
