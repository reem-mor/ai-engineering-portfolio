"""Unit tests for enrichment tools and Lambda handlers (demo scenario)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

from app.enrichment_tools import (
    correlate_deployments,
    enrich_triage_demo,
    find_similar_incidents,
    lookup_owner,
    score_business_impact,
)

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data" / "agent_data"

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


@pytest.mark.parametrize(
    "folder,event_file",
    [
        ("iiq-correlate", "demo_correlate.json"),
        ("iiq-context", "demo_owner.json"),
        ("iiq-similar", "demo_similar.json"),
    ],
)
def test_lambda_handlers_demo_events(folder: str, event_file: str):
    import importlib.util

    ag_dir = ROOT / "action_groups" / folder
    ag_str = str(ag_dir)
    if ag_str not in sys.path:
        sys.path.insert(0, ag_str)
    spec = importlib.util.spec_from_file_location(
        f"lambda_{folder.replace('-', '_')}",
        ag_dir / "lambda_function.py",
    )
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    event = json.loads((ag_dir / "events" / event_file).read_text(encoding="utf-8"))
    resp = mod.lambda_handler(event, None)
    assert resp["response"]["httpStatusCode"] == 200
    body = json.loads(resp["response"]["responseBody"]["application/json"]["body"])
    assert "error" not in body
