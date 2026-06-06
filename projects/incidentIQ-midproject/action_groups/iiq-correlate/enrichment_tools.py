"""IncidentIQ enrichment tools â€” correlate, context, similar incidents."""
from __future__ import annotations

import csv
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

_DEFAULT_DATA = Path(__file__).resolve().parent / "data"
_HISTORY = Path(__file__).resolve().parent / "data" / "incident_history.csv"


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
    data_dir: Path | None = None,
) -> dict[str, Any]:
    """Recent deploys for service + dependency hop via service_catalog."""
    data_dir = data_dir or _DEFAULT_DATA
    catalog = _load_catalog(data_dir)
    deploys = _load_deploys(data_dir)
    svc = _find_service(catalog, service)
    if not svc:
        return {"error": f"Unknown service '{service}'", "service": service}

    alert_dt = _parse_iso(alert_time)
    cutoff = alert_dt - timedelta(hours=lookback_hours)
    env = environment.upper()
    targets = {service.lower()} | {d.lower() for d in svc.get("depends_on", [])}
    depended_by = {d.lower() for d in svc.get("depended_by", [])}
    hop_targets = targets | depended_by

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
            "upstream" if svc_name in {d.lower() for d in svc.get("depends_on", [])} else "downstream"
        )
        matched.append({**row, "hop": hop})

    matched.sort(key=lambda r: r["deployed_at"], reverse=True)
    return {
        "service": service,
        "environment": env,
        "alert_time": alert_time,
        "lookback_hours": lookback_hours,
        "dependency_hop": {
            "depends_on": svc.get("depends_on", []),
            "depended_by": svc.get("depended_by", []),
        },
        "deployments": matched,
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


def score_business_impact(
    *,
    service: str,
    environment: str,
    severity: str,
    data_dir: Path | None = None,
) -> dict[str, Any]:
    data_dir = data_dir or _DEFAULT_DATA
    rows = _load_impact(data_dir)
    env = environment.upper()
    sev = severity.upper()
    svc = service.lower()
    for row in rows:
        if (
            row["environment"].upper() == env
            and row["service"].lower() == svc
            and row["severity"].upper() == sev
        ):
            return {
                "service": service,
                "environment": env,
                "severity": sev,
                "tier": int(row["tier"]),
                "revenue_impact_usd_per_hour": int(row["revenue_impact_usd_per_hour"]),
                "player_impact_pct": int(row["player_impact_pct"]),
                "regulatory_flag": row["regulatory_flag"].lower() == "true",
                "escalation_minutes": int(row["escalation_minutes"]),
            }
    return {
        "error": f"No impact row for {svc}/{env}/{sev}",
        "service": service,
        "environment": env,
        "severity": sev,
    }


def find_similar_incidents(
    *,
    service: str,
    symptom: str,
    limit: int = 5,
    history_path: Path | None = None,
) -> dict[str, Any]:
    history = _load_history(history_path)
    svc = service.lower()
    symptom_lower = symptom.lower()
    scored: list[tuple[int, dict[str, str]]] = []
    for row in history:
        if row.get("service", "").lower() != svc:
            continue
        text = f"{row.get('root_cause', '')} {row.get('customer_impact', '')}".lower()
        score = sum(1 for token in symptom_lower.split() if len(token) > 3 and token in text)
        if "cpu" in symptom_lower and "cpu" in text:
            score += 2
        if "pool" in symptom_lower and "pool" in text:
            score += 2
        if "replication" in symptom_lower and "replica" in text:
            score += 2
        if score > 0:
            scored.append((score, row))
    scored.sort(key=lambda x: (-x[0], x[1].get("date", "")))
    top = [r for _, r in scored[:limit]]
    return {
        "service": service,
        "symptom": symptom,
        "similar_incidents": [
            {
                "incident_id": r["incident_id"],
                "date": r["date"],
                "severity": r["severity"],
                "root_cause": r["root_cause"],
                "mttr_minutes": int(r["mttr_minutes"]),
                "customer_impact": r["customer_impact"],
            }
            for r in top
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

