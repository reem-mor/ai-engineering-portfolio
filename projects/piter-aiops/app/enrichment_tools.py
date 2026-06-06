"""IncidentIQ enrichment tools — correlate, context, similar incidents."""
from __future__ import annotations

import csv
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

_DEFAULT_DATA = Path(__file__).resolve().parents[1] / "data" / "agent_data"
_HISTORY = Path(__file__).resolve().parents[1] / "data" / "sample_documents" / "incident_history.csv"


def _parse_iso(ts: str) -> datetime:
    return datetime.fromisoformat(ts.replace("Z", "+00:00"))


def _load_catalog(data_dir: Path) -> dict[str, Any]:
    path = data_dir / "service_catalog.json"
    return json.loads(path.read_text(encoding="utf-8"))


def _load_deploys(data_dir: Path) -> list[dict[str, str]]:
    path = data_dir / "deploys.csv"
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def _load_impact(data_dir: Path) -> list[dict[str, str]]:
    path = data_dir / "impact_matrix.csv"
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def _load_history(history_path: Path | None = None) -> list[dict[str, str]]:
    path = history_path or _HISTORY
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def _find_service(catalog: dict[str, Any], name: str) -> dict[str, Any] | None:
    name = name.strip().lower()
    for svc in catalog.get("services", []):
        if svc.get("name", "").lower() == name:
            return svc
    return None


def correlate_deployments(
    *,
    service: str,
    environment: str,
    alert_time: str,
    lookback_hours: int = 6,
    window_minutes: int | None = None,
    data_dir: Path | None = None,
) -> dict[str, Any]:
    """Find recent deploys for a service and its dependency hops near an alert.

    Args:
        service: Affected service name (matched against the service catalog).
        environment: Environment code, e.g. ``NJ-DGE`` (case-insensitive).
        alert_time: ISO-8601 alert timestamp.
        lookback_hours: Default lookback window (used when ``window_minutes`` is None).
        window_minutes: Optional explicit lookback window in minutes (spec input);
            overrides ``lookback_hours`` when provided.
        data_dir: Override the data directory (tests).

    Returns:
        A structured dict with matching ``deployments``, the most likely
        ``suspect_deployment``, a human ``reason``, and a
        ``dependency_hop_explanation``. On a bad input it returns an ``error``
        key instead of raising, so callers never crash.
    """
    data_dir = data_dir or _DEFAULT_DATA
    if not service or not service.strip():
        return {"error": "Missing service", "deployments": [], "likely_deploy_correlation": False}
    if not environment or not environment.strip():
        return {"error": "Missing environment", "deployments": [], "likely_deploy_correlation": False}
    catalog = _load_catalog(data_dir)
    deploys = _load_deploys(data_dir)
    svc = _find_service(catalog, service)
    if not svc:
        return {
            "error": f"Unknown service '{service}'",
            "service": service,
            "deployments": [],
            "likely_deploy_correlation": False,
        }

    try:
        alert_dt = _parse_iso(alert_time)
    except (ValueError, AttributeError):
        return {
            "error": f"Invalid alert_time '{alert_time}'",
            "service": service,
            "deployments": [],
            "likely_deploy_correlation": False,
        }

    if window_minutes is not None:
        cutoff = alert_dt - timedelta(minutes=window_minutes)
    else:
        cutoff = alert_dt - timedelta(hours=lookback_hours)
    env = environment.upper()
    depends_on = {d.lower() for d in svc.get("depends_on", [])}
    depended_by = {d.lower() for d in svc.get("depended_by", [])}
    hop_targets = {service.lower()} | depends_on | depended_by

    matched: list[dict[str, Any]] = []
    for row in deploys:
        if row["environment"].upper() != env:
            continue
        deployed_at = _parse_iso(row["deployed_at"])
        if deployed_at < cutoff or deployed_at > alert_dt + timedelta(minutes=30):
            continue
        svc_name = row["service"].lower()
        if svc_name not in hop_targets:
            continue
        hop = "direct" if svc_name == service.lower() else (
            "upstream" if svc_name in depends_on else "downstream"
        )
        matched.append({**row, "hop": hop})

    matched.sort(key=lambda r: r["deployed_at"], reverse=True)

    suspect = matched[0] if matched else None
    if suspect:
        reason = (
            f"{suspect['service']} {suspect['version']} deployed at "
            f"{suspect['deployed_at']} ({suspect['hop']} hop) is the closest deploy "
            f"before the alert — '{suspect['change_summary']}'."
        )
    else:
        reason = "No deployments to the service or its dependencies inside the window."
    hop_explanation = (
        f"{service} depends on {sorted(depends_on) or 'nothing'} and is depended on by "
        f"{sorted(depended_by) or 'nothing'}; deploys to any hop can cause this alert."
    )

    return {
        "service": service,
        "environment": env,
        "alert_time": alert_time,
        "lookback_hours": lookback_hours,
        "window_minutes": window_minutes,
        "dependency_hop": {
            "depends_on": svc.get("depends_on", []),
            "depended_by": svc.get("depended_by", []),
        },
        "dependency_hop_explanation": hop_explanation,
        "deployments": matched,
        "suspect_deployment": suspect,
        "reason": reason,
        "likely_deploy_correlation": len(matched) > 0,
    }


def lookup_owner(
    *,
    service: str,
    environment: str,
    data_dir: Path | None = None,
) -> dict[str, Any]:
    data_dir = data_dir or _DEFAULT_DATA
    catalog = _load_catalog(data_dir)
    svc = _find_service(catalog, service)
    if not svc:
        return {"error": f"Unknown service '{service}'"}
    env = environment.upper()
    if env not in [e.upper() for e in svc.get("environments", [])]:
        return {
            "warning": f"Service '{service}' not listed for environment '{env}'",
            **{k: svc.get(k) for k in ("name", "owner_team", "escalation_path", "pagerduty_service")},
        }
    return {
        "service": svc["name"],
        "environment": env,
        "owner_team": svc["owner_team"],
        "escalation_path": svc["escalation_path"],
        "pagerduty_service": svc["pagerduty_service"],
        "display_name": svc.get("display_name", svc["name"]),
    }


def lookup_owner_and_escalation(
    *,
    service: str,
    severity: str = "",
    data_dir: Path | None = None,
) -> dict[str, Any]:
    """Return owner team, on-call, escalation chain, Slack channel and deps.

    Args:
        service: Service name to look up in the catalog.
        severity: Optional incident severity (used to surface urgency hints).
        data_dir: Override the data directory (tests).

    Returns:
        A structured dict with ``owner_team``, ``primary_on_call``,
        ``secondary_escalation``, ``slack_channel``, ``escalation_chain``, and
        ``dependencies``. On an unknown service it returns an ``error`` key.
    """
    data_dir = data_dir or _DEFAULT_DATA
    if not service or not service.strip():
        return {"error": "Missing service"}
    catalog = _load_catalog(data_dir)
    svc = _find_service(catalog, service)
    if not svc:
        return {"error": f"Unknown service '{service}'", "service": service}

    chain = [part.strip() for part in svc.get("escalation_path", "").split("->") if part.strip()]
    return {
        "service": svc["name"],
        "display_name": svc.get("display_name", svc["name"]),
        "severity": (severity or "").upper(),
        "owner_team": svc.get("owner_team", ""),
        "primary_on_call": svc.get("on_call", ""),
        "secondary_escalation": svc.get("secondary_oncall", ""),
        "slack_channel": svc.get("slack_channel", ""),
        "pagerduty_service": svc.get("pagerduty_service", ""),
        "escalation_path": svc.get("escalation_path", ""),
        "escalation_chain": chain,
        "dependencies": {
            "depends_on": svc.get("depends_on", []),
            "depended_by": svc.get("depended_by", []),
        },
    }


# Severity-based SLA risk ranking for the business-impact fallback.
_SEVERITY_RANK = {"P1": "critical", "P2": "high", "P3": "moderate", "P4": "low"}
_FALLBACK_REVENUE = {"P1": 200000, "P2": 80000, "P3": 12000, "P4": 2000}


def score_business_impact(
    *,
    service: str,
    environment: str,
    severity: str,
    duration_minutes: int = 60,
    data_dir: Path | None = None,
) -> dict[str, Any]:
    """Estimate incident cost and risk from the impact matrix.

    Args:
        service: Affected service.
        environment: Environment code (case-insensitive).
        severity: Incident severity, e.g. ``P2``.
        duration_minutes: Incident duration so far (drives total-cost estimate).
        data_dir: Override the data directory (tests).

    Returns:
        A structured dict with ``revenue_impact_usd_per_hour``,
        ``cost_per_15min``, ``estimated_total_cost``, ``sla_risk``,
        ``regulatory_risk``, and a ``business_explanation``. When no matrix row
        matches, returns a conservative ``fallback`` estimate instead of failing.
    """
    data_dir = data_dir or _DEFAULT_DATA
    try:
        duration = max(0, int(duration_minutes))
    except (TypeError, ValueError):
        duration = 60
    env = environment.upper() if environment else ""
    sev = severity.upper() if severity else ""
    svc = service.lower() if service else ""

    rows = _load_impact(data_dir)
    matched_row: dict[str, str] | None = None
    for row in rows:
        if (
            row["environment"].upper() == env
            and row["service"].lower() == svc
            and row["severity"].upper() == sev
        ):
            matched_row = row
            break

    if matched_row is not None:
        revenue_per_hour = int(matched_row["revenue_impact_usd_per_hour"])
        regulatory = matched_row["regulatory_flag"].lower() == "true"
        tier = int(matched_row["tier"])
        player_impact = int(matched_row["player_impact_pct"])
        escalation_minutes = int(matched_row["escalation_minutes"])
        fallback = False
    else:
        revenue_per_hour = _FALLBACK_REVENUE.get(sev, 5000)
        regulatory = sev in {"P1", "P2"} and env.startswith("NJ")
        tier = 1 if sev == "P1" else 2 if sev == "P2" else 3
        player_impact = 0
        escalation_minutes = 30
        fallback = True

    cost_per_15min = round(revenue_per_hour / 4)
    estimated_total_cost = round(revenue_per_hour * (duration / 60))
    sla_risk = _SEVERITY_RANK.get(sev, "unknown")
    regulatory_risk = "high" if regulatory else "low"
    note = " (fallback estimate; no exact matrix row)" if fallback else ""
    explanation = (
        f"{sev or 'severity?'} on {service or 'service?'} in {env or 'env?'} costs about "
        f"${revenue_per_hour:,}/hour (~${cost_per_15min:,} per 15 min). After {duration} min "
        f"the estimated impact is ${estimated_total_cost:,}. SLA risk {sla_risk}, "
        f"regulatory risk {regulatory_risk}{note}."
    )

    return {
        "service": service,
        "environment": env,
        "severity": sev,
        "duration_minutes": duration,
        "tier": tier,
        "revenue_impact_usd_per_hour": revenue_per_hour,
        "cost_per_15min": cost_per_15min,
        "estimated_total_cost": estimated_total_cost,
        "player_impact_pct": player_impact,
        "regulatory_flag": regulatory,
        "regulatory_risk": regulatory_risk,
        "sla_risk": sla_risk,
        "escalation_minutes": escalation_minutes,
        "fallback": fallback,
        "business_explanation": explanation,
    }


def find_similar_incidents(
    *,
    service: str,
    symptom: str,
    environment: str = "",
    limit: int = 5,
    top_k: int | None = None,
    history_path: Path | None = None,
) -> dict[str, Any]:
    """Find past incidents similar to the current symptom for a service.

    Args:
        service: Affected service (matched case-insensitively, prefix-aware so
            ``postgres`` also matches ``postgres-primary``/``postgres-replica``).
        symptom: Free-text symptom / description to match against root causes.
        environment: Optional environment filter (e.g. ``NJ-DGE``).
        limit: Max results (kept for backward compatibility).
        top_k: Spec alias for ``limit``; overrides ``limit`` when provided.
        history_path: Override the history CSV path (tests).

    Returns:
        A structured dict with ``similar_incidents`` (each carrying
        ``root_cause``, ``resolution``, ``mttr_minutes`` and a
        ``similarity_reason``) and a ``count``.
    """
    max_results = top_k if top_k is not None else limit
    max_results = max(1, int(max_results or 1))
    history = _load_history(history_path)
    svc = (service or "").lower()
    env = (environment or "").upper()
    symptom_lower = (symptom or "").lower()
    symptom_tokens = [t for t in symptom_lower.split() if len(t) > 3]

    scored: list[tuple[int, list[str], dict[str, str]]] = []
    for row in history:
        row_service = row.get("service", "").lower()
        if not (row_service == svc or row_service.startswith(f"{svc}-") or svc.startswith(f"{row_service}-")):
            continue
        if env and row.get("environment", "").upper() != env:
            continue
        text = f"{row.get('root_cause', '')} {row.get('customer_impact', '')}".lower()
        reasons: list[str] = []
        score = 0
        shared = [tok for tok in symptom_tokens if tok in text]
        if shared:
            score += len(shared)
            reasons.append("shared terms: " + ", ".join(sorted(set(shared))))
        for keyword, hint in (("cpu", "cpu"), ("pool", "pool"), ("replica", "replic"), ("lag", "lag")):
            if keyword in symptom_lower and hint in text:
                score += 2
                reasons.append(f"both involve {keyword}")
        if score > 0:
            scored.append((score, reasons, row))

    scored.sort(key=lambda x: (-x[0], x[2].get("date", "")), reverse=False)
    top = scored[:max_results]
    return {
        "service": service,
        "symptom": symptom,
        "environment": env,
        "similar_incidents": [
            {
                "incident_id": r["incident_id"],
                "date": r["date"],
                "severity": r["severity"],
                "environment": r.get("environment", ""),
                "root_cause": r["root_cause"],
                "resolution": r.get("resolution", ""),
                "mttr_minutes": int(r["mttr_minutes"]),
                "customer_impact": r["customer_impact"],
                "similarity_reason": "; ".join(reasons) or "same service",
            }
            for _score, reasons, r in top
        ],
        "count": len(top),
    }


def enrich_triage_demo(
    *,
    service: str = "postgres",
    environment: str = "NJ-DGE",
    severity: str = "P2",
    symptom: str = "CPU > 90%",
    alert_time: str = "2026-06-10T09:00:00Z",
    data_dir: Path | None = None,
) -> dict[str, Any]:
    """Full enrichment bundle for the grading demo scenario."""
    data_dir = data_dir or _DEFAULT_DATA
    return {
        "correlate_deployments": correlate_deployments(
            service=service,
            environment=environment,
            alert_time=alert_time,
            data_dir=data_dir,
        ),
        "lookup_owner": lookup_owner(service=service, environment=environment, data_dir=data_dir),
        "score_business_impact": score_business_impact(
            service=service,
            environment=environment,
            severity=severity,
            data_dir=data_dir,
        ),
        "find_similar_incidents": find_similar_incidents(service=service, symptom=symptom),
    }
