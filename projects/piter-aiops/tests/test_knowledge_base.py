"""Validate the organized Knowledge Base structure."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
KB = ROOT / "knowledge_base"

REQUIRED_DIRS = {"runbooks", "environments", "policies", "incidents", "glossary"}
REQUIRED_FRONT_MATTER_KEYS = {
    "title",
    "doc_type",
    "services",
    "environments",
    "severity_applicable",
    "tags",
    "last_updated",
    "author",
    "version",
}
VALID_DOC_TYPES = {"runbook", "environment", "policy", "incident", "glossary"}


def _front_matter(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8-sig")
    assert text.startswith("---\n"), f"{path} missing YAML front matter"
    end = text.find("\n---\n", 4)
    assert end != -1, f"{path} missing YAML front matter terminator"
    pairs = {}
    for line in text[4:end].splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            pairs[key.strip()] = value.strip()
    return pairs


def test_knowledge_base_has_authoritative_sections():
    assert REQUIRED_DIRS <= {path.name for path in KB.iterdir() if path.is_dir()}


def test_knowledge_base_markdown_has_required_front_matter():
    docs = [
        path
        for path in KB.rglob("*.md")
        if path.is_file() and path.name != "README.md"
    ]
    assert docs
    for path in docs:
        metadata = _front_matter(path)
        assert REQUIRED_FRONT_MATTER_KEYS <= set(metadata), f"{path} missing front matter keys"
        assert metadata["doc_type"].strip('"') in VALID_DOC_TYPES


def test_knowledge_base_keeps_fresh_data_out_of_markdown():
    kb_text = "\n".join(path.read_text(encoding="utf-8-sig") for path in KB.rglob("*.md"))
    assert "real phone numbers" in kb_text
    assert "personal email addresses" in kb_text
    assert "PITER_NOTIFICATION_MODE=live" not in kb_text
