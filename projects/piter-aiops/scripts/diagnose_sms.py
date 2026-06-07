#!/usr/bin/env python3
"""Diagnose why live SNS SMS may not reach a phone."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv

load_dotenv(ROOT / ".env")

from app.services.notification_dispatch import (  # noqa: E402
    SMS_BILLING_RESUBSCRIBE_URL,
    SMS_CONSOLE_URL,
    check_sms_account_ready,
    sms_preflight_enabled,
)


def main() -> int:
    phone = __import__("os").environ.get("PITER_DEMO_SMS_RECIPIENT", "").strip()
    status = check_sms_account_ready()
    report = {
        "demo_phone": phone,
        "preflight_enabled": sms_preflight_enabled(),
        "sms_account": status,
        "console_url": SMS_CONSOLE_URL,
        "billing_url": SMS_BILLING_RESUBSCRIBE_URL,
        "fix_script": "python scripts/fix_sms_subscription.py",
        "next_steps": [],
    }

    if status.get("ready"):
        report["next_steps"] = [
            "Account SMS settings look OK. Send a test: python scripts/test_live_notify.py",
            "If still no SMS, verify the phone in SNS SMS sandbox and check carrier filtering.",
        ]
    else:
        report["next_steps"] = [
            "Run: python scripts/fix_sms_subscription.py  (opens console + auto-configures when ready)",
            f"Or manually: {SMS_CONSOLE_URL}",
            "Accept SMS terms, set monthly spend limit ($10+), verify sandbox phone.",
            f"Account verification if prompted: {SMS_BILLING_RESUBSCRIBE_URL}",
        ]

    print(json.dumps(report, indent=2))
    return 0 if status.get("ready") else 1


if __name__ == "__main__":
    raise SystemExit(main())
