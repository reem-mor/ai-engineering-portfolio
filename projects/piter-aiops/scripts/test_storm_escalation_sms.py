#!/usr/bin/env python3
"""Verify alert-storm escalation modal path sends SMS (same as UI button)."""
from __future__ import annotations

import importlib.util
import json
import os
import sys
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv

load_dotenv(ROOT / ".env")

from app.services.escalation_service import notify_demo_channel  # noqa: E402
from app.services.notification_dispatch import check_sms_account_ready  # noqa: E402

LAMBDA_PATH = ROOT / "action_groups" / "piter-escalation" / "lambda_function.py"


def _clear_idempotency() -> None:
    spec = importlib.util.spec_from_file_location("piter_escalation_lambda", LAMBDA_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.SENT_IDEMPOTENCY_KEYS.clear()


def main() -> int:
    _clear_idempotency()
    phone = os.environ.get("PITER_DEMO_SMS_RECIPIENT", "").strip()
    token = os.environ.get("PITER_NOTIFICATION_CONFIRMATION_TOKEN", "piter").strip()

    sms_ready = check_sms_account_ready(phone=phone or None)
    ctx = {
        "incident_id": "ALT-2026-06-10-0251",
        "severity": "P1",
        "service": "bet-service",
        "environment": "GIB-UKGC",
        "incident_title": "CRITICAL: bet-service nodes unresponsive - 100% error rate on GIB-UKGC",
        "on_call_name": "Primary on-call engineer",
        "owner_team": "Platform SRE",
        "war_room_channel": "#war-room",
        "business_impact": "32000 affected users; 100% error rate on active market",
        "support_complaints": "Support ticket volume above baseline",
        "top_error": "HTTP 5xx / connection errors",
        "recent_deployment": "v2.4.1 deployed 27m ago",
        "recommended_actions": ["Acknowledge incident", "Join war room", "Review deploy"],
        "runbook_count": 5,
    }

    result = notify_demo_channel(
        channel="sms",
        incident_id=ctx["incident_id"],
        service=ctx["service"],
        severity=ctx["severity"],
        confirmation_token=token,
        escalation_context=ctx,
        idempotency_key=f"{ctx['incident_id']}:sms:storm-verify-{uuid.uuid4().hex[:8]}",
    )

    report = {
        "bootstrap_sms": sms_ready,
        "storm_escalation_sms": {
            k: result.get(k)
            for k in (
                "http_status",
                "ok",
                "sent",
                "channel",
                "route",
                "message_id",
                "blocked",
                "reasons",
                "message",
            )
        },
    }
    print(json.dumps(report, indent=2))
    ok = bool(result.get("sent")) and int(result.get("http_status", 0)) == 200
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
