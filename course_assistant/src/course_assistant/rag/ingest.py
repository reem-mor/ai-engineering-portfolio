"""Re-runnable ingestion: Drive materials → text → chunks → embeddings → store.

Run as a command (``course-assistant-ingest``) to (re)build the local vector
index over the course materials. Ingestion is idempotent: the store is cleared
and rebuilt each run, so re-running picks up new or changed files.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from course_assistant.drive.models import DriveFile, LessonMaterials
from course_assistant.rag.chunk import DEFAULT_CHUNK_SIZE, DEFAULT_OVERLAP, chunk_text
from course_assistant.rag.extract import extract_text, is_extractable
from course_assistant.rag.vectorstore import Document, VectorStore

# Lessons 1–14 of Cohort 1 (the schedule the course follows).
DEFAULT_LESSONS = range(1, 15)


class MaterialsSource(Protocol):
    """What ingestion needs from a Drive service: list materials and read bytes."""

    def get_materials(self, lesson: int) -> LessonMaterials:
        ...

    def download_file(self, file_id: str, mime_type: str) -> bytes:
        ...


@dataclass(frozen=True)
class IngestStats:
    """Summary of an ingestion run."""

    lessons: int
    files: int
    chunks: int
    skipped: int


def _material_files(materials: LessonMaterials) -> list[DriveFile]:
    """All non-recording files for a lesson (slides + homework + code + other)."""
    return [*materials.slides, *materials.homework, *materials.code, *materials.other]


def ingest_materials(
    source: MaterialsSource,
    store: VectorStore,
    lessons: range | list[int] = DEFAULT_LESSONS,
    *,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    overlap: int = DEFAULT_OVERLAP,
) -> IngestStats:
    """Walk lesson materials, extract + chunk text, and (re)build the index."""
    documents: list[Document] = []
    lessons_seen = 0
    files_used = 0
    skipped = 0

    for lesson in lessons:
        materials = source.get_materials(lesson)
        if not materials.found:
            continue
        lessons_seen += 1
        for file in _material_files(materials):
            if not is_extractable(file.title):
                skipped += 1
                continue
            data = source.download_file(file.id, file.mime_type)
            text = extract_text(file.title, data)
            chunks = chunk_text(text, chunk_size=chunk_size, overlap=overlap)
            if not chunks:
                skipped += 1
                continue
            files_used += 1
            for index, chunk in enumerate(chunks):
                documents.append(
                    Document(
                        id=f"{file.id}:{index}",
                        text=chunk,
                        source=file.title,
                        metadata={
                            "url": file.url,
                            "lesson": str(lesson),
                            "kind": str(file.kind),
                        },
                    )
                )

    store.clear()  # idempotent re-index
    store.add(documents)
    return IngestStats(
        lessons=lessons_seen, files=files_used, chunks=len(documents), skipped=skipped
    )


def main() -> None:  # pragma: no cover - wiring for the CLI entry point
    """Build the live Drive service + Chroma store and ingest all lessons."""
    from course_assistant.config import get_settings
    from course_assistant.drive.service import GoogleDriveService
    from course_assistant.rag.embeddings import OpenAIEmbedder
    from course_assistant.rag.stores import ChromaVectorStore

    settings = get_settings()
    source = GoogleDriveService(settings)
    store = ChromaVectorStore(OpenAIEmbedder(settings), persist_dir=settings.chroma_dir)
    stats = ingest_materials(source, store)
    print(
        f"Ingested {stats.chunks} chunks from {stats.files} files "
        f"across {stats.lessons} lessons ({stats.skipped} skipped)."
    )
