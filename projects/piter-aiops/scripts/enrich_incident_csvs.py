#!/usr/bin/env python3
"""Add SRE post-mortem columns to incident CSV corpora."""
from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

ESCALATION = {
    "P1": "NOC → Platform SRE → Service owner → Incident commander → Exec comms",
    "P2": "NOC → Platform SRE → Service owner",
    "P3": "NOC → Service owner (next business day review)",
    "P4": "Auto-resolve / noise bucket — no escalation",
}


def _escalation(severity: str) -> str:
    return ESCALATION.get(severity.upper(), ESCALATION["P3"])


def enrich_past_incidents(path: Path) -> None:
    if not path.is_file():
        return
    with path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    if not rows:
        return
    fieldnames = list(rows[0].keys())
    for col in (
        "escalation_path",
        "business_impact_summary",
        "postmortem_summary",
        "time_to_resolution_minutes",
    ):
        if col not in fieldnames:
            fieldnames.append(col)
    for row in rows:
        sev = row.get("severity", "P3")
        mttr = row.get("mttr_minutes") or row.get("time_to_resolution_minutes") or ""
        row.setdefault("time_to_resolution_minutes", mttr)
        row.setdefault("escalation_path", _escalation(sev))
        title = row.get("title", row.get("service", "incident"))
        rc = row.get("root_cause", "unknown")
        res = row.get("resolution", "resolved per runbook")
        row.setdefault(
            "business_impact_summary",
            f"{sev} on {row.get('service', 'service')} in {row.get('environment', 'prod')}: "
            f"{title}. Customer-facing degradation until rollback/fix.",
        )
        row.setdefault(
            "postmortem_summary",
            f"Root cause: {rc}. Resolution: {res}. MTTR {mttr} min. "
            f"Follow-up: tighten monitoring, canary gates, and runbook validation.",
        )
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    print(f"Enriched {path} ({len(rows)} rows)")


def enrich_incident_history(path: Path) -> None:
    if not path.is_file():
        return
    with path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    if not rows:
        return
    fieldnames = list(rows[0].keys())
    for col in (
        "escalation_path",
        "business_impact_summary",
        "postmortem_summary",
        "time_to_resolution_minutes",
        "symptoms",
    ):
        if col not in fieldnames:
            fieldnames.append(col)
    for row in rows:
        sev = row.get("severity", "P3")
        mttr = row.get("mttr_minutes") or row.get("time_to_resolution_minutes") or ""
        row.setdefault("time_to_resolution_minutes", mttr)
        row.setdefault("escalation_path", _escalation(sev))
        svc = row.get("service", "service")
        env = row.get("environment", "prod")
        impact = row.get("customer_impact") or row.get("business_impact_summary") or ""
        row.setdefault(
            "business_impact_summary",
            impact or f"{sev} {svc} in {env}: regulated betting path affected until recovery.",
        )
        rc = row.get("root_cause", "under investigation")
        res = row.get("resolution", "mitigated")
        row.setdefault("symptoms", row.get("symptoms", f"{svc} degradation in {env}"))
        row.setdefault(
            "postmortem_summary",
            f"Root cause: {rc}. Resolution: {res}. TTR {mttr} min. "
            f"Escalation: {_escalation(sev)}.",
        )
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    print(f"Enriched {path} ({len(rows)} rows)")


def main() -> None:
    enrich_past_incidents(ROOT / "data" / "source" / "past_incidents.csv")
    for rel in (
        "data/sample_documents/incident_history.csv",
        "action_groups/iiq-similar/data/incident_history.csv",
        "action_groups/piter-similar-incidents/data/incident_history.csv",
    ):
        enrich_incident_history(ROOT / rel)


if __name__ == "__main__":
    main()
