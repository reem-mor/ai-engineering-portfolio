"""PITER AiOps enrichment tools — correlate, context, similar incidents."""
from __future__ import annotations

import csv
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from app.services import data_access
from app.services.incident_analysis import (
    _correlate_deployments as source_correlate_deployments,
    _find_service_owner,
    _find_similar_incidents as source_find_similar,
    _score_business_impact as source_score_impact,
)

_DEFAULT_SOURCE = data_access.source_data_dir()
_DATA_ROOT = Path(__file__).resolve().parents[1] / "data"
_AGENT_DATA = _DATA_ROOT / "agent_data"
_HISTORY = _DATA_ROOT / "sample_documents" / "incident_history.csv"


def _resolve_data_dir(data_dir: Path | None) -> Path:
    return data_dir or _DEFAULT_SOURCE


def _uses_source_catalog(data_dir: Path) -> bool:
    return (data_dir / "service_owners.csv").is_file()


def _parse_iso(ts: str) -> datetime:
    return datetime.fromisoformat(ts.replace("Z", "+00:00"))


def _load_catalog(data_dir: Path) -> dict[str, Any]:
    path = data_dir / "service_catalog.json"
    if path.is_file():
        return json.loads(path.read_text(encoding="utf-8"))
    services_path = _DATA_ROOT / "services.json"
    if services_path.is_file():
        raw = json.loads(services_path.read_text(encoding="utf-8"))
        services: list[dict[str, Any]] = []
        for item in raw.get("services", []):
            if not isinstance(item, dict):
                continue
            services.append(
                {
                    "name": item.get("service") or item.get("name"),
                    "owner": item.get("owner"),
                    "criticality": item.get("criticality"),
                    "dependencies": item.get("dependencies", []),
                    "sla": item.get("sla"),
                    "business_impact": item.get("business_impact"),
                    "escalation_team": item.get("escalation_team"),
                }
            )
        return {"services": services}
    raise FileNotFoundError(f"service_catalog.json not found under {data_dir}")


def _load_deploys_legacy(data_dir: Path) -> list[dict[str, str]]:
    path = data_dir / "deploys.csv"
    if path.is_file():
        with path.open(encoding="utf-8", newline="") as f:
            return list(csv.DictReader(f))
    alt = _DATA_ROOT / "deployments.csv"
    if alt.is_file():
        rows: list[dict[str, str]] = []
        with alt.open(encoding="utf-8", newline="") as f:
            for row in csv.DictReader(f):
                rows.append(
                    {
                        "deploy_id": row.get("deployment_id") or row.get("deploy_id", ""),
                        "service": row.get("service", ""),
                        "environment": row.get("environment", ""),
                        "version": row.get("version", ""),
                        "deployed_at": row.get("deployed_at", ""),
                        "deployed_by": row.get("owner", ""),
                        "change_summary": row.get("change_summary", ""),
                    }
                )
        return rows
    raise FileNotFoundError(f"deploys.csv not found under {data_dir}")


def _load_impact_legacy(data_dir: Path) -> list[dict[str, str]]:
    path = data_dir / "impact_matrix.csv"
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def _load_history(history_path: Path | None = None) -> list[dict[str, str]]:
    if history_path and history_path.is_file():
        with history_path.open(encoding="utf-8", newline="") as f:
            return list(csv.DictReader(f))
    try:
        return data_access.load_incident_history()
    except data_access.DataAccessError:
        pass
    try:
        return data_access.load_past_incidents()
    except data_access.DataAccessError:
        pass
    hist = _DATA_ROOT / "historical_incidents.csv"
    if hist.is_file():
        with hist.open(encoding="utf-8", newline="") as f:
            return list(csv.DictReader(f))
    return []


def _find_service_legacy(catalog: dict[str, Any], name: str) -> dict[str, Any] | None:
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
    """Find recent deploys for a service and its dependency hops near an alert."""
    base = _resolve_data_dir(data_dir)
    if _uses_source_catalog(base):
        owner = _find_service_owner(service, base)
        if owner:
            if window_minutes is not None:
                lookback_hours = max(1, window_minutes // 60)
            return source_correlate_deployments(
                service=service,
                environment=environment,
                alert_time=alert_time,
                dependencies=owner.get("dependencies", []),
                lookback_hours=lookback_hours,
                source_dir=base,
            )

    legacy_dir = _AGENT_DATA if base == _DEFAULT_SOURCE else base
    if not service or not service.strip():
        return {"error": "Missing service", "deployments": [], "likely_deploy_correlation": False}
    if not environment or not environment.strip():
        return {"error": "Missing environment", "deployments": [], "likely_deploy_correlation": False}
    catalog = _load_catalog(legacy_dir)
    deploys = _load_deploys_legacy(legacy_dir)
    svc = _find_service_legacy(catalog, service)
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
        "dependency_hop_explanation": (
            f"{service} depends on {sorted(depends_on) or 'nothing'} and is depended on by "
            f"{sorted(depended_by) or 'nothing'}; deploys to any hop can cause this alert."
        ),
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
    base = _resolve_data_dir(data_dir)
    if _uses_source_catalog(base):
        owner = _find_service_owner(service, base)
        if owner:
            env = environment.upper()
            return {
                "service": owner["service"],
                "environment": env,
                "owner_team": owner["owner_team"],
                "escalation_path": owner["escalation_path"],
                "pagerduty_service": owner["pagerduty_service"],
                "display_name": owner["display_name"],
            }

    legacy_dir = _AGENT_DATA if base == _DEFAULT_SOURCE else base
    catalog = _load_catalog(legacy_dir)
    svc = _find_service_legacy(catalog, service)
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
    environment: str = "",
    data_dir: Path | None = None,
) -> dict[str, Any]:
    """Return owner team, on-call, escalation chain, Slack channel and deps."""
    base = _resolve_data_dir(data_dir)
    if not service or not service.strip():
        return {"error": "Missing service"}

    if _uses_source_catalog(base):
        owner = _find_service_owner(service, base)
        if owner:
            return {
                "service": owner["service"],
                "display_name": owner["display_name"],
                "severity": (severity or "").upper(),
                "owner_team": owner["owner_team"],
                "primary_on_call": owner["primary_on_call"],
                "secondary_escalation": owner["secondary_on_call"],
                "slack_channel": owner["slack_channel"],
                "pagerduty_service": owner["pagerduty_service"],
                "escalation_path": owner["escalation_path"],
                "escalation_chain": owner["escalation_chain"],
                "dependencies": {
                    "depends_on": owner["dependencies"],
                    "depended_by": [],
                },
                "runbook": owner.get("runbook", ""),
                "dashboard": owner.get("dashboard", ""),
                "business_function": owner.get("business_function", ""),
                "service_tier": owner.get("service_tier", ""),
            }

    legacy_dir = _AGENT_DATA if base == _DEFAULT_SOURCE else base
    catalog = _load_catalog(legacy_dir)
    svc = _find_service_legacy(catalog, service)
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


_SEVERITY_RANK = {"P1": "critical", "P2": "high", "P3": "moderate", "P4": "low"}
_FALLBACK_REVENUE = {"P1": 200000, "P2": 80000, "P3": 12000, "P4": 2000}


def score_business_impact(
    *,
    service: str,
    environment: str,
    severity: str,
    duration_minutes: int = 60,
    alert: dict[str, Any] | None = None,
    data_dir: Path | None = None,
) -> dict[str, Any]:
    """Estimate incident cost and risk from business_impact.json or legacy matrix."""
    base = _resolve_data_dir(data_dir)
    try:
        duration = max(0, int(duration_minutes))
    except (TypeError, ValueError):
        duration = 60
    sev = severity.upper() if severity else ""

    if _uses_source_catalog(base):
        owner = _find_service_owner(service, base)
        if owner:
            impact = source_score_impact(
                service=service,
                severity=sev,
                alert=alert or {},
                source_dir=base,
            )
            revenue_per_hour = impact["revenue_impact_usd_per_hour"]
            cost_per_15min = round(revenue_per_hour / 4)
            estimated_total_cost = round(revenue_per_hour * (duration / 60))
            tier_str = owner.get("service_tier", "tier-2")
            tier = int(tier_str.replace("tier-", "")) if "tier-" in tier_str else 2
            return {
                **impact,
                "environment": environment.upper(),
                "duration_minutes": duration,
                "tier": tier,
                "cost_per_15min": cost_per_15min,
                "estimated_total_cost": estimated_total_cost,
                "regulatory_flag": impact.get("regulatory_risk") == "high",
                "escalation_minutes": 5 if sev == "P1" else 15 if sev == "P2" else 30,
                "fallback": False,
            }

    legacy_dir = _AGENT_DATA if base == _DEFAULT_SOURCE else base
    env = environment.upper() if environment else ""
    svc = service.lower() if service else ""
    rows = _load_impact_legacy(legacy_dir)
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
    data_dir: Path | None = None,
) -> dict[str, Any]:
    """Find past incidents similar to the current symptom for a service."""
    max_results = top_k if top_k is not None else limit
    max_results = max(1, int(max_results or 1))
    base = _resolve_data_dir(data_dir)

    if _uses_source_catalog(base) and _find_service_owner(service, base):
        result = source_find_similar(
            service=service,
            environment=environment,
            symptom=symptom,
            limit=max_results,
            source_dir=base,
        )
        return {
            "service": service,
            "symptom": symptom,
            "environment": environment.upper(),
            **result,
        }

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
                "date": r.get("date", r.get("start_time", "")),
                "severity": r["severity"],
                "environment": r.get("environment", ""),
                "root_cause": r["root_cause"],
                "resolution": r.get("resolution", ""),
                "mttr_minutes": int(r["mttr_minutes"]),
                "customer_impact": r.get("customer_impact", r.get("symptoms", "")),
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
    base = data_dir or (_AGENT_DATA if service == "postgres" else _DEFAULT_SOURCE)
    alert = {"affected_users": 0, "error_rate_pct": 0}
    return {
        "correlate_deployments": correlate_deployments(
            service=service,
            environment=environment,
            alert_time=alert_time,
            data_dir=base,
        ),
        "lookup_owner": lookup_owner(service=service, environment=environment, data_dir=base),
        "score_business_impact": score_business_impact(
            service=service,
            environment=environment,
            severity=severity,
            alert=alert,
            data_dir=base,
        ),
        "find_similar_incidents": find_similar_incidents(
            service=service, symptom=symptom, environment=environment, data_dir=base
        ),
    }
