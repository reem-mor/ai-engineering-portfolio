from pathlib import Path

import pytest

from app.core.config import settings
from app.rag.embeddings import FakeEmbeddingProvider
from app.rag.faiss_store import FaissVectorStore
from app.services.document_service import DocumentService


def test_document_service_lists_supported_files(tmp_path: Path):
    (tmp_path / "a.txt").write_text("hello", encoding="utf-8")
    (tmp_path / "b.exe").write_text("ignore", encoding="utf-8")
    service = DocumentService(embedding_provider=FakeEmbeddingProvider(), vector_store=FaissVectorStore(index_dir=tmp_path / "index"))
    files = service.list_supported_files(tmp_path)
    assert [file.name for file in files] == ["a.txt"]


def test_document_service_processes_file_with_fake_embeddings(tmp_path: Path):
    source = tmp_path / "auth.txt"
    source.write_text("auth-service login failure after deployment. Check logs and health endpoint." * 5, encoding="utf-8")
    index_dir = tmp_path / "index"
    service = DocumentService(embedding_provider=FakeEmbeddingProvider(dimensions=8), vector_store=FaissVectorStore(index_dir=index_dir))
    service.process_embed_and_index_file(source)
    assert (index_dir / settings.faiss_index_file).exists()
    assert (index_dir / settings.faiss_metadata_file).exists()


def test_document_service_rejects_empty_path_list(tmp_path: Path):
    index_dir = tmp_path / "index"
    svc = DocumentService(embedding_provider=FakeEmbeddingProvider(dimensions=8), vector_store=FaissVectorStore(index_dir=index_dir))
    with pytest.raises(ValueError, match="No files"):
        svc.process_embed_and_index_files([])


def test_document_service_raises_for_missing_directory(tmp_path: Path):
    svc = DocumentService(embedding_provider=FakeEmbeddingProvider(dimensions=8), vector_store=FaissVectorStore(index_dir=tmp_path / "index"))
    missing = tmp_path / "no_such_folder"
    with pytest.raises(ValueError, match="does not exist"):
        svc.list_supported_files(missing)
