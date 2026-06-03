"""boto3 wrapper for Amazon Bedrock Agents invoke_agent (KB-backed)."""
from __future__ import annotations

import logging
import time
import uuid
from typing import Any

import boto3
from botocore.config import Config as BotoConfig
from botocore.exceptions import EventStreamError

from app.bedrock_client import Citation, RagAnswer, _dedupe_citations
from app.config import Config
from app.errors import translate
from app.text_utils import extract_reference_metadata, format_citation_label, format_citation_preview
from app.validators import validate_question

log = logging.getLogger(__name__)

AGENT_INSTRUCTION = """You are IncidentIQ, an NOC assistant for on-call engineers.

Use your linked knowledge base for runbooks, postmortems, escalation policies, and
historical incident patterns.

Use the incidentiq-ops action group for live operational data:
- Environment health status (getEnvironmentStatus)
- Recent alerts for an environment (getRecentAlerts)
- Creating incident tickets (createIncident)

Before calling createIncident (POST /incidents), confirm title, severity, and environment
with the user. Never open a ticket without explicit user approval.

Write plain English in your final response. Do NOT emit raw tool calls, JSON, or lines
starting with "Action:" in the user-facing answer.

Use exactly this structure:

Summary:
One short sentence answering the question.

Recommended steps:
1. First concrete action
2. Second action
(continue numbering as needed)

Escalation:
- When to escalate
- Who to escalate to

Why this answer:
One line citing the runbook, live ops data, alert history, or postmortem that supports
the answer.

If neither the knowledge base nor ops tools have relevant data, say so clearly and
recommend escalating with prepared notes. Do not invent runbook steps or live metrics.
"""


class BedrockAgentClient:
    """Question in via invoke_agent; grounded answer + citations out."""

    def __init__(self, config: Config, *, client: Any | None = None) -> None:
        self._config = config
        boto_cfg = BotoConfig(
            read_timeout=120,
            connect_timeout=10,
            retries={"max_attempts": 3, "mode": "standard"},
        )
        self._client = client or boto3.client(
            "bedrock-agent-runtime",
            region_name=config.AWS_REGION,
            config=boto_cfg,
        )

    def ask(self, question: str, *, session_id: str | None = None) -> RagAnswer:
        question = validate_question(question)
        started = time.perf_counter()
        request: dict[str, Any] = {
            "agentId": self._config.BEDROCK_AGENT_ID,
            "agentAliasId": self._config.BEDROCK_AGENT_ALIAS_ID,
            "inputText": question,
            "sessionId": session_id or str(uuid.uuid4()),
            "enableTrace": True,
        }
        try:
            response = self._client.invoke_agent(**request)
        except Exception as exc:  # noqa: BLE001
            log.exception("Bedrock invoke_agent failed")
            raise translate(exc) from exc

        answer_parts: list[str] = []
        citations_raw: list[dict[str, Any]] = []
        out_session_id = response.get("sessionId")

        try:
            for event in response.get("completion", []):
                chunk = event.get("chunk")
                if chunk:
                    raw_bytes = chunk.get("bytes")
                    if raw_bytes:
                        answer_parts.append(raw_bytes.decode("utf-8"))
                    attribution = chunk.get("attribution") or {}
                    for citation in attribution.get("citations", []) or []:
                        for ref in citation.get("retrievedReferences", []) or []:
                            citations_raw.append(ref)

                trace = event.get("trace") or {}
                orch = trace.get("trace", {}).get("orchestrationTrace") or trace.get(
                    "orchestrationTrace"
                )
                if orch:
                    observation = orch.get("observation") or {}
                    kb_out = observation.get("knowledgeBaseLookupOutput") or {}
                    for ref in kb_out.get("retrievedReferences", []) or []:
                        citations_raw.append(ref)
        except EventStreamError as exc:
            log.exception("Bedrock invoke_agent stream failed")
            raise translate(exc) from exc

        latency_ms = int((time.perf_counter() - started) * 1000)
        answer_text = "".join(answer_parts).strip()
        citations = _parse_references(citations_raw)
        grounded = bool(citations)
        if not grounded and not answer_text:
            answer_text = "I could not find anything in the knowledge base for that question."

        matched = citations[0].source_label if citations else None
        return RagAnswer(
            answer=answer_text,
            citations=citations,
            session_id=out_session_id,
            grounded=grounded,
            latency_ms=latency_ms,
            matched_runbook=matched,
        )


def _parse_references(refs: list[dict[str, Any]]) -> list[Citation]:
    parsed: list[Citation] = []
    for ref in refs:
        snippet = (ref.get("content", {}) or {}).get("text", "").strip()
        if not snippet:
            continue
        location = ref.get("location", {}) or {}
        source_uri = (location.get("s3Location", {}) or {}).get("uri")
        label = format_citation_label(source_uri)
        score, chunk_index = extract_reference_metadata(ref)
        parsed.append(
            Citation(
                snippet=snippet,
                source_uri=source_uri,
                source_label=label,
                score=score,
                chunk_index=chunk_index,
                preview=format_citation_preview(snippet, label),
            ),
        )
    return _dedupe_citations(parsed)
