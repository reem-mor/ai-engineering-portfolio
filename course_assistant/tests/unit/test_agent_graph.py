"""Tests for chat-model selection and the agent loop (with a fake model)."""

from __future__ import annotations

from langchain_core.messages import AIMessage, HumanMessage, ToolMessage

from course_assistant.agent.deps import AgentDeps
from course_assistant.agent.graph import build_agent, build_chat_model
from course_assistant.config import LLMProvider, Settings
from course_assistant.drive.fake import FakeDriveService
from course_assistant.rag.embeddings import HashingEmbedder
from course_assistant.rag.stores import InMemoryVectorStore
from tests.fixtures.fake_llm import FakeToolCallingModel


def _deps(drive: FakeDriveService) -> AgentDeps:
    return AgentDeps(
        drive=drive,
        store=InMemoryVectorStore(HashingEmbedder(dim=64)),
        settings=Settings(_env_file=None),  # type: ignore[call-arg]
        lang="en",
    )


def test_build_chat_model_selects_provider() -> None:
    anthropic = build_chat_model(
        Settings(_env_file=None, llm_provider=LLMProvider.ANTHROPIC, anthropic_api_key="x")  # type: ignore[call-arg]
    )
    assert type(anthropic).__name__ == "ChatAnthropic"
    openai = build_chat_model(
        Settings(_env_file=None, llm_provider=LLMProvider.OPENAI, openai_api_key="x")  # type: ignore[call-arg]
    )
    assert type(openai).__name__ == "ChatOpenAI"


def test_agent_executes_tool_and_returns_final(drive: FakeDriveService) -> None:
    model = FakeToolCallingModel(
        responses=[
            AIMessage(
                content="",
                tool_calls=[
                    {
                        "name": "drive_lookup",
                        "args": {"lesson": 1, "category": "recordings"},
                        "id": "call_1",
                    }
                ],
            ),
            AIMessage(content="Here are the recordings for lesson 1."),
        ]
    )
    agent = build_agent(_deps(drive), model=model)
    result = agent.invoke({"messages": [HumanMessage(content="recordings for lesson 1")]})

    messages = result["messages"]
    tool_messages = [m for m in messages if isinstance(m, ToolMessage)]
    assert tool_messages, "expected the drive_lookup tool to run"
    assert "part 1.mp4" in tool_messages[0].content  # real fake-drive data flowed through
    assert isinstance(messages[-1], AIMessage)
    assert "recordings for lesson 1" in messages[-1].content
