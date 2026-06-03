"""Select RAG backend: Bedrock Agent (invoke_agent) or direct RetrieveAndGenerate."""
from __future__ import annotations

from typing import Protocol

from app.bedrock_agent_client import BedrockAgentClient
from app.bedrock_client import BedrockRagClient, RagAnswer
from app.config import Config


class RagClient(Protocol):
    def ask(self, question: str, *, session_id: str | None = None) -> RagAnswer: ...


def get_rag_client(config: Config, *, client: object | None = None) -> RagClient:
    if config.RAG_BACKEND == "retrieve_and_generate":
        return BedrockRagClient(config, client=client)
    return BedrockAgentClient(config, client=client)
