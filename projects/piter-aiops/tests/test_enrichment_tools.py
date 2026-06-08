"""Unit tests for enrichment tools and Lambda handlers (demo scenario)."""
from __future__ import annotations

from pathlib import Path

from app.enrichment_tools import (
    correlate_deployments,
    enrich_triage_demo,
    find_similar_incidents,
    lookup_owner,
    score_business_impact,
)

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data" / "agent_data"
SOURCE_DIR = ROOT / "data" / "source"

DEMO = {
    "service": "postgres",
    "environment": "NJ-DGE",
    "severity": "P2",
    "symptom": "CPU > 90%",
    "alert_time": "2026-06-10T09:00:00Z",
}


def test_correlate_deployments_demo():
    result = correlate_deployments(
        service=DEMO["service"],
        environment=DEMO["environment"],
        alert_time=DEMO["alert_time"],
        data_dir=DATA_DIR,
    )
    assert "error" not in result
    assert result["environment"] == "NJ-DGE"
    assert result["likely_deploy_correlation"] is True
    assert any(d["service"] == "postgres" for d in result["deployments"])


def test_lookup_owner_demo():
    result = lookup_owner(
        service=DEMO["service"],
        environment=DEMO["environment"],
        data_dir=DATA_DIR,
    )
    assert result["owner_team"] == "platform-dba"
    assert "dba-oncall" in result["escalation_path"]


def test_score_business_impact_demo():
    result = score_business_impact(
        service=DEMO["service"],
        environment=DEMO["environment"],
        severity=DEMO["severity"],
        data_dir=DATA_DIR,
    )
    assert result["revenue_impact_usd_per_hour"] == 120000
    assert result["regulatory_flag"] is True


def test_find_similar_incidents_demo():
    result = find_similar_incidents(service=DEMO["service"], symptom=DEMO["symptom"])
    assert result["count"] >= 1
    assert any("CPU" in i["root_cause"] or "cpu" in i["root_cause"].lower() for i in result["similar_incidents"])


def test_enrich_triage_demo_bundle():
    bundle = enrich_triage_demo(data_dir=DATA_DIR)
    assert bundle["correlate_deployments"]["deployments"]
    assert bundle["lookup_owner"]["owner_team"]
    assert bundle["score_business_impact"]["tier"] == 1
    assert bundle["find_similar_incidents"]["count"] >= 1


STORM = {
    "service": "bet-service",
    "environment": "GIB-UKGC",
    "severity": "P1",
    "symptom": "CRITICAL: bet-service nodes unresponsive — 100% error rate on GIB-UKGC",
    "alert_time": "2026-06-10T10:02:55Z",
}


def test_bet_service_storm_enrichment():
    owner = lookup_owner(
        service=STORM["service"],
        environment=STORM["environment"],
        data_dir=SOURCE_DIR,
    )
    assert "error" not in owner
    assert owner["owner_team"] == "Betting Core"

    deploys = correlate_deployments(
        service=STORM["service"],
        environment=STORM["environment"],
        alert_time=STORM["alert_time"],
        data_dir=SOURCE_DIR,
    )
    assert "error" not in deploys
    assert deploys["likely_deploy_correlation"] is True

    impact = score_business_impact(
        service=STORM["service"],
        environment=STORM["environment"],
        severity=STORM["severity"],
        alert=STORM,
        data_dir=SOURCE_DIR,
    )
    assert impact["sla_risk"] == "critical"
    assert impact["revenue_impact_usd_per_hour"] == 588000

    similar = find_similar_incidents(
        service=STORM["service"],
        symptom=STORM["symptom"],
        environment=STORM["environment"],
        data_dir=SOURCE_DIR,
    )
    assert similar["count"] >= 1

