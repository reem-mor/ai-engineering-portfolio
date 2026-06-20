"""Tests for the agent's LangChain tool wrappers."""

from __future__ import annotations

from course_assistant.agent.deps import AgentDeps
from course_assistant.agent.tools import build_tools
from course_assistant.config import Settings
from course_assistant.drive.fake import FakeDriveService
from course_assistant.rag.embeddings import HashingEmbedder
from course_assistant.rag.stores import InMemoryVectorStore


def _deps(drive: FakeDriveService, lang: str = "en") -> AgentDeps:
    return AgentDeps(
        drive=drive,
        store=InMemoryVectorStore(HashingEmbedder(dim=64)),
        settings=Settings(_env_file=None, hw_to_email="alex@x.com", hw_cc_email="sagy@x.com"),  # type: ignore[call-arg]
        lang=lang,
    )


def test_build_tools_names(drive: FakeDriveService) -> None:
    names = {t.name for t in build_tools(_deps(drive))}
    assert names == {"drive_lookup", "search_course_materials", "explain_homework_submission"}


def test_drive_lookup_tool_invokes_underlying(drive: FakeDriveService) -> None:
    tools = {t.name: t for t in build_tools(_deps(drive))}
    out = tools["drive_lookup"].invoke({"lesson": 1, "category": "recordings"})
    assert "part 1.mp4" in out


def test_drive_lookup_tool_rejects_bad_category(drive: FakeDriveService) -> None:
    tools = {t.name: t for t in build_tools(_deps(drive))}
    out = tools["drive_lookup"].invoke({"lesson": 1, "category": "bogus"})
    assert "Unknown category" in out


def test_search_tool_handles_empty_store(drive: FakeDriveService) -> None:
    tools = {t.name: t for t in build_tools(_deps(drive))}
    out = tools["search_course_materials"].invoke({"query": "anything"})
    assert "couldn't find" in out


def test_explain_tool_uses_settings_recipients(drive: FakeDriveService) -> None:
    tools = {t.name: t for t in build_tools(_deps(drive))}
    out = tools["explain_homework_submission"].invoke({})
    assert "alex@x.com" in out
    assert "sagy@x.com" in out
