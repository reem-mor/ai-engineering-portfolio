"""Turns a user message into a reply: guardrail check, then the agent.

Interface-agnostic so it can sit behind Telegram (or anything else). Detects the
language, short-circuits "do my homework" requests to the disclaimer, and
otherwise runs the LangGraph agent.
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

from langchain_core.messages import AIMessage, HumanMessage

from course_assistant.agent.deps import AgentDeps
from course_assistant.agent.graph import build_agent, build_chat_model
from course_assistant.config import Settings
from course_assistant.drive.service import BaseDriveService
from course_assistant.homework.guardrail import homework_help_disclaimer, looks_like_solve_request
from course_assistant.rag.vectorstore import VectorStore

if TYPE_CHECKING:
    from langchain_core.language_models import BaseChatModel

_HEBREW_RE = re.compile(r"[֐-׿]")

_FALLBACK = {
    "he": "מצטער, לא הצלחתי לעבד את הבקשה. נסה/י לנסח מחדש.",
    "en": "Sorry, I couldn't process that. Please try rephrasing.",
}


def detect_language(text: str) -> str:
    """Return ``"he"`` if the text contains Hebrew letters, else ``"en"``."""
    return "he" if _HEBREW_RE.search(text or "") else "en"


def _last_ai_text(result: dict[str, object]) -> str:
    messages = result.get("messages", [])
    if not isinstance(messages, list):
        return ""
    for message in reversed(messages):
        if isinstance(message, AIMessage):
            content = message.content
            if isinstance(content, str):
                return content
            if isinstance(content, list):
                return "".join(
                    part.get("text", "")
                    for part in content
                    if isinstance(part, dict)
                )
    return ""


class Dispatcher:
    """Routes a message to the guardrail or the agent and returns a reply string."""

    def __init__(
        self,
        drive: BaseDriveService,
        store: VectorStore,
        settings: Settings,
        model: BaseChatModel | None = None,
    ) -> None:
        self._drive = drive
        self._store = store
        self._settings = settings
        self._model = model

    def _chat_model(self) -> BaseChatModel:
        if self._model is None:
            self._model = build_chat_model(self._settings)
        return self._model

    def respond(self, text: str) -> str:
        """Produce a reply for ``text`` in the user's detected language."""
        lang = detect_language(text)
        if looks_like_solve_request(text):
            return homework_help_disclaimer(lang)
        deps = AgentDeps(self._drive, self._store, self._settings, lang=lang)
        agent = build_agent(deps, model=self._chat_model())
        result = agent.invoke({"messages": [HumanMessage(content=text)]})
        return _last_ai_text(result) or _FALLBACK[lang]
