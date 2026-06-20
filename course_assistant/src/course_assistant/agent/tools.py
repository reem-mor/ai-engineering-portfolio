"""LangChain tool wrappers around the course-assistant tools.

Each wrapper closes over :class:`AgentDeps` so the underlying Phase 2–4 functions
get the right services and the conversation language. Tools are read-only; the
email send flow is handled deterministically by the interface, not the LLM.
"""

from __future__ import annotations

from langchain_core.tools import BaseTool, StructuredTool

from course_assistant.agent.deps import AgentDeps
from course_assistant.tools.drive_lookup import DriveCategory, drive_lookup
from course_assistant.tools.homework import explain_homework_submission
from course_assistant.tools.search_materials import search_course_materials

_VALID_CATEGORIES = ", ".join(c.value for c in DriveCategory)


def build_tools(deps: AgentDeps) -> list[BaseTool]:
    """Build the agent's tool set bound to ``deps``."""

    def _drive_lookup(lesson: int, category: str = "all") -> str:
        """Look up Drive materials for a lesson."""
        try:
            cat = DriveCategory(category.lower())
        except ValueError:
            return f"Unknown category '{category}'. Valid: {_VALID_CATEGORIES}."
        return drive_lookup(deps.drive, lesson, cat, lang=deps.lang)

    def _search_course_materials(query: str) -> str:
        """Search the course materials for relevant content."""
        return search_course_materials(deps.store, query, k=4, lang=deps.lang)

    def _explain_homework_submission() -> str:
        """Explain how to submit homework by email."""
        return explain_homework_submission(
            lang=deps.lang,
            to_email=deps.settings.hw_to_email,
            cc_email=deps.settings.hw_cc_email,
        )

    return [
        StructuredTool.from_function(
            _drive_lookup,
            name="drive_lookup",
            description=(
                "Get Drive links for a specific lesson. Args: lesson (int), "
                f"category (one of: {_VALID_CATEGORIES}; default 'all'). "
                "Use for 'where are the recordings/slides/homework/code for lesson N'."
            ),
        ),
        StructuredTool.from_function(
            _search_course_materials,
            name="search_course_materials",
            description=(
                "Search the course materials (slides, homework, code) to answer a "
                "content question. Args: query (str). Returns snippets with sources."
            ),
        ),
        StructuredTool.from_function(
            _explain_homework_submission,
            name="explain_homework_submission",
            description=(
                "Explain the exact homework submission procedure (recipients, subject "
                "format, body, attachments). No arguments."
            ),
        ),
    ]
