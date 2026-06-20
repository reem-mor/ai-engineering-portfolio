"""Vector-store backends implementing :class:`~course_assistant.rag.VectorStore`.

- :class:`ChromaVectorStore` — the MVP default: a local Chroma collection
  (persistent on disk, or ephemeral/in-memory when no directory is given).
- :class:`InMemoryVectorStore` — a tiny pure-Python cosine store, dependency-free,
  used as a fast default in tests and as an offline fallback.

Both embed text through an injected :class:`~course_assistant.rag.embeddings.Embedder`,
so embeddings stay mockable and no provider is hardcoded.
"""

from __future__ import annotations

import math
from typing import Any

from course_assistant.rag.embeddings import Embedder
from course_assistant.rag.vectorstore import Document, SearchResult

_COLLECTION = "course_materials"


def _metadata_for(doc: Document) -> dict[str, str]:
    return {"source": doc.source, **doc.metadata}


def _document_from(doc_id: str, text: str, metadata: dict[str, Any]) -> Document:
    meta = {k: str(v) for k, v in (metadata or {}).items()}
    source = meta.pop("source", "")
    return Document(id=doc_id, text=text, source=source, metadata=meta)


class InMemoryVectorStore:
    """A minimal cosine-similarity store kept entirely in memory."""

    def __init__(self, embedder: Embedder) -> None:
        self._embedder = embedder
        self._docs: list[Document] = []
        self._vectors: list[list[float]] = []

    def add(self, documents: list[Document]) -> None:
        if not documents:
            return
        self._docs.extend(documents)
        self._vectors.extend(self._embedder.embed_documents([d.text for d in documents]))

    def search(self, query: str, k: int = 4) -> list[SearchResult]:
        if not self._docs:
            return []
        q = self._embedder.embed_query(query)
        scored = [
            SearchResult(document=doc, score=_cosine(q, vec))
            for doc, vec in zip(self._docs, self._vectors, strict=True)
        ]
        scored.sort(key=lambda r: r.score, reverse=True)
        return scored[:k]

    def clear(self) -> None:
        self._docs.clear()
        self._vectors.clear()


def _cosine(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b, strict=True))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    return dot / (na * nb) if na and nb else 0.0


class ChromaVectorStore:
    """Local Chroma collection (the MVP default vector store).

    Args:
        embedder: Embedder used for both documents and queries.
        persist_dir: Directory for on-disk persistence; ``None`` → ephemeral
            in-memory client (handy for tests).
        collection: Collection name.
    """

    def __init__(
        self,
        embedder: Embedder,
        persist_dir: str | None = None,
        collection: str = _COLLECTION,
    ) -> None:
        import chromadb

        self._embedder = embedder
        self._collection_name = collection
        self._client = (
            chromadb.PersistentClient(path=persist_dir)
            if persist_dir
            else chromadb.EphemeralClient()
        )
        self._collection = self._client.get_or_create_collection(
            collection, metadata={"hnsw:space": "cosine"}
        )

    def add(self, documents: list[Document]) -> None:
        if not documents:
            return
        # chromadb's type stubs are strict about embedding containers; our
        # list[list[float]] is fine at runtime, so cross the boundary as Any.
        embeddings: Any = self._embedder.embed_documents([d.text for d in documents])
        self._collection.upsert(
            ids=[d.id for d in documents],
            embeddings=embeddings,
            documents=[d.text for d in documents],
            metadatas=[_metadata_for(d) for d in documents],
        )

    def search(self, query: str, k: int = 4) -> list[SearchResult]:
        if self._collection.count() == 0:
            return []
        query_embeddings: Any = [self._embedder.embed_query(query)]
        res: Any = self._collection.query(
            query_embeddings=query_embeddings,
            n_results=min(k, self._collection.count()),
        )
        ids = res["ids"][0]
        docs = res["documents"][0]
        metas = res["metadatas"][0]
        dists = res["distances"][0]
        results: list[SearchResult] = []
        for doc_id, text, meta, dist in zip(ids, docs, metas, dists, strict=True):
            results.append(
                SearchResult(
                    document=_document_from(doc_id, text, meta),
                    score=1.0 - float(dist),  # cosine distance → similarity
                )
            )
        return results

    def clear(self) -> None:
        self._client.delete_collection(self._collection_name)
        self._collection = self._client.get_or_create_collection(
            self._collection_name, metadata={"hnsw:space": "cosine"}
        )
