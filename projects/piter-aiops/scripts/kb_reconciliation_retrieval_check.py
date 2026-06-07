#!/usr/bin/env python3
"""Spot-check Bedrock retrieval for reconciled RB topics."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.bedrock_client import BedrockRagClient
from app.config import Config

CHECKS = [
    ("RB-006 promotions", "Promotions engine p95 latency above 800ms cache miss promo rules", ["runbook_promotions", "RB-006"]),
    ("RB-008 redis", "Redis token store eviction storm auth login failures FLUSHALL", ["runbook_redis", "RB-008"]),
    ("RB-009 kafka", "Kafka consumer lag settlement group offset reset do not skip", ["runbook_kafka", "RB-009"]),
    ("RB-010 rollback", "deployment rollback forward-only migration kubectl rollout undo", ["runbook_deployment_rollback", "RB-010"]),
    ("RB-001 gateway", "API Gateway 5xx WAF throttle integration timeout RB-001", ["api_gateway_5xx", "RB-001"]),
]


def main() -> int:
    client = BedrockRagClient(Config.from_env())
    failed = 0
    for name, question, frags in CHECKS:
        result = client.ask(question)
        labels = " ".join(c.source_label or "" for c in result.citations)
        blob = f"{labels} {result.answer or ''}".lower()
        hit = any(f.lower() in blob for f in frags)
        ok = hit and result.grounded
        status = "PASS" if ok else "FAIL"
        print(f"[{status}] {name}: grounded={result.grounded} labels={labels[:120]}")
        if not ok:
            failed += 1
    return failed


if __name__ == "__main__":
    raise SystemExit(main())
