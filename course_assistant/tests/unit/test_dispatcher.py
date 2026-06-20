"""Tests for the Dispatcher (language detection, guardrail, agent routing)."""

from __future__ import annotations

from langchain_core.messages import AIMessage

from course_assistant.agent.dispatcher import Dispatcher, detect_language
from course_assistant.config import Settings
from course_assistant.drive.fake import FakeDriveService
from course_assistant.rag.embeddings import HashingEmbedder
from course_assistant.rag.stores import InMemoryVectorStore
from tests.fixtures.fake_llm import FakeToolCallingModel


def _dispatcher(drive: FakeDriveService, model: FakeToolCallingModel) -> Dispatcher:
    return Dispatcher(
        drive=drive,
        store=InMemoryVectorStore(HashingEmbedder(dim=64)),
        settings=Settings(_env_file=None),  # type: ignore[call-arg]
        model=model,
    )


def test_detect_language() -> None:
    assert detect_language("מתי השיעור הבא?") == "he"
    assert detect_language("when is the next lesson?") == "en"


def test_solve_request_short_circuits_to_disclaimer(drive: FakeDriveService) -> None:
    # Model would error if called; the guardrail must short-circuit before the agent.
    model = FakeToolCallingModel(responses=[])
    out = _dispatcher(drive, model).respond("please just do my homework for me")
    assert "can't complete your homework" in out


def test_normal_request_runs_agent(drive: FakeDriveService) -> None:
    model = FakeToolCallingModel(
        responses=[
            AIMessage(
                content="",
                tool_calls=[
                    {
                        "name": "drive_lookup",
                        "args": {"lesson": 1, "category": "recordings"},
                        "id": "c1",
                    }
                ],
            ),
            AIMessage(content="The lesson 1 recording is available."),
        ]
    )
    out = _dispatcher(drive, model).respond("where is the recording for lesson 1?")
    assert out == "The lesson 1 recording is available."
