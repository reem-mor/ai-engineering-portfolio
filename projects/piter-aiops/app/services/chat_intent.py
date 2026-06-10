"""Lightweight intent guard for /api/chat — greetings and capability prompts."""
from __future__ import annotations

import re

_GREETING = re.compile(
    r"^(?:hi|hello|hey|yo|howdy|good\s+(?:morning|afternoon|evening)|sup|what(?:'s| is) up)\b[\s!.?]*$",
    re.I,
)
_CAPABILITY = re.compile(
    r"^(?:help|what can you do|capabilities|who are you|what are you)\b",
    re.I,
)

CAPABILITY_REPLY = """I'm the **PITER Ops** incident assistant. I can help you with:

- **Triage** — classify priority and summarize alert context
- **Runbooks** — grounded answers from the knowledge base
- **Deployments** — recent changes for a service
- **Escalation** — on-call paths and notification previews (human approval required)
- **Post-mortems** — draft summaries from investigation history

Select an incident context or ask one of the suggested questions to get started."""


def small_talk_reply(question: str) -> str | None:
    """Return a canned reply for greetings/capability asks, or None to continue RAG."""
    q = question.strip()
    if not q:
        return None
    if _GREETING.match(q):
        return CAPABILITY_REPLY
    if _CAPABILITY.match(q):
        return CAPABILITY_REPLY
    return None
