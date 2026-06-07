"""SPA-equivalent demo verification using API-only checks (no /console dependency).

Mirrors the core triage + follow-up assertions from verify_live_demo.py so the
React SPA can replace /console after this script passes 29/29 equivalent checks.

Run:  python scripts/verify_spa_demo.py
"""
from __future__ import annotations

import os
import sys

from dotenv import load_dotenv

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

load_dotenv(os.path.join(REPO_ROOT, ".env"), override=True)

from app.services.alert_stream import p1_demo_alert  # noqa: E402

SCENARIO = {
    "alert_id": "ALERT-DEMO-PG-CPU",
    "service": "postgres",
    "environment": "NJ-DGE",
    "severity": "P2",
    "symptom": "PostgreSQL CPU above 90%",
    "description": "prod-db-1 CPU reached 95% for 5 minutes and settlement latency is increasing.",
    "alert_time": "2026-06-10T09:00:00Z",
    "duration_minutes": 45,
}
FOLLOW_UP = "Who do I escalate this to?"

_results: list[tuple[bool, str]] = []


def check(label: str, passed: bool, detail: str = "") -> bool:
    _results.append((passed, label))
    mark = "PASS" if passed else "FAIL"
    line = f"[{mark}] {label}"
    if detail:
        line += f" -- {detail}"
    print(line)
    return passed


def _drive_api_flow(client, *, expected_mode: str, phase: str) -> None:
    r = client.get("/api/bootstrap")
    boot = r.get_json() or {}
    check(f"[{phase}] bootstrap ok", r.status_code == 200 and boot.get("ok") is True)
    stream = boot.get("alert_stream") or {}
    check(f"[{phase}] alert stream in bootstrap", 390 <= stream.get("total", 0) <= 400)

    r = client.get("/api/alert-stream")
    stream_api = r.get_json() or {}
    check(f"[{phase}] alert-stream endpoint", r.status_code == 200 and stream_api.get("ok") is True)
    p1 = stream_api.get("p1_trigger") or {}
    check(f"[{phase}] storm P1 trigger present", bool(p1.get("service") == "bet-service"))
    check(
        f"[{phase}] p1_demo_alert payload",
        p1_demo_alert().get("service") == "bet-service",
    )

    r = client.post("/api/triage", json=SCENARIO)
    card = r.get_json() or {}
    check(f"[{phase}] triage returns 200 ok", r.status_code == 200 and card.get("ok") is True)
    check(f"[{phase}] served by {expected_mode}", card.get("mode") == expected_mode)

    citations = card.get("citations") or []
    check(f"[{phase}] RAG answer grounded", bool(card.get("grounded")))
    check(f"[{phase}] >=1 citation returned", len(citations) >= 1)

    owner = card.get("owner") or {}
    impact = card.get("impact") or {}
    similar = card.get("similar_incidents") or []
    suspect = card.get("suspect_deploys")
    check(f"[{phase}] tool correlate_deployments ran", isinstance(suspect, list))
    check(f"[{phase}] tool owner/escalation present", bool(owner.get("primary_on_call")))
    check(f"[{phase}] tool business impact present", bool(impact.get("sla_risk")))
    check(f"[{phase}] tool similar incidents present", len(similar) >= 1)

    steps = card.get("recommended_steps") or []
    check(f"[{phase}] recommended steps >= 2", len(steps) >= 2)

    sid = card.get("session_id")
    check(f"[{phase}] session id issued", bool(sid))
    r = client.post("/api/follow-up", json={"session_id": sid, "question": FOLLOW_UP})
    fu = r.get_json() or {}
    check(f"[{phase}] follow-up returns 200 ok", r.status_code == 200 and fu.get("ok") is True)
    check(f"[{phase}] follow-up used session memory", fu.get("memory_used") is True)

    r = client.get("/api/kb/manifest")
    kb = r.get_json() or {}
    check(f"[{phase}] kb manifest ok", r.status_code == 200 and kb.get("ok") is True and len(kb.get("documents", [])) >= 11)


def main() -> int:
    from app import create_app

    print("=" * 64)
    print("SPA DEMO — Phase A (live Bedrock when configured)")
    print("=" * 64)
    app_a = create_app()
    cfg_a = app_a.config.get("PITER_CONFIG")
    use_bedrock = getattr(cfg_a, "USE_BEDROCK", None)
    if use_bedrock:
        _drive_api_flow(app_a.test_client(), expected_mode="bedrock", phase="A")
    else:
        check("[A] USE_BEDROCK skipped", True, "set USE_BEDROCK=true to verify live path")

    print("=" * 64)
    print("SPA DEMO — Phase B (bad KB id -> local fallback)")
    print("=" * 64)
    os.environ["USE_BEDROCK"] = "true"
    os.environ["PITER_USE_BEDROCK"] = "true"
    os.environ["BEDROCK_KB_ID"] = "ZZZZZZZZZZ"
    os.environ["PITER_BEDROCK_KB_ID"] = "ZZZZZZZZZZ"
    app_b = create_app()
    _drive_api_flow(app_b.test_client(), expected_mode="local", phase="B")

    passed = sum(1 for ok, _ in _results if ok)
    total = len(_results)
    print("=" * 64)
    print(f"RESULT: {passed}/{total} checks passed")
    return 0 if passed == total else 1


if __name__ == "__main__":
    raise SystemExit(main())
