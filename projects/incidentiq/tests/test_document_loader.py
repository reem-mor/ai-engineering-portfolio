"""Tests for multi-format document loading."""

from __future__ import annotations

from pathlib import Path

import pytest

from app.core.document_loader import default_documents_dir, extract_text, load_documents_from_folder

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
_FIXTURES = _PROJECT_ROOT / "tests" / "fixtures" / "documents"


def test_default_documents_dir_points_at_data_documents() -> None:
    assert default_documents_dir().name == "documents"
    assert default_documents_dir().parent.name == "data"


def test_load_sample_txt_document() -> None:
    records = load_documents_from_folder(_PROJECT_ROOT / "data" / "documents")
    txt_records = [r for r in records if r["source_file"].endswith(".txt")]
    assert txt_records, "Expected at least one TXT document in data/documents/"
    assert txt_records[0]["text"]
    assert txt_records[0]["id"].startswith("INC-")


def test_extract_text_from_fixture_txt(tmp_path: Path) -> None:
    sample = tmp_path / "INC-099_sample.txt"
    sample.write_text("Incident INC-099 sample text for retrieval.", encoding="utf-8")
    assert "INC-099" in extract_text(sample)


def test_unsupported_extension_is_skipped(tmp_path: Path, caplog: pytest.LogCaptureFixture) -> None:
    (tmp_path / "notes.md").write_text("# ignore me", encoding="utf-8")
    records = load_documents_from_folder(tmp_path)
    assert records == []
    assert any("Skipping unsupported" in rec.message for rec in caplog.records)


def test_xlsx_fixture_when_present() -> None:
    xlsx_path = _PROJECT_ROOT / "data" / "documents" / "incident_register.xlsx"
    if not xlsx_path.is_file():
        pytest.skip("Sample XLSX not generated yet")
    text = extract_text(xlsx_path)
    assert "INC-001" in text
    assert "PostgreSQL" in text
