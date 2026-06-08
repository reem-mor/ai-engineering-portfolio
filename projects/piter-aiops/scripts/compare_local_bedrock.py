#!/usr/bin/env python3
"""Compare local TF-IDF RAG vs live Bedrock KB on the same questions."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv

load_dotenv(ROOT / ".env")

from app.bedrock_client import BedrockRagClient  # noqa: E402
from app.config import Config  # noqa: E402
from app.local_agent import LocalRagClient  # noqa: E402

EXTRA = [
    {
        "id": "bet-p1",
        "question": "bet-service critical errors GIB UKGC P1 — what is the runbook?",
        "expected_source_contains": ["runbook_bet_service", "RB-011"],
        "answer_keywords": ["bet", "rollback", "escalat"],
    },
]


def _source_labels(citations) -> list[str]:
    return [getattr(c, "source_label", "") or "" for c in citations]


def _overlap(local_labels: list[str], bedrock_labels: list[str]) -> bool:
    local_set = {x.lower() for x in local_labels if x}
    bed_set = {x.lower() for x in bedrock_labels if x}
    return bool(local_set & bed_set) or any(
        any(l in b or b in l for b in bed_set) for l in local_set
    )


def main() -> int:
    cfg = Config.from_env()
    local = LocalRagClient(cfg)
    bedrock = BedrockRagClient(cfg)
    questions = json.loads((ROOT / "evaluation" / "test_questions.json").read_text(encoding="utf-8"))
    questions = [q for q in questions if not q.get("expect_validation_error")] + EXTRA

    failed = 0
    print(f"Model: {cfg.BEDROCK_MODEL_ARN}\n")
    for item in questions:
        q = item["question"]
        local_r = local.ask(q)
        bed_r = bedrock.ask(q)
        local_labels = _source_labels(local_r.citations)
        bed_labels = _source_labels(bed_r.citations)
        grounded_ok = local_r.grounded == bed_r.grounded
        source_ok = True
        expected = item.get("expected_source_contains", [])
        if expected and bed_r.grounded:
            blob = " ".join(bed_labels).lower()
            source_ok = any(e.lower() in blob for e in expected)
        overlap_ok = _overlap(local_labels, bed_labels) if local_r.grounded and bed_r.grounded else True
        ok = grounded_ok and source_ok and overlap_ok
        if not ok:
            failed += 1
        status = "PASS" if ok else "FAIL"
        print(f"[{status}] {item.get('id', '?')}: {q[:70]}")
        print(f"  local: grounded={local_r.grounded} sources={local_labels[:3]}")
        print(f"  bedrock: grounded={bed_r.grounded} sources={bed_labels[:3]}")
        if not grounded_ok:
            print("  mismatch: grounded flag differs")
        if not source_ok:
            print(f"  mismatch: bedrock missing expected {expected}")
        if not overlap_ok:
            print("  mismatch: no overlapping citation labels")
        print()

    return failed


if __name__ == "__main__":
    raise SystemExit(main())
