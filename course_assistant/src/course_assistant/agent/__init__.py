"""LangGraph agent: tools + bilingual system prompt + guardrails.

The agent answers course questions via the read-only tools (`drive_lookup`,
`search_course_materials`, `explain_homework_submission`). The homework *send*
flow is handled deterministically by the interface, not the LLM. The LLM is
mocked in tests — no paid calls in CI.
"""

from course_assistant.agent.deps import AgentDeps
from course_assistant.agent.dispatcher import Dispatcher, detect_language
from course_assistant.agent.graph import build_agent, build_chat_model
from course_assistant.agent.tools import build_tools

__all__ = [
    "AgentDeps",
    "Dispatcher",
    "build_agent",
    "build_chat_model",
    "build_tools",
    "detect_language",
]
