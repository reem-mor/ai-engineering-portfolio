"""Retrieval-augmented generation over course materials.

Phase 1 establishes the :mod:`vectorstore` interface. Phase 3 adds the ingestion
pipeline and the ``search_course_materials`` retrieval tool.
"""

from course_assistant.rag.vectorstore import Document, SearchResult, VectorStore

__all__ = ["Document", "SearchResult", "VectorStore"]
