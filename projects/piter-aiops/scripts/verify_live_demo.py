"""Live end-to-end verification of the /console demo against EXISTING AWS.

Phase A (live AWS): respects the local .env (USE_BEDROCK=true,
RAG_BACKEND=retrieve_and_generate) and drives the exact class scenario through
the Flask test client. Asserts a grounded, cited RAG answer served by Bedrock
(mode='bedrock') plus the full 4-tool enrichment, owner/escalation, business
impact, similar incidents and follow-up session memory.

Phase B (AWS-down fallback): points BEDROCK_KB_ID at a non-existent KB so the
Bedrock call raises ResourceNotFoundException, then asserts the app transparently
falls back to the LOCAL knowledge base (mode='local') and STILL returns a grounded
card with all tools + working session memory. This proves the demo never fails.

Run:  python scripts/verify_live_demo.py
Exit 0 = all checks passed; 1 = at least one failed.
"""
from __future__ import annotations

import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

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


def _drive_triage_flow(client, *, expected_mode: str, phase: str) -> None:
    r = client.get("/console")
    check(f"[{phase}] console page loads (200)", r.status_code == 200, f"status={r.status_code}")

    r = client.post("/api/triage", json=SCENARIO)
    card = r.get_json() or {}
    check(f"[{phase}] triage returns 200 ok",
          r.status_code == 200 and card.get("ok") is True, f"status={r.status_code}")

    check(f"[{phase}] served by {expected_mode}", card.get("mode") == expected_mode,
          f"mode={card.get('mode')}")

    citations = card.get("citations") or []
    docs = " ".join(str(c.get("document", "")).lower() for c in citations)
    check(f"[{phase}] RAG answer grounded", bool(card.get("grounded")),
          f"grounded={card.get('grounded')}")
    check(f"[{phase}] >=1 citation returned", len(citations) >= 1, f"n={len(citations)}")
    check(f"[{phase}] citation references postgres CPU runbook",
          ("postgres" in docs or "rb-007" in docs or "db_cpu" in docs or "cpu" in docs),
          docs[:90])

    owner = card.get("owner") or {}
    impact = card.get("impact") or {}
    similar = card.get("similar_incidents") or []
    suspect = card.get("suspect_deploys")
    check(f"[{phase}] tool correlate_deployments ran", isinstance(suspect, list))
    check(f"[{phase}] tool owner/escalation present", bool(owner.get("primary_on_call")),
          str(owner.get("primary_on_call")))
    check(f"[{phase}] tool business impact present", bool(impact.get("sla_risk")),
          str(impact.get("sla_risk")))
    check(f"[{phase}] tool similar incidents present", len(similar) >= 1, f"n={len(similar)}")

    steps = card.get("recommended_steps") or []
    check(f"[{phase}] recommended steps >= 2", len(steps) >= 2, f"n={len(steps)}")

    sid = card.get("session_id")
    check(f"[{phase}] session id issued", bool(sid), str(sid))
    r = client.post("/api/follow-up", json={"session_id": sid, "question": FOLLOW_UP})
    fu = r.get_json() or {}
    check(f"[{phase}] follow-up returns 200 ok",
          r.status_code == 200 and fu.get("ok") is True, f"status={r.status_code}")
    check(f"[{phase}] follow-up used session memory", fu.get("memory_used") is True,
          f"memory_used={fu.get('memory_used')} kind={fu.get('kind')}")


def main() -> int:
    # --- Phase A: live AWS path (uses .env as-is) ---
    print("=" * 64)
    print("PHASE A — live AWS (USE_BEDROCK=true, RAG_BACKEND from .env)")
    print("=" * 64)
    from app import create_app  # imported after sys.path setup

    app_a = create_app()
    cfg_a = app_a.config.get("PITER_CONFIG")
    use_bedrock = getattr(cfg_a, "USE_BEDROCK", None)
    backend = getattr(cfg_a, "RAG_BACKEND", None)
    check("[A] app configured for live Bedrock",
          bool(use_bedrock) and backend in ("agent", "retrieve_and_generate"),
          f"USE_BEDROCK={use_bedrock} RAG_BACKEND={backend}")
    if not use_bedrock:
        print("NOTE: USE_BEDROCK is false — skipping live AWS assertions. "
              "Set USE_BEDROCK=true in .env to verify the live path.")
    else:
        _drive_triage_flow(app_a.test_client(), expected_mode="bedrock", phase="A")

    # --- Phase B: AWS-down -> local fallback ---
    print("=" * 64)
    print("PHASE B — simulated AWS-down (bad KB id) -> local fallback")
    print("=" * 64)
    os.environ["USE_BEDROCK"] = "true"
    os.environ["PITER_USE_BEDROCK"] = "true"
    os.environ["RAG_BACKEND"] = "retrieve_and_generate"
    os.environ["BEDROCK_KB_ID"] = "ZZZZZZZZZZ"  # valid format, does not exist
    os.environ["PITER_BEDROCK_KB_ID"] = "ZZZZZZZZZZ"
    # Phase B only needs enough config for Config.from_env() to build; the bad KB id
    # forces the Bedrock call to fail so the app falls back to LOCAL. Supply harmless
    # defaults so this phase runs even with no .env / no AWS credentials at all.
    os.environ.setdefault("AWS_REGION", "us-east-1")
    os.environ.setdefault("PITER_AWS_REGION", os.environ["AWS_REGION"])
    os.environ.setdefault(
        "BEDROCK_MODEL_ARN",
        "arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-3-haiku-20240307-v1:0",
    )
    os.environ.setdefault("PITER_BEDROCK_MODEL_ARN", os.environ["BEDROCK_MODEL_ARN"])
    os.environ.setdefault("FLASK_SECRET_KEY", "verify-local-fallback")
    os.environ.setdefault("PITER_FLASK_SECRET_KEY", os.environ["FLASK_SECRET_KEY"])
    # Fresh app: create_app() re-reads Config.from_env() with the broken KB id,
    # so the Bedrock call fails (ResourceNotFound live, or auth/endpoint error
    # offline) and the app falls back to the local knowledge base.
    app_b = create_app()
    _drive_triage_flow(app_b.test_client(), expected_mode="local", phase="B")

    print("-" * 64)
    failed = [label for ok, label in _results if not ok]
    total = len(_results)
    passed = total - len(failed)
    print(f"RESULT: {passed}/{total} checks passed")
    if failed:
        print("FAILED CHECKS:")
        for label in failed:
            print(f"  - {label}")
        return 1
    print("ALL CHECKS PASSED -- live AWS demo + local fallback are class-ready.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
