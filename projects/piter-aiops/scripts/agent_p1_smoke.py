#!/usr/bin/env python3
"""Single P1 bet-service invoke_agent smoke for AWS mutation validation."""
from __future__ import annotations

import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv  # noqa: E402

load_dotenv(ROOT / ".env")
os.environ.setdefault("RAG_BACKEND", "agent")

from app.config import Config  # noqa: E402
from app.rag_factory import get_rag_client  # noqa: E402

PROMPT = """P1 incident detected:
Service: bet-service
Environment: GIB-UKGC
Title: CRITICAL: bet-service nodes unresponsive - 100% error rate
Affected users: 32000

Return:
1. Priority
2. Investigation findings
3. Triage plan
4. Escalation recommendation
5. Resolution plan
6. Business impact
7. Sources
8. Confidence and uncertainty"""

SECTIONS = (
    "Priority",
    "Investigation findings",
    "Triage plan",
    "Escalation recommendation",
    "Resolution plan",
    "Business impact",
    "Sources",
    "Confidence and uncertainty",
)

EMAIL_RE = re.compile(r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}", re.I)
PHONE_RE = re.compile(
    r"(?<!\d)(?:\+\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}(?!\d)"
)


def main() -> int:
    cfg = Config.from_env()
    if cfg.RAG_BACKEND != "agent":
        print("RAG_BACKEND must be agent", file=sys.stderr)
        return 1
    client = get_rag_client(cfg)
    result = client.ask(PROMPT)
    text = result.answer
    failures: list[str] = []
    for section in SECTIONS:
        if section.lower() not in text.lower():
            failures.append(f"missing section: {section}")
    if not result.grounded:
        failures.append("expected grounded citations")
    if EMAIL_RE.search(text):
        failures.append("raw email in response")
    if PHONE_RE.search(text):
        failures.append("raw phone in response")
    print(f"backend=agent grounded={result.grounded} citations={len(result.citations)} latency_ms={result.latency_ms}")
    preview = text[:400].encode("ascii", errors="replace").decode("ascii")
    print(f"answer_preview={preview}...")
    if failures:
        for f in failures:
            print(f"FAIL: {f}")
        return 1
    print("PASS: P1 bet-service agent smoke")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
