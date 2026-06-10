"""Build a single structured analysis view for API responses and UI rendering."""
from __future__ import annotations

import re
from typing import Any

_MD_BOLD = re.compile(r"\*\*(.+?)\*\*")
_MD_ITALIC = re.compile(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)")
_MD_HEADING = re.compile(r"^#{1,6}\s+", re.MULTILINE)
_MD_BULLET = re.compile(r"^[-*•]\s+", re.MULTILINE)
_MD_NUMBERED = re.compile(r"^\d+\.\s+", re.MULTILINE)


def strip_markdown(text: str | None) -> str:
    """Remove common markdown markers for plain UI text."""
    if not text:
        return ""
    cleaned = str(text).strip()
    cleaned = _MD_HEADING.sub("", cleaned)
    cleaned = _MD_BOLD.sub(r"\1", cleaned)
    cleaned = _MD_ITALIC.sub(r"\1", cleaned)
    cleaned = _MD_BULLET.sub("", cleaned)
    cleaned = _MD_NUMBERED.sub("", cleaned)
    return cleaned.strip()


def _split_text_items(text: str | None) -> list[str]:
    if not text:
        return []
    items: list[str] = []
    for raw in re.split(r"\n+", str(text)):
        line = strip_markdown(raw)
        if line:
            items.append(line)
    if len(items) <= 1 and text and len(text) > 180:
        for part in re.split(r"(?<=[.!?])\s+(?=[A-Z*])", str(text)):
            chunk = strip_markdown(part)
            if chunk and len(chunk) > 12:
                items.append(chunk)
    return items


def _normalize_steps(steps: Any) -> list[str]:
    if not steps:
        return []
    if isinstance(steps, str):
        return _split_text_items(steps)
    if not isinstance(steps, list):
        return []
    out: list[str] = []
    for step in steps:
        if isinstance(step, str):
            out.extend(_split_text_items(step) if "\n" in step else [strip_markdown(step)])
        elif step:
            out.append(strip_markdown(str(step)))
    return [s for s in out if s]


def _similar_rows(payload: dict[str, Any]) -> list[dict[str, Any]]:
    raw = payload.get("similar_incidents") or []
    if not isinstance(raw, list):
        return []
    rows: list[dict[str, Any]] = []
    for item in raw[:8]:
        if not isinstance(item, dict):
            continue
        rows.append(
            {
                "incident_id": str(item.get("incident_id") or item.get("id") or ""),
                "service": str(item.get("service") or ""),
                "summary": strip_markdown(
                    str(item.get("summary") or item.get("symptom") or item.get("title") or item.get("root_cause") or "")
                ),
                "mttr_minutes": item.get("mttr_minutes"),
            }
        )
    return [r for r in rows if r.get("incident_id") or r.get("summary")]


def _correlation_chain(payload: dict[str, Any]) -> list[dict[str, str]]:
    chain: list[dict[str, str]] = []
    dep = payload.get("suspect_deployment")
    alert = payload.get("alert") if isinstance(payload.get("alert"), dict) else {}
    similar = _similar_rows(payload)

    if isinstance(dep, dict) and dep:
        version = str(dep.get("version") or "").strip()
        service = str(dep.get("service") or alert.get("service") or "").strip()
        ts = str(dep.get("deployed_at") or dep.get("timestamp") or "").strip()
        detail = strip_markdown(str(dep.get("change_summary") or dep.get("summary") or ""))
        label = f"{service} {version}".strip() if version else service
        chain.append(
            {
                "step": "deployment",
                "label": label or "Recent deployment",
                "timestamp": ts,
                "detail": detail or "Suspect deployment correlated to alert window",
            }
        )

    if alert:
        service = str(alert.get("service") or "").strip()
        env = str(alert.get("environment") or "").strip()
        symptom = strip_markdown(
            str(alert.get("symptom") or alert.get("title") or alert.get("description") or "")
        )
        chain.append(
            {
                "step": "alert",
                "label": f"{service} · {env}".strip(" ·") or "Active alert",
                "timestamp": str(alert.get("alert_time") or alert.get("timestamp") or ""),
                "detail": symptom or "Alert triggered investigation",
            }
        )

    if similar:
        first = similar[0]
        chain.append(
            {
                "step": "similar_incident",
                "label": str(first.get("incident_id") or "Similar incident"),
                "timestamp": "",
                "detail": str(first.get("summary") or "Historical match from past incidents"),
            }
        )

    return chain


def _evidence(payload: dict[str, Any]) -> list[str]:
    evidence: list[str] = []
    alert = payload.get("alert") if isinstance(payload.get("alert"), dict) else {}
    if alert:
        svc = str(alert.get("service") or "").strip()
        env = str(alert.get("environment") or "").strip()
        if svc or env:
            evidence.append(f"Alert evidence: {svc} · {env}".strip(" ·"))

    runbook = str(payload.get("matched_runbook") or "").strip()
    if runbook:
        evidence.append(f"Matched runbook: {runbook}")

    dep = payload.get("suspect_deployment")
    if isinstance(dep, dict) and dep.get("version"):
        evidence.append(
            f"Deployment {dep.get('service')} {dep.get('version')} at {dep.get('deployed_at') or dep.get('timestamp') or 'recent window'}"
        )

    piter = payload.get("piter") if isinstance(payload.get("piter"), dict) else {}
    investigation = _split_text_items(piter.get("investigation") if piter else None)
    evidence.extend(investigation[:4])

    sources = payload.get("sources") or []
    if isinstance(sources, list):
        for src in sources[:3]:
            evidence.append(strip_markdown(str(src)))

    deduped: list[str] = []
    seen: set[str] = set()
    for item in evidence:
        key = item.lower()
        if key and key not in seen:
            seen.add(key)
            deduped.append(item)
    return deduped


def _escalation_suggestion(payload: dict[str, Any]) -> dict[str, Any]:
    owner = payload.get("owner") if isinstance(payload.get("owner"), dict) else {}
    policy = payload.get("escalation_policy") if isinstance(payload.get("escalation_policy"), dict) else {}
    piter = payload.get("piter") if isinstance(payload.get("piter"), dict) else {}
    notify = policy.get("notify")
    path = owner.get("escalation_path") or owner.get("escalation_chain")
    if isinstance(path, list):
        path_text = " → ".join(str(x) for x in path if x)
    else:
        path_text = str(path or "")
    if isinstance(notify, list) and notify:
        path_text = " → ".join(str(x) for x in notify if x)
    return {
        "owner_team": str(owner.get("owner_team") or owner.get("owner_team") or ""),
        "primary_oncall": str(owner.get("primary_oncall") or owner.get("primary_on_call") or ""),
        "escalation_path": strip_markdown(path_text),
        "requires_escalation": bool(payload.get("requires_escalation")),
        "summary": strip_markdown(str(piter.get("escalation") or policy.get("summary") or path_text)),
    }


def build_structured_analysis(payload: dict[str, Any]) -> dict[str, Any]:
    """Normalize triage/chat payloads into the structured analysis contract."""
    piter = payload.get("piter") if isinstance(payload.get("piter"), dict) else {}
    severity = str(payload.get("priority") or piter.get("priority") or "P3").strip()
    summary = strip_markdown(
        str(payload.get("business_impact") or piter.get("investigation") or payload.get("answer") or "")[:500]
    )
    recommended = _normalize_steps(payload.get("recommended_steps"))
    if not recommended:
        recommended = _normalize_steps(piter.get("triage"))

    return {
        "severity": severity,
        "summary": summary,
        "correlation_chain": _correlation_chain(payload),
        "evidence": _evidence(payload),
        "similar_incidents": _similar_rows(payload),
        "recommended_actions": recommended[:12],
        "escalation_suggestion": _escalation_suggestion(payload),
    }
