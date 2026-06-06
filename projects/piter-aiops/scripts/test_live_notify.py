#!/usr/bin/env python3
"""Send test live escalation email + SMS using .env gates."""
from __future__ import annotations

import json
import sys
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv

load_dotenv(ROOT / ".env")

from app.services.escalation_service import notify_demo_channel  # noqa: E402


def send(channel: str) -> dict:
    suffix = uuid.uuid4().hex[:8]
    return notify_demo_channel(
        channel=channel,
        incident_id=f"INC-TEST-{suffix}",
        service="bet-service",
        severity="P1",
        confirmation_token=__import__("os").environ.get("PITER_NOTIFICATION_CONFIRMATION_TOKEN", ""),
        message=(
            f"PITER test {channel.upper()}: P1 bet-service outage on GIB-UKGC. "
            "If you received this, live escalation works."
        ),
        idempotency_key=f"test-{channel}-{suffix}",
    )


def main() -> int:
    results = {}
    for channel in ("email", "sms"):
        try:
            results[channel] = send(channel)
        except Exception as exc:  # noqa: BLE001
            results[channel] = {"sent": False, "error": str(exc)}
    print(json.dumps(results, indent=2))
    ok = all(r.get("sent") for r in results.values())
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
