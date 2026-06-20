"""End-to-end ingestion test: Drive materials → store → retrieval (all offline)."""

from __future__ import annotations

from course_assistant.drive.fake import FakeDriveService
from course_assistant.rag.embeddings import HashingEmbedder
from course_assistant.rag.ingest import ingest_materials
from course_assistant.rag.stores import InMemoryVectorStore
from course_assistant.tools.search_materials import search_course_materials
from tests.fixtures.docs import make_docx
from tests.fixtures.drive_tree import build_tree

# Real file IDs from the captured snapshot (Lesson 10 HW + code, Lesson 14 HW).
_MIDPROJECT = "1Yn2wAKmT4SpTyXAn5hrZ006uvluDfQ9Z"  # פרויקט אמצע.docx
_BEDROCK_PY = "1qFl0WRx1QYwyaLFRGzxvcEMZBeCA0d3e"  # bedroc_agent.py
_N8N_HW = "1v6pvkGjuxRmGmVoPEk0iCh5v9P7uYWEd"  # n8n_hw.docx


def _source() -> FakeDriveService:
    root_id, tree = build_tree()
    blobs = {
        _MIDPROJECT: make_docx(["Mid project: build a retrieval augmented generation app."]),
        _BEDROCK_PY: b"def call_bedrock_agent(prompt):\n    return invoke('bedrock', prompt)\n",
        _N8N_HW: make_docx(["n8n homework: build an automation workflow with a webhook trigger."]),
    }
    return FakeDriveService(root_id, tree, blobs=blobs)


def test_ingest_indexes_materials_and_is_searchable() -> None:
    store = InMemoryVectorStore(HashingEmbedder(dim=256))
    stats = ingest_materials(_source(), store, lessons=[10, 14])

    assert stats.lessons == 2
    assert stats.files == 3  # midproject docx + bedrock py + n8n docx
    assert stats.chunks >= 3

    out = search_course_materials(store, "bedrock agent code", k=1, lang="en")
    assert "bedroc_agent.py" in out
    assert "Lesson 10" in out


def test_ingest_is_idempotent_on_rerun() -> None:
    store = InMemoryVectorStore(HashingEmbedder(dim=256))
    first = ingest_materials(_source(), store, lessons=[10, 14])
    second = ingest_materials(_source(), store, lessons=[10, 14])
    assert first.chunks == second.chunks
    # Re-running clears + rebuilds, so no duplicate chunks accumulate.
    assert len(store.search("n8n workflow", k=50)) == second.chunks


def test_non_extractable_lessons_skipped_when_absent() -> None:
    store = InMemoryVectorStore(HashingEmbedder(dim=64))
    stats = ingest_materials(_source(), store, lessons=[99])  # no such lesson folder
    assert stats.lessons == 0
    assert stats.chunks == 0
