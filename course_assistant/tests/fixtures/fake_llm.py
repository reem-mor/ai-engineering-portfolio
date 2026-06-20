"""A scripted, tool-calling fake chat model for agent tests (no network)."""

from __future__ import annotations

from typing import Any

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AIMessage, BaseMessage
from langchain_core.outputs import ChatGeneration, ChatResult
from pydantic import PrivateAttr


class FakeToolCallingModel(BaseChatModel):
    """Returns a pre-scripted sequence of ``AIMessage`` objects, one per call.

    Use it to drive ``create_react_agent``: script a first message with
    ``tool_calls`` and a second plain message as the final answer.
    """

    responses: list[AIMessage]
    _idx: int = PrivateAttr(default=0)

    @property
    def _llm_type(self) -> str:
        return "fake-tool-calling"

    def bind_tools(self, tools: Any, **kwargs: Any) -> FakeToolCallingModel:
        return self

    def _generate(
        self,
        messages: list[BaseMessage],
        stop: list[str] | None = None,
        run_manager: Any = None,
        **kwargs: Any,
    ) -> ChatResult:
        message = self.responses[min(self._idx, len(self.responses) - 1)]
        self._idx += 1
        return ChatResult(generations=[ChatGeneration(message=message)])
