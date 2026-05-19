"""Knowledge-base browse endpoints — power the left-sidebar incident/SOP/resource lists.

These endpoints serve curated, pre-computed views of the static seed corpus
(``data/sample_incidents``) and the live FAISS retriever stats. They are
strictly read-only and do not invoke the LLM.
"""

from __future__ import annotations

from collections import defaultdict
from typing import Any

from fastapi import APIRouter

from app.core.retriever import get_retriever
from app.utils.logger import get_logger
from data.sample_incidents import (
    get_incidents,
    get_references,
    get_sops,
)

router: APIRouter = APIRouter()
_logger = get_logger(__name__)

_SEVERITY_ORDER: dict[str, int] = {"P1": 0, "P2": 1, "P3": 2}


@router.get(
    "/incidents",
    tags=["knowledge"],
    summary="All incidents grouped by severity (P1 → P2 → P3)",
)
async def list_incidents() -> dict[str, list[dict[str, Any]]]:
    """Return incidents grouped by severity, sorted ascending by mttr_minutes within each group."""
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for inc in get_incidents():
        sev: str = str(inc.get("severity", "")).upper()
        if sev not in _SEVERITY_ORDER:
            continue
        grouped[sev].append(
            {
                "id": str(inc.get("id", "")),
                "title": str(inc.get("title", "")),
                "category": str(inc.get("category", "Unknown")),
                "mttr_minutes": int(inc.get("mttr_minutes", 0)),
            }
        )

    for sev in grouped:
        grouped[sev].sort(key=lambda r: (r["mttr_minutes"], r["id"]))

    payload: dict[str, list[dict[str, Any]]] = {
        "P1": grouped.get("P1", []),
        "P2": grouped.get("P2", []),
        "P3": grouped.get("P3", []),
    }
    _logger.info(
        "Incidents listed: p1=%d p2=%d p3=%d",
        len(payload["P1"]),
        len(payload["P2"]),
        len(payload["P3"]),
    )
    return payload


@router.get(
    "/sops",
    tags=["knowledge"],
    summary="All SOPs sorted by severity_trigger (P1 first)",
)
async def list_sops() -> list[dict[str, Any]]:
    """Return SOPs sorted by severity_trigger ascending (P1 → P2 → P3 → unknown last)."""
    rows: list[dict[str, Any]] = []
    for sop in get_sops():
        trigger: str = str(sop.get("severity_trigger", "")).upper()
        rows.append(
            {
                "id": str(sop.get("id", "")),
                "title": str(sop.get("title", "")),
                "applicability": str(sop.get("applicability", "")),
                "severity_trigger": trigger or "N/A",
                "owner": str(sop.get("owner", "Unassigned")),
            }
        )

    rows.sort(
        key=lambda r: (
            _SEVERITY_ORDER.get(r["severity_trigger"], 99),
            r["id"],
        )
    )
    _logger.info("SOPs listed: count=%d", len(rows))
    return rows


@router.get(
    "/resources",
    tags=["knowledge"],
    summary="Curated external references (REAL_REFERENCES) for the resource panel",
)
async def list_resources() -> list[dict[str, Any]]:
    """Return REAL_REFERENCES projected to the fields the resource panel needs."""
    rows: list[dict[str, Any]] = []
    for ref in get_references():
        rows.append(
            {
                "id": str(ref.get("id", "")),
                "title": str(ref.get("title", "")),
                "source": str(ref.get("source", "")),
                "category": str(ref.get("category", "Reference")),
                "mttr_impact": str(ref.get("mttr_impact", "")),
                "key_concepts": list(ref.get("key_concepts", [])),
                "content": str(ref.get("content", "")),
            }
        )
    _logger.info("Resources listed: count=%d", len(rows))
    return rows


@router.get(
    "/stats",
    tags=["knowledge"],
    summary="Knowledge base statistics for the left-sidebar stats bar",
)
async def stats() -> dict[str, Any]:
    """Aggregate counts and MTTR averages across the seed corpus and live FAISS index."""
    incidents: list[dict[str, Any]] = get_incidents()
    sops: list[dict[str, Any]] = get_sops()
    references: list[dict[str, Any]] = get_references()

    severity_buckets: dict[str, list[int]] = defaultdict(list)
    categories: set[str] = set()
    for inc in incidents:
        sev: str = str(inc.get("severity", "")).upper()
        if sev in _SEVERITY_ORDER:
            severity_buckets[sev].append(int(inc.get("mttr_minutes", 0)))
        categories.add(str(inc.get("category", "Unknown")))

    p1_mttrs: list[int] = severity_buckets.get("P1", [])
    p2_mttrs: list[int] = severity_buckets.get("P2", [])

    try:
        index_stats: dict[str, Any] = get_retriever().get_index_stats()
        total_vectors: int = int(index_stats.get("total_vectors", 0))
    except RuntimeError:
        total_vectors = 0

    payload: dict[str, Any] = {
        "total_incidents": len(incidents),
        "total_sops": len(sops),
        "total_references": len(references),
        "total_vectors": total_vectors,
        "p1_incidents": len(p1_mttrs),
        "p2_incidents": len(p2_mttrs),
        "p3_incidents": len(severity_buckets.get("P3", [])),
        "categories": sorted(categories),
        "avg_mttr_p1_minutes": round(sum(p1_mttrs) / len(p1_mttrs)) if p1_mttrs else 0,
        "avg_mttr_p2_minutes": round(sum(p2_mttrs) / len(p2_mttrs)) if p2_mttrs else 0,
    }
    _logger.info(
        "Stats: vectors=%d incidents=%d sops=%d refs=%d p1=%d p2=%d p3=%d",
        payload["total_vectors"],
        payload["total_incidents"],
        payload["total_sops"],
        payload["total_references"],
        payload["p1_incidents"],
        payload["p2_incidents"],
        payload["p3_incidents"],
    )
    return payload
