import json
from pathlib import Path
from typing import Any

import faiss
import numpy as np

from app.core.config import settings
from app.schemas.embedding_schema import EmbeddedChunk
from app.schemas.search_schema import SearchResult


class FaissVectorStore:
    """
    FAISS vector-store wrapper.

    Supports both:
    1. Production flow:
       build_and_save(embedded_chunks)

    2. Test/backward-compatible flow:
       build_index(embedded_chunks)
       save()
       load()
       search(query_embedding, top_k)

    Important:
    - In production, OpenAI embeddings are usually 1536 dimensions.
    - In tests, fake embeddings may be 3 or 8 dimensions.
    - Therefore, this class infers the dimension from the provided vectors
      unless embedding_dimensions is explicitly passed.
    """

    def __init__(
        self,
        index_dir: Path | None = None,
        embedding_dimensions: int | None = None,
    ) -> None:
        self.index_dir = index_dir or settings.faiss_index_dir
        self.embedding_dimensions = embedding_dimensions

        self.index_path = self.index_dir / settings.faiss_index_file
        self.metadata_path = self.index_dir / settings.faiss_metadata_file

        self.index: faiss.IndexFlatIP | None = None
        self.metadata: list[dict[str, Any]] = []

    def build_and_save(self, embedded_chunks: list[EmbeddedChunk]) -> None:
        """
        Build and save FAISS index from EmbeddedChunk objects.
        Used by DocumentService.
        """
        self.build_index(embedded_chunks)
        self.save()

    def build_index(self, embedded_chunks: list[EmbeddedChunk]) -> None:
        """
        Build FAISS index in memory from embedded chunks.

        This method is intentionally separate from save() because tests expect:
            store.build_index(...)
            store.save()
        """
        if not embedded_chunks:
            raise ValueError("No embedded chunks were provided.")

        embeddings: list[list[float]] = []
        metadata: list[dict[str, Any]] = []

        for item in embedded_chunks:
            item_dict = item.model_dump()

            embedding = self._extract_embedding(item_dict)
            chunk_metadata = self._extract_metadata(item_dict)

            embeddings.append(embedding)
            metadata.append(chunk_metadata)

        vectors = self._validate_and_prepare_vectors(embeddings)

        index = faiss.IndexFlatIP(vectors.shape[1])
        index.add(vectors)

        self.index = index
        self.metadata = metadata
        self.embedding_dimensions = vectors.shape[1]

    def save(
        self,
        embeddings: list[list[float]] | None = None,
        metadata: list[dict[str, Any]] | None = None,
    ) -> None:
        """
        Save FAISS index and metadata to disk.

        Supports two flows:
        1. save(embeddings, metadata) - direct save
        2. build_index(...), then save() - test-compatible flow
        """
        if embeddings is not None or metadata is not None:
            if embeddings is None or metadata is None:
                raise ValueError(
                    "Both embeddings and metadata must be provided together."
                )

            vectors = self._validate_and_prepare_vectors(embeddings)

            index = faiss.IndexFlatIP(vectors.shape[1])
            index.add(vectors)

            self.index = index
            self.metadata = metadata
            self.embedding_dimensions = vectors.shape[1]

        if self.index is None or not self.metadata:
            raise ValueError("Cannot save empty FAISS index.")

        self.index_dir.mkdir(parents=True, exist_ok=True)

        faiss.write_index(self.index, str(self.index_path))

        with self.metadata_path.open("w", encoding="utf-8") as file:
            json.dump(self.metadata, file, ensure_ascii=False, indent=2)

    def load(self) -> None:
        if not self.index_path.exists() or not self.metadata_path.exists():
            raise FileNotFoundError("FAISS index is not loaded.")

        self.index = faiss.read_index(str(self.index_path))

        with self.metadata_path.open("r", encoding="utf-8") as file:
            self.metadata = json.load(file)

        if self.index.ntotal != len(self.metadata):
            raise ValueError(
                "FAISS index and metadata size mismatch. "
                f"Index vectors: {self.index.ntotal}, "
                f"metadata records: {len(self.metadata)}."
            )

        self.embedding_dimensions = self.index.d

    def search(
        self,
        query_embedding: list[float],
        top_k: int,
    ) -> list[SearchResult]:
        if top_k < 1:
            raise ValueError("top_k must be positive.")

        if self.index is None:
            self.load()

        if self.index is None:
            raise FileNotFoundError("FAISS index is not loaded.")

        query_vector = np.array([query_embedding], dtype="float32")

        if query_vector.ndim != 2 or query_vector.shape[1] == 0:
            raise ValueError("Query embedding must be a non-empty vector.")

        if query_vector.shape[1] != self.index.d:
            raise ValueError(
                "Query embedding dimension does not match index dimension. "
                f"Expected index dimension {self.index.d}, got query dimension {query_vector.shape[1]}."
            )

        faiss.normalize_L2(query_vector)

        safe_top_k = min(top_k, self.index.ntotal)
        scores, indices = self.index.search(query_vector, safe_top_k)

        results: list[SearchResult] = []

        for score, index_position in zip(scores[0], indices[0]):
            if index_position < 0:
                continue

            row = self.metadata[index_position]

            results.append(
                SearchResult(
                    chunk_id=str(row.get("chunk_id", "")),
                    source_file=str(row.get("source_file", "")),
                    chunk_index=int(row.get("chunk_index", 0)),
                    text=str(row.get("text", "")),
                    score=float(score),
                )
            )

        return results

    def save_index(
        self,
        embeddings: list[list[float]],
        metadata: list[dict[str, Any]],
    ) -> None:
        """
        Backward-compatible alias.
        """
        self.save(embeddings=embeddings, metadata=metadata)

    def load_index(self) -> None:
        """
        Backward-compatible alias.
        """
        self.load()

    def _validate_and_prepare_vectors(
        self,
        embeddings: list[list[float]],
    ) -> np.ndarray:
        if not embeddings:
            raise ValueError("Cannot build FAISS index from empty embeddings.")

        dimensions = [len(vector) for vector in embeddings]

        if any(dimension <= 0 for dimension in dimensions):
            raise ValueError("Embedding dimension must be greater than zero.")

        if len(set(dimensions)) != 1:
            raise ValueError("All embeddings must have the same dimension.")

        vectors = np.array(embeddings, dtype="float32")

        if vectors.ndim != 2:
            raise ValueError("Embeddings must be a 2D list of vectors.")

        actual_dimension = vectors.shape[1]

        if (
            self.embedding_dimensions is not None
            and actual_dimension != self.embedding_dimensions
        ):
            raise ValueError(
                f"Embedding dimension mismatch. Expected {self.embedding_dimensions}, "
                f"got {actual_dimension}."
            )

        faiss.normalize_L2(vectors)

        return vectors

    @staticmethod
    def _extract_embedding(item_dict: dict[str, Any]) -> list[float]:
        if "embedding" in item_dict:
            embedding = item_dict["embedding"]
        else:
            embedding = item_dict.get("vector")

        if embedding is None:
            raise ValueError(
                "EmbeddedChunk is missing an embedding field. "
                "Expected 'embedding' or 'vector'."
            )

        if not isinstance(embedding, list):
            raise ValueError("EmbeddedChunk embedding must be a list of floats.")

        return [float(value) for value in embedding]

    @staticmethod
    def _extract_metadata(item_dict: dict[str, Any]) -> dict[str, Any]:
        chunk = item_dict.get("chunk")

        if isinstance(chunk, dict):
            source = chunk
        else:
            source = item_dict

        return {
            "chunk_id": str(source.get("chunk_id", "")),
            "source_file": str(source.get("source_file", "")),
            "chunk_index": int(source.get("chunk_index", 0)),
            "text": str(source.get("text", "")),
        }
