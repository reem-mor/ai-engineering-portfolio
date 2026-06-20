"""Retrieval-augmented generation over course materials.

Phase 1 established the :mod:`vectorstore` interface. Phase 3 adds the embedding
backends, chunking, content extraction, vector-store backends, and the
re-runnable ingestion pipeline behind that interface.
"""

from course_assistant.rag.embeddings import Embedder, HashingEmbedder, OpenAIEmbedder
from course_assistant.rag.stores import ChromaVectorStore, InMemoryVectorStore
from course_assistant.rag.vectorstore import Document, SearchResult, VectorStore

__all__ = [
    "ChromaVectorStore",
    "Document",
    "Embedder",
    "HashingEmbedder",
    "InMemoryVectorStore",
    "OpenAIEmbedder",
    "SearchResult",
    "VectorStore",
]
