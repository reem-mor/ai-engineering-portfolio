"""Build the LangGraph ReAct agent and its chat model."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from langgraph.prebuilt import create_react_agent

from course_assistant.agent.deps import AgentDeps
from course_assistant.agent.prompt import SYSTEM_PROMPT
from course_assistant.agent.tools import build_tools
from course_assistant.config import LLMProvider, Settings

if TYPE_CHECKING:
    from langchain_core.language_models import BaseChatModel


def build_chat_model(settings: Settings) -> BaseChatModel:
    """Construct the configured chat model (Claude by default; OpenAI optional)."""
    key = settings.require_llm_key()  # SecretStr
    if settings.llm_provider is LLMProvider.ANTHROPIC:
        from langchain_anthropic import ChatAnthropic

        return ChatAnthropic(
            model_name=settings.llm_model, api_key=key, timeout=None, stop=None
        )
    from langchain_openai import ChatOpenAI

    return ChatOpenAI(model=settings.llm_model, api_key=key)


def build_agent(deps: AgentDeps, model: BaseChatModel | None = None) -> Any:
    """Create the ReAct agent: chat model + tools + system prompt.

    ``model`` can be injected (e.g. a fake model in tests); otherwise it is built
    from settings.
    """
    chat_model = model if model is not None else build_chat_model(deps.settings)
    return create_react_agent(chat_model, build_tools(deps), prompt=SYSTEM_PROMPT)
