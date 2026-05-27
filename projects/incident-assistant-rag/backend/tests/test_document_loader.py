from pathlib import Path

import pytest

from app.core.config import settings
from app.core.exceptions import EmptyDocumentError, UnsupportedFileTypeError
from app.rag.document_loader import DocumentLoader

SAMPLE_DOCS_DIR = settings.sample_documents_dir


def test_loader_loads_text_file(tmp_path: Path):
    path = tmp_path / "a.txt"
    path.write_text("hello", encoding="utf-8")
    assert DocumentLoader().load(path) == "hello"


def test_loader_rejects_unsupported_file(tmp_path: Path):
    path = tmp_path / "a.exe"
    path.write_text("hello", encoding="utf-8")
    with pytest.raises(UnsupportedFileTypeError):
        DocumentLoader().load(path)


def test_loader_rejects_empty_file(tmp_path: Path):
    path = tmp_path / "a.txt"
    path.write_text("", encoding="utf-8")
    with pytest.raises(EmptyDocumentError):
        DocumentLoader().load(path)


def test_loader_file_not_found(tmp_path: Path):
    missing = tmp_path / "missing.txt"
    with pytest.raises(FileNotFoundError, match="File not found"):
        DocumentLoader().load(missing)


def test_loader_reads_markdown(tmp_path: Path):
    path = tmp_path / "note.md"
    path.write_text("# Title\nHello", encoding="utf-8")
    assert "Hello" in DocumentLoader().load(path)


def test_loader_reads_csv_with_headers(tmp_path: Path):
    path = tmp_path / "sheet.csv"
    path.write_text("col_a,col_b\n1,2\n", encoding="utf-8")
    out = DocumentLoader().load(path)
    assert "col_a" in out and "2" in out


def test_loader_reads_sample_pdf():
    path = SAMPLE_DOCS_DIR / "database_locks_runbook.pdf"
    if not path.is_file():
        pytest.skip("sample PDF not present in data/sample_documents")
    text = DocumentLoader().load(path)
    assert "database" in text.lower()
    assert "lock" in text.lower()


def test_loader_reads_sample_docx():
    path = SAMPLE_DOCS_DIR / "deployment_failure_sop.docx"
    if not path.is_file():
        pytest.skip("sample DOCX not present in data/sample_documents")
    text = DocumentLoader().load(path)
    assert "deployment" in text.lower()


def test_loader_reads_sample_csv():
    path = SAMPLE_DOCS_DIR / "incident_examples.csv"
    if not path.is_file():
        pytest.skip("sample CSV not present in data/sample_documents")
    text = DocumentLoader().load(path)
    assert len(text.strip()) > 0
