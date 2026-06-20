"""Guardrail against "just do my homework for me" requests.

The assistant helps students *understand* and *submit* homework — it does not
complete assignments for them. :func:`looks_like_solve_request` flags such asks
so the agent can respond with :func:`homework_help_disclaimer` instead of solving.
"""

from __future__ import annotations

import re

_SOLVE_PATTERNS = [
    r"\bdo (?:my|the) homework\b",
    r"\b(?:solve|complete|finish|answer) (?:my|the|this)\b.*"
    r"\b(?:homework|assignment|exercise|task)\b",
    r"\bwrite (?:the |my |all )?(?:code|solution|answer|program)\b.*\bfor me\b",
    r"\bgive me (?:the )?(?:answer|solution|code)\b",
    r"\bsolve (?:it|this) for me\b",
    # Hebrew
    r"תעשה לי את ה?שיעור",
    r"תפתור לי",
    r"תכתוב לי את הקוד",
    r"תן לי את התשובה",
    r"תעשה את השיעור",
]

_SOLVE_RE = re.compile("|".join(_SOLVE_PATTERNS), re.IGNORECASE)

_DISCLAIMER = {
    "en": (
        "I can't complete your homework for you — that's yours to do. "
        "But I can explain the concepts, point you to the relevant course materials, "
        "and help you format and submit it correctly. Want me to do any of those?"
    ),
    "he": (
        "אני לא יכול לעשות את שיעורי הבית במקומך — זה התפקיד שלך. "
        "אבל אני יכול להסביר מושגים, להפנות אותך לחומרי הקורס הרלוונטיים, "
        "ולעזור לך להגיש את העבודה בפורמט הנכון. רוצה שאעזור באחד מאלה?"
    ),
}


def looks_like_solve_request(text: str) -> bool:
    """True if ``text`` is asking the assistant to do the homework itself."""
    return bool(_SOLVE_RE.search(text))


def homework_help_disclaimer(lang: str = "he") -> str:
    """The bilingual "I won't solve it, but I can help" message."""
    return _DISCLAIMER["he" if lang.lower().startswith("he") else "en"]
