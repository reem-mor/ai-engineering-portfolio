"""Incident triage orchestration: RAG + 4 tools + session memory.

Backend-agnostic: callers pass an ``ask_fn(question) -> RagAnswer`` so the same
orchestration drives both the local offline client and the Bedrock client (with
fallback handled by the caller). The output matches the IncidentIQ triage card
JSON contract.
"""
from __future__ import annotations

from typing import Any, Callable

from app.bedrock_client import RagAnswer
from app.services import session_memory
from app.services.local_rag import _first_excerpt_steps
from app.services.tool_router import decide_tools, run_plan
from app.text_utils import parse_action_bullets

AskFn = Callable[[str], RagAnswer]

DEMO_ALERT: dict[str, Any] = {
    "alert_id": "ALERT-DEMO-PG-CPU",
    "service": "postgres",
    "environment": "NJ-DGE",
    "severity": "P2",
    "symptom": "Postgres CPU is 95% on prod-db-1",
    "description": "Postgres CPU is 95% on prod-db-1",
    "alert_time": "2026-06-10T09:00:00Z",
    "duration_minutes": 45,
}


def build_triage_question(alert: dict[str, Any]) -> str:
    """Build the retrieval query sent to the RAG backend.

    Symptom-focused on purpose: we avoid boilerplate words ("runbook",
    "severity") that appear across the whole corpus, so an off-topic alert stays
    below the relevance threshold and is refused instead of falsely grounded.
    """
    symptom = str(alert.get("symptom") or alert.get("description") or "").strip()
    service = str(alert.get("service", "")).strip()
    pieces = [symptom or "incident"]
    if service:
        pieces.append(service)
    return " ".join(pieces).strip()


def _citations_payload(rag: RagAnswer) -> list[dict[str, Any]]:
    return [
        {
            "document": c.source_label,
            "excerpt": c.snippet,
            "score": c.score,
        }
        for c in rag.citations
    ]


def _recommended_steps(rag: RagAnswer) -> list[str]:
    """Best-effort recommended steps: prefer the answer, then richest citation."""
    steps = parse_action_bullets(rag.answer)
    if len(steps) >= 2:
        return steps[:8]
    # Scan retrieved chunks for the richest numbered/bulleted step list.
    best: list[str] = steps
    for citation in rag.citations:
        candidate = _first_excerpt_steps(citation.snippet)
        if len(candidate) > len(best):
            best = candidate
    return best[:8]


def run_triage(
    alert: dict[str, Any],
    *,
    ask_fn: AskFn,
    session_id: str | None = None,
) -> dict[str, Any]:
    """Run full triage: retrieve runbook, run 4 tools, compose one triage card."""
    sid = session_memory.create_session(alert, session_id=session_id)
    question = build_triage_question(alert)
    rag = ask_fn(question)

    tool_outputs = run_plan(decide_tools(alert))
    correlate = tool_outputs.get("correlate_deployments", {})
    owner = tool_outputs.get("lookup_owner_and_escalation", {})
    impact = tool_outputs.get("score_business_impact", {})
    similar = tool_outputs.get("find_similar_incidents", {})

    citations = _citations_payload(rag)
    suspect_deploys = correlate.get("deployments", []) if isinstance(correlate, dict) else []

    card: dict[str, Any] = {
        "answer": rag.answer,
        "citations": citations,
        "recommended_steps": _recommended_steps(rag),
        "suspect_deploys": suspect_deploys,
        "suspect_deployment": correlate.get("suspect_deployment") if isinstance(correlate, dict) else None,
        "owner": owner,
        "impact": impact,
        "similar_incidents": similar.get("similar_incidents", []) if isinstance(similar, dict) else [],
        "grounded": rag.grounded,
        "matched_runbook": rag.matched_runbook,
        "session_id": sid,
        "memory_used": False,
        "mode": rag.mode,
        "alert": alert,
    }

    session_memory.save_triage(
        sid,
        citations=citations,
        tool_outputs=tool_outputs,
        triage_card=card,
    )
    return card


def _classify_followup(question: str) -> str:
    q = question.lower()
    if any(k in q for k in ("escalate", "who do i", "owner", "on-call", "on call", "contact")):
        return "owner"
    if any(k in q for k in ("deploy", "deployment", "rollback", "cause", "what caused")):
        return "deploy"
    if any(k in q for k in ("sql", "command", "query", "show me")):
        return "sql"
    if any(k in q for k in ("impact", "cost", "revenue", "business", "sla", "regulatory")):
        return "impact"
    if any(k in q for k in ("summarize", "summary", "recap", "tl;dr")):
        return "summary"
    return "general"


def run_follow_up(
    session_id: str,
    question: str,
    *,
    ask_fn: AskFn,
) -> dict[str, Any] | None:
    """Answer a follow-up using stored session memory; re-run RAG only if needed.

    Returns ``None`` when the session is unknown so the caller can return 404.
    """
    session = session_memory.get_session(session_id)
    if session is None:
        return None

    tools = session.get("tool_outputs", {}) or {}
    card = session.get("triage_card", {}) or {}
    kind = _classify_followup(question)
    memory_used = True
    mode = card.get("mode", "local")

    if kind == "owner":
        owner = tools.get("lookup_owner_and_escalation", {})
        chain = " -> ".join(owner.get("escalation_chain", [])) or owner.get("escalation_path", "")
        answer = (
            f"Escalate to {owner.get('primary_on_call', 'the on-call')} "
            f"(team {owner.get('owner_team', 'n/a')}, Slack {owner.get('slack_channel', 'n/a')}). "
            f"Escalation chain: {chain}. Secondary: {owner.get('secondary_escalation', 'n/a')}."
        )
        payload = {"answer": answer, "owner": owner}
    elif kind == "deploy":
        correlate = tools.get("correlate_deployments", {})
        suspect = correlate.get("suspect_deployment")
        answer = correlate.get("reason", "No suspect deployment found in the window.")
        payload = {"answer": answer, "suspect_deployment": suspect, "suspect_deploys": correlate.get("deployments", [])}
    elif kind == "impact":
        impact = tools.get("score_business_impact", {})
        answer = impact.get("business_explanation", "No business impact estimate available.")
        payload = {"answer": answer, "impact": impact}
    elif kind == "summary":
        owner = tools.get("lookup_owner_and_escalation", {})
        impact = tools.get("score_business_impact", {})
        answer = (
            f"Runbook: {card.get('matched_runbook', 'n/a')}. "
            f"Owner: {owner.get('owner_team', 'n/a')} ({owner.get('primary_on_call', 'n/a')}). "
            f"Impact: {impact.get('sla_risk', 'n/a')} SLA risk, "
            f"~${impact.get('estimated_total_cost', 0):,} so far. "
            f"{len(card.get('recommended_steps', []))} recommended steps."
        )
        payload = {"answer": answer, "summary_of": card.get("matched_runbook")}
    else:
        # "sql" and "general" re-query the knowledge base for fresh grounded text.
        memory_used = False
        rag = ask_fn(question)
        mode = rag.mode
        payload = {
            "answer": rag.answer,
            "citations": _citations_payload(rag),
            "grounded": rag.grounded,
        }

    result = {
        **payload,
        "session_id": session_id,
        "memory_used": memory_used,
        "mode": mode,
        "kind": kind,
    }
    session_memory.append_followup(session_id, question, result)
    return result
