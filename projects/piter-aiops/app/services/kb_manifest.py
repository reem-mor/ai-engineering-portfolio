"""Knowledge Base manifest for SPA listing and retrieval tester."""
from __future__ import annotations

import re
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
KB_ROOT = ROOT / "knowledge_base"


def _parse_front_matter(text: str) -> dict[str, str]:
    if not text.startswith("---\n"):
        return {}
    end = text.find("\n---\n", 4)
    if end == -1:
        return {}
    meta: dict[str, str] = {}
    for line in text[4:end].splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            meta[key.strip()] = value.strip().strip('"')
    return meta


def _infer_from_filename(path: Path) -> dict[str, str]:
    name = path.stem
    doc_type = "runbook"
    if name.startswith("ENV-"):
        doc_type = "environment"
    elif name.startswith("POL-"):
        doc_type = "policy"
    elif name.startswith("INC-"):
        doc_type = "incident"
    elif name.startswith("GLO-"):
        doc_type = "glossary"
    title = name.replace("-", " ").title()
    return {
        "title": title,
        "doc_type": doc_type,
        "services": "[]",
        "environments": "[]",
        "severity_applicable": "[]",
        "tags": "[]",
        "last_updated": "2026-06-06",
        "author": "Re'em Mor",
        "version": "1.0",
    }


@lru_cache(maxsize=1)
def load_kb_manifest() -> list[dict]:
    docs: list[dict] = []
    if not KB_ROOT.is_dir():
        return docs

    for path in sorted(KB_ROOT.rglob("*.md")):
        if path.name == "README.md" and path.parent.name == "runbooks":
            continue
        text = path.read_text(encoding="utf-8-sig")
        meta = _parse_front_matter(text)
        if not meta:
            meta = _infer_from_filename(path)

        rel = path.relative_to(KB_ROOT).as_posix()
        docs.append(
            {
                "id": rel,
                "title": meta.get("title", path.stem),
                "doc_type": meta.get("doc_type", "runbook"),
                "services": meta.get("services", "[]"),
                "environments": meta.get("environments", "[]"),
                "severity_applicable": meta.get("severity_applicable", "[]"),
                "tags": meta.get("tags", "[]"),
                "last_updated": meta.get("last_updated", ""),
                "author": meta.get("author", ""),
                "version": meta.get("version", "1.0"),
                "indexed": True,
                "sync_status": "indexed",
            }
        )
    return docs


def kb_sections() -> dict[str, list[dict]]:
    manifest = load_kb_manifest()
    sections: dict[str, list[dict]] = {
        "runbooks": [],
        "environments": [],
        "policies": [],
        "incidents": [],
        "glossary": [],
    }
    for doc in manifest:
        dtype = doc.get("doc_type", "runbook")
        key = f"{dtype}s" if dtype != "policy" else "policies"
        if dtype == "environment":
            key = "environments"
        if dtype == "glossary":
            key = "glossary"
        if dtype == "incident":
            key = "incidents"
        if key in sections:
            sections[key].append(doc)
    return sections
