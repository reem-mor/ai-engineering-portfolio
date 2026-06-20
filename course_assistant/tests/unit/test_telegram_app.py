"""Light tests for the Telegram adapter wiring (no network)."""

from __future__ import annotations

import pytest

from course_assistant.agent.dispatcher import Dispatcher
from course_assistant.config import Settings
from course_assistant.drive.fake import FakeDriveService
from course_assistant.interface.telegram_app import _HELP, build_application
from course_assistant.rag.embeddings import HashingEmbedder
from course_assistant.rag.stores import InMemoryVectorStore
from tests.fixtures.fake_llm import FakeToolCallingModel


def _dispatcher(drive: FakeDriveService) -> Dispatcher:
    return Dispatcher(
        drive=drive,
        store=InMemoryVectorStore(HashingEmbedder(dim=32)),
        settings=Settings(_env_file=None),  # type: ignore[call-arg]
        model=FakeToolCallingModel(responses=[]),
    )


def test_help_text_is_bilingual() -> None:
    assert "עוז ורוח" in _HELP["he"]
    assert "course assistant" in _HELP["en"]


def test_build_application_registers_handlers(drive: FakeDriveService) -> None:
    settings = Settings(_env_file=None, telegram_bot_token="123:ABCdefGHI")  # type: ignore[call-arg]
    dispatcher = _dispatcher(drive)
    app = build_application(settings, dispatcher)
    assert app.bot_data["dispatcher"] is dispatcher
    assert app.bot_data["settings"] is settings
    # start, help, submit commands + the text handler are registered.
    assert sum(len(group) for group in app.handlers.values()) >= 4


def test_build_application_requires_token(drive: FakeDriveService) -> None:
    settings = Settings(_env_file=None, telegram_bot_token=None)  # type: ignore[call-arg]
    with pytest.raises(RuntimeError, match="TELEGRAM_BOT_TOKEN"):
        build_application(settings, _dispatcher(drive))
