"""Thin boto3 wrapper around Bedrock Knowledge Base RetrieveAndGenerate."""
from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from typing import Any

import boto3

from app.config import Config
from app.errors import BedrockError, translate
from app.text_utils import format_citation_label
from app.validators import MAX_QUESTION_LEN, validate_question

log = logging.getLogger(__name__)

# Re-export for templates and tests that import from bedrock_client.
MIN_QUESTION_LEN = 3

# Override Bedrock default prompt (which can nudge models toward tool-style output).
RAG_GENERATION_PROMPT = """You are IncidentIQ, an NOC assistant. Answer ONLY using the search results below.
Write plain English runbook steps. Do NOT emit tool calls, JSON, or lines starting with "Action:".

User question:
$query$

Search results:
$search_results$

$output_format_instructions$
"""


@dataclass(frozen=True)
class Citation:
    snippet: str
    source_uri: str | None
    source_label: str = "Unknown source"
    index: int = 1


@dataclass(frozen=True)
class RagAnswer:
    answer: str
    citations: list[Citation]
    session_id: str | None
    grounded: bool
    latency_ms: int = 0
    matched_runbook: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "answer": self.answer,
            "citations": [
                {
                    "snippet": c.snippet,
                    "source_uri": c.source_uri,
                    "source_label": c.source_label,
                    "index": c.index,
                }
                for c in self.citations
            ],
            "session_id": self.session_id,
            "grounded": self.grounded,
            "latency_ms": self.latency_ms,
            "matched_runbook": self.matched_runbook,
        }


class BedrockRagClient:
    """One call: question in, grounded answer + citations out."""

    def __init__(self, config: Config, *, client: Any | None = None) -> None:
        self._config = config
        self._client = client or boto3.client("bedrock-agent-runtime", region_name=config.AWS_REGION)

    def ask(self, question: str, *, session_id: str | None = None) -> RagAnswer:
        question = validate_question(question)
        started = time.perf_counter()
        request: dict[str, Any] = {
            "input": {"text": question},
            "retrieveAndGenerateConfiguration": {
                "type": "KNOWLEDGE_BASE",
                "knowledgeBaseConfiguration": {
                    "knowledgeBaseId": self._config.BEDROCK_KB_ID,
                    "modelArn": self._config.BEDROCK_MODEL_ARN,
                    "retrievalConfiguration": {
                        "vectorSearchConfiguration": {
                            "numberOfResults": self._config.BEDROCK_NUM_RESULTS,
                        },
                    },
                    "generationConfiguration": {
                        "promptTemplate": {
                            "textPromptTemplate": RAG_GENERATION_PROMPT,
                        },
                        "inferenceConfig": {
                            "textInferenceConfig": {
                                "temperature": 0.0,
                                "topP": 0.9,
                                "maxTokens": 1024,
                                "stopSequences": ["Action:", "GlobalDataSource"],
                            },
                        },
                    },
                },
            },
        }
        if session_id:
            request["sessionId"] = session_id
        try:
            response = self._client.retrieve_and_generate(**request)
        except Exception as exc:  # noqa: BLE001 — funneled through translate()
            log.exception("Bedrock retrieve_and_generate failed")
            raise translate(exc) from exc

        latency_ms = int((time.perf_counter() - started) * 1000)
        return _parse_response(response, latency_ms=latency_ms)


def _parse_response(response: dict[str, Any], *, latency_ms: int) -> RagAnswer:
    answer_text = (response.get("output", {}) or {}).get("text", "").strip()
    citations_raw = response.get("citations", []) or []

    parsed: list[Citation] = []
    for citation in citations_raw:
        for ref in citation.get("retrievedReferences", []) or []:
            snippet = (ref.get("content", {}) or {}).get("text", "").strip()
            location = ref.get("location", {}) or {}
            source_uri = (location.get("s3Location", {}) or {}).get("uri")
            if snippet:
                parsed.append(
                    Citation(
                        snippet=snippet,
                        source_uri=source_uri,
                        source_label=format_citation_label(source_uri),
                    ),
                )

    citations = _dedupe_citations(parsed)
    grounded = bool(citations)
    if not grounded and not answer_text:
        answer_text = "I could not find anything in the knowledge base for that question."

    matched = citations[0].source_label if citations else None
    return RagAnswer(
        answer=answer_text,
        citations=citations,
        session_id=response.get("sessionId"),
        grounded=grounded,
        latency_ms=latency_ms,
        matched_runbook=matched,
    )


def _dedupe_citations(citations: list[Citation]) -> list[Citation]:
    seen: set[tuple[str | None, str]] = set()
    unique: list[Citation] = []
    for citation in citations:
        key = (citation.source_uri, citation.snippet[:80])
        if key in seen:
            continue
        seen.add(key)
        unique.append(citation)
    return [
        Citation(
            snippet=c.snippet,
            source_uri=c.source_uri,
            source_label=c.source_label,
            index=idx,
        )
        for idx, c in enumerate(unique, start=1)
    ]
