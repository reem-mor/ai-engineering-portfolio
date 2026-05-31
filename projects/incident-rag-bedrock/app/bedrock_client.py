"""Thin boto3 wrapper around Bedrock Knowledge Base RetrieveAndGenerate."""
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

import boto3

from app.config import Config
from app.errors import BedrockError, translate

log = logging.getLogger(__name__)

MIN_QUESTION_LEN = 1
MAX_QUESTION_LEN = 500


@dataclass(frozen=True)
class Citation:
    snippet: str
    source_uri: str | None


@dataclass(frozen=True)
class RagAnswer:
    answer: str
    citations: list[Citation]
    session_id: str | None
    grounded: bool  # True if at least one citation was returned

    def to_dict(self) -> dict[str, Any]:
        return {
            "answer": self.answer,
            "citations": [{"snippet": c.snippet, "source_uri": c.source_uri} for c in self.citations],
            "session_id": self.session_id,
            "grounded": self.grounded,
        }


class BedrockRagClient:
    """One call: question in, grounded answer + citations out.

    Designed with a clean `ask()` seam so we can wrap it as an MCP tool later.
    """

    def __init__(self, config: Config, *, client: Any | None = None) -> None:
        self._config = config
        self._client = client or boto3.client("bedrock-agent-runtime", region_name=config.AWS_REGION)

    def ask(self, question: str) -> RagAnswer:
        question = (question or "").strip()
        if len(question) < MIN_QUESTION_LEN:
            raise BedrockError("Please enter a question.", code="empty_question")
        if len(question) > MAX_QUESTION_LEN:
            raise BedrockError(
                f"Question is too long ({len(question)} chars). Maximum is {MAX_QUESTION_LEN}.",
                code="oversize_question",
            )

        try:
            response = self._client.retrieve_and_generate(
                input={"text": question},
                retrieveAndGenerateConfiguration={
                    "type": "KNOWLEDGE_BASE",
                    "knowledgeBaseConfiguration": {
                        "knowledgeBaseId": self._config.BEDROCK_KB_ID,
                        "modelArn": self._config.BEDROCK_MODEL_ARN,
                        "retrievalConfiguration": {
                            "vectorSearchConfiguration": {
                                "numberOfResults": self._config.BEDROCK_NUM_RESULTS,
                            },
                        },
                    },
                },
            )
        except Exception as exc:  # noqa: BLE001 — funneled through translate()
            log.exception("Bedrock retrieve_and_generate failed")
            raise translate(exc) from exc

        return _parse_response(response)


def _parse_response(response: dict[str, Any]) -> RagAnswer:
    answer_text = (response.get("output", {}) or {}).get("text", "").strip()
    citations_raw = response.get("citations", []) or []

    parsed: list[Citation] = []
    for citation in citations_raw:
        for ref in citation.get("retrievedReferences", []) or []:
            snippet = (ref.get("content", {}) or {}).get("text", "").strip()
            location = ref.get("location", {}) or {}
            source_uri = (location.get("s3Location", {}) or {}).get("uri")
            if snippet:
                parsed.append(Citation(snippet=snippet, source_uri=source_uri))

    grounded = bool(parsed)
    if not grounded and not answer_text:
        answer_text = "I could not find anything in the knowledge base for that question."

    return RagAnswer(
        answer=answer_text,
        citations=parsed,
        session_id=response.get("sessionId"),
        grounded=grounded,
    )
