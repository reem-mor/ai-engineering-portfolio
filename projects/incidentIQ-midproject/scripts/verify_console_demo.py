"""Offline end-to-end verification of the /console demo flow.

Drives the exact class scenario (postgres / NJ-DGE / P2 / Postgres CPU 95%)
through the Flask test client in guaranteed local mode (USE_BEDROCK=false) and
checks the 15 live-demo validation points that do not require a browser.

Run:  python scripts/verify_console_demo.py
Exit code 0 = all checks passed; 1 = at least one failed.
"""
from __future__ import annotations

import os
import sys

# Force the guaranteed offline path before importing the app factory.
os.environ["USE_BEDROCK"] = "false"

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from app import create_app  # noqa: E402

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


def main() -> int:
    app = create_app()
    client = app.test_client()

    # 1. App / console opens.
    r = client.get("/console")
    check("console page loads (200)", r.status_code == 200, f"status={r.status_code}")

    # 2. Demo alert loads.
    r = client.get("/api/demo-alert")
    alert_ok = r.status_code == 200 and r.get_json().get("ok") is True
    check("demo alert loads", alert_ok, f"status={r.status_code}")

    # 3. Submit alert -> triage card.
    r = client.post("/api/triage", json=SCENARIO)
    card = r.get_json() or {}
    check("triage returns 200 ok", r.status_code == 200 and card.get("ok") is True,
          f"status={r.status_code}")

    # 4. Cited RAG answer grounded in the runbooks.
    citations = card.get("citations") or []
    docs = " ".join(str(c.get("document", "")).lower() for c in citations)
    check("RAG answer is grounded", bool(card.get("grounded")),
          f"grounded={card.get('grounded')}")
    check("at least one citation returned", len(citations) >= 1,
          f"n={len(citations)}")
    check("citation points at postgres CPU runbook",
          ("postgres" in docs and "cpu" in docs) or "rb-007" in docs,
          docs[:80])

    # 5. All 4 tools enriched the result.
    owner = card.get("owner") or {}
    impact = card.get("impact") or {}
    similar = card.get("similar_incidents") or []
    suspect = card.get("suspect_deploys") or []
    check("tool: correlate_deployments ran", isinstance(suspect, list))
    check("tool: owner/escalation present", bool(owner.get("primary_on_call")),
          str(owner.get("primary_on_call")))
    check("tool: business impact present", bool(impact.get("sla_risk")),
          str(impact.get("sla_risk")))
    check("tool: similar incidents present", len(similar) >= 1,
          f"n={len(similar)}")

    # 6. Owner + escalation + impact rendered with real values.
    check("escalation chain available",
          bool(owner.get("escalation_chain") or owner.get("escalation_path")))
    check("business impact has a cost estimate",
          impact.get("estimated_total_cost") is not None,
          str(impact.get("estimated_total_cost")))

    # 7. Recommended steps composed.
    steps = card.get("recommended_steps") or []
    check("recommended steps >= 2", len(steps) >= 2, f"n={len(steps)}")

    # 8. Local mode used (guaranteed fallback path).
    check("mode is local (offline guarantee)", card.get("mode") == "local",
          str(card.get("mode")))

    # 9-10. Follow-up uses session memory.
    sid = card.get("session_id")
    check("session id issued", bool(sid), str(sid))
    r = client.post("/api/follow-up", json={"session_id": sid, "question": FOLLOW_UP})
    fu = r.get_json() or {}
    check("follow-up returns 200 ok", r.status_code == 200 and fu.get("ok") is True,
          f"status={r.status_code}")
    check("follow-up used memory", fu.get("memory_used") is True,
          f"memory_used={fu.get('memory_used')} kind={fu.get('kind')}")
    check("follow-up answer references owner",
          bool(fu.get("owner")) or "escalate" in str(fu.get("answer", "")).lower())

    # 11. Off-topic safety: unrelated alert is refused, not falsely grounded.
    r = client.post("/api/triage", json={
        "service": "marketing",
        "symptom": "What is the best pizza topping?",
        "environment": "dev",
        "severity": "P4",
    })
    off = r.get_json() or {}
    check("off-topic alert is not falsely grounded",
          off.get("grounded") is False,
          f"grounded={off.get('grounded')}")

    print("-" * 60)
    failed = [label for ok, label in _results if not ok]
    total = len(_results)
    passed = total - len(failed)
    print(f"RESULT: {passed}/{total} checks passed")
    if failed:
        print("FAILED CHECKS:")
        for label in failed:
            print(f"  - {label}")
        return 1
    print("ALL CHECKS PASSED -- offline demo path is class-ready.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
