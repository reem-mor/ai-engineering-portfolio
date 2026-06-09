"""Load the PITER Knowledge Base corpus (JSON documents + catalog CSV).

Operational CSV/JSON for tools lives under ``data/source/``. This module covers
only the narrative RAG corpus under ``knowledge_base/`` (``.json`` + ``catalog.csv``).
"""
from __future__ import annotations

import csv
import json
from functools import lru_cache
from pathlib import Path
from typing import Any, Iterator

ROOT = Path(__file__).resolve().parents[2]
KB_ROOT = ROOT / "knowledge_base"

REQUIRED_DOC_KEYS = {
    "doc_id",
    "title",
    "doc_type",
    "services",
    "environments",
    "severity_applicable",
    "tags",
    "last_updated",
    "author",
    "version",
    "body",
}
VALID_DOC_TYPES = {"runbook", "policy", "incident", "service", "guide", "reference"}
CORPUS_JSON_GLOB = "*.json"
CATALOG_NAME = "catalog.csv"
STRUCTURED_INDEX_NAME = "structured_data_index.json"


def kb_root() -> Path:
    return KB_ROOT


def iter_corpus_json_paths(*, root: Path | None = None) -> Iterator[Path]:
    """Yield KB document JSON files (excludes index/manifest JSON)."""
    base = root or KB_ROOT
    if not base.is_dir():
        return
    for path in sorted(base.rglob(CORPUS_JSON_GLOB)):
        if not path.is_file():
            continue
        if path.name == "README.json":
            continue
        yield path


def load_kb_document(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a JSON object")
    missing = REQUIRED_DOC_KEYS - set(data)
    if missing:
        raise ValueError(f"{path} missing keys: {sorted(missing)}")
    dtype = str(data["doc_type"]).strip()
    if dtype not in VALID_DOC_TYPES:
        raise ValueError(f"{path} invalid doc_type: {dtype!r}")
    return data


def document_text(doc: dict[str, Any]) -> str:
    """Text used for chunking / retrieval (title + body)."""
    title = str(doc.get("title", "")).strip()
    body = str(doc.get("body", "")).strip()
    if title and body:
        return f"# {title}\n\n{body}"
    return title or body


@lru_cache(maxsize=1)
def load_kb_manifest() -> list[dict[str, Any]]:
    docs: list[dict[str, Any]] = []
    for path in iter_corpus_json_paths():
        doc = load_kb_document(path)
        rel = path.relative_to(KB_ROOT).as_posix()
        docs.append(
            {
                "id": rel,
                "doc_id": doc["doc_id"],
                "title": doc["title"],
                "doc_type": doc["doc_type"],
                "services": doc["services"],
                "environments": doc["environments"],
                "severity_applicable": doc["severity_applicable"],
                "tags": doc["tags"],
                "last_updated": doc["last_updated"],
                "author": doc["author"],
                "version": doc["version"],
                "format": "json",
                "indexed": True,
                "sync_status": "indexed",
            }
        )
    return docs


def write_catalog_csv(*, root: Path | None = None) -> Path:
    """Regenerate catalog.csv from corpus JSON metadata."""
    base = root or KB_ROOT
    catalog_path = base / CATALOG_NAME
    rows: list[dict[str, str]] = []
    for path in iter_corpus_json_paths(root=base):
        doc = load_kb_document(path)
        rel = path.relative_to(base).as_posix()
        rows.append(
            {
                "doc_id": str(doc["doc_id"]),
                "path": rel,
                "doc_type": str(doc["doc_type"]),
                "title": str(doc["title"]),
                "services": str(doc["services"]),
                "format": "json",
            }
        )
    base.mkdir(parents=True, exist_ok=True)
    with catalog_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["doc_id", "path", "doc_type", "title", "services", "format"],
        )
        writer.writeheader()
        writer.writerows(rows)
    return catalog_path
