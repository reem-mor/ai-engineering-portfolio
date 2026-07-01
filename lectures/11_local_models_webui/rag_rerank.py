"""Local RAG pipeline: bi-encoder FAISS retrieval, cross-encoder rerank, llama-server generation."""

from __future__ import annotations

import json
import re
import urllib.error
import urllib.request
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any, Protocol

import faiss
import numpy as np

BI_ENCODER_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
CROSS_ENCODER_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"
DEFAULT_CHUNK_SIZE = 500
DEFAULT_CHUNK_OVERLAP = 50
DEFAULT_RETRIEVE_K = 10
DEFAULT_TOP_K = 3
DEFAULT_RERANK_THRESHOLD = 0.35
NO_CONTEXT_MESSAGE = (
    "I do not have enough relevant information in the knowledge base to answer that question."
)

GROUNDED_SYSTEM_PROMPT = """You are a helpful assistant that answers questions using only the provided context.

Rules:
1. Answer using only the provided context.
2. If the context is insufficient, say you do not have enough information.
3. Keep the answer concise and factual.
4. Do not invent facts not present in the context."""


@dataclass(frozen=True)
class RetrievedChunk:
    content: str
    source: str
    bi_score: float
    rerank_score: float | None = None


@dataclass(frozen=True)
class RagAnswer:
    answer: str
    sources: list[str]
    chunks: list[RetrievedChunk]
    used_context: bool


class CrossEncoderLike(Protocol):
    def predict(self, pairs: list[tuple[str, str]]) -> list[float] | np.ndarray: ...


class BiEncoderLike(Protocol):
    def encode(
        self,
        sentences: list[str],
        *,
        normalize_embeddings: bool = False,
        convert_to_numpy: bool = True,
    ) -> np.ndarray: ...


def load_and_chunk(
    path: Path,
    *,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
) -> list[tuple[str, str]]:
    """Load a text file and split into (content, source) chunks."""
    text = path.read_text(encoding="utf-8").strip()
    if not text:
        raise ValueError(f"No text found in {path}")

    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    chunks: list[tuple[str, str]] = []
    source = path.name

    for paragraph in paragraphs:
        if len(paragraph) <= chunk_size:
            chunks.append((paragraph, source))
            continue

        start = 0
        while start < len(paragraph):
            end = start + chunk_size
            piece = paragraph[start:end].strip()
            if piece:
                chunks.append((piece, source))
            if end >= len(paragraph):
                break
            start = max(end - chunk_overlap, start + 1)

    if not chunks:
        raise ValueError(f"No chunks produced from {path}")
    return chunks


class BiEncoderIndex:
    """FAISS index backed by a sentence-transformers bi-encoder."""

    def __init__(
        self,
        encoder: BiEncoderLike | None = None,
        *,
        model_name: str = BI_ENCODER_MODEL,
    ) -> None:
        if encoder is None:
            from sentence_transformers import SentenceTransformer

            self._encoder = SentenceTransformer(model_name)
        else:
            self._encoder = encoder
        self._index: faiss.IndexFlatIP | None = None
        self._chunks: list[tuple[str, str]] = []

    @property
    def ready(self) -> bool:
        return self._index is not None and bool(self._chunks)

    def build(self, chunks: list[tuple[str, str]]) -> None:
        if not chunks:
            raise ValueError("Cannot build index from empty chunk list")

        texts = [content for content, _ in chunks]
        embeddings = self._encoder.encode(
            texts,
            normalize_embeddings=True,
            convert_to_numpy=True,
        ).astype("float32")

        faiss.normalize_L2(embeddings)
        index = faiss.IndexFlatIP(embeddings.shape[1])
        index.add(embeddings)

        self._index = index
        self._chunks = list(chunks)

    def retrieve(self, query: str, *, k: int = DEFAULT_RETRIEVE_K) -> list[RetrievedChunk]:
        if self._index is None:
            raise RuntimeError("Index is not built yet")

        query_vec = self._encoder.encode(
            [query],
            normalize_embeddings=True,
            convert_to_numpy=True,
        ).astype("float32")
        faiss.normalize_L2(query_vec)

        scores, indices = self._index.search(query_vec, min(k, len(self._chunks)))
        results: list[RetrievedChunk] = []
        for score, idx in zip(scores[0], indices[0], strict=False):
            if idx == -1:
                continue
            content, source = self._chunks[idx]
            results.append(
                RetrievedChunk(content=content, source=source, bi_score=float(score))
            )
        return results


class CrossEncoderReranker:
    """Rerank retrieved chunks with a cross-encoder."""

    def __init__(
        self,
        model: CrossEncoderLike | None = None,
        *,
        model_name: str = CROSS_ENCODER_MODEL,
    ) -> None:
        if model is None:
            from sentence_transformers import CrossEncoder

            self._model = CrossEncoder(model_name)
        else:
            self._model = model

    def rerank(
        self,
        query: str,
        chunks: list[RetrievedChunk],
        *,
        top_k: int = DEFAULT_TOP_K,
    ) -> list[RetrievedChunk]:
        if not chunks:
            return []

        pairs = [(query, chunk.content) for chunk in chunks]
        scores = self._model.predict(pairs)
        scored = sorted(
            (
                replace(chunk, rerank_score=float(score))
                for chunk, score in zip(chunks, scores, strict=True)
            ),
            key=lambda item: item.rerank_score if item.rerank_score is not None else float("-inf"),
            reverse=True,
        )
        return scored[:top_k]


def filter_by_threshold(
    chunks: list[RetrievedChunk],
    *,
    threshold: float = DEFAULT_RERANK_THRESHOLD,
) -> list[RetrievedChunk]:
    """Keep chunks whose rerank score meets the deterministic floor."""
    return [
        chunk
        for chunk in chunks
        if chunk.rerank_score is not None and chunk.rerank_score >= threshold
    ]


def build_context(chunks: list[RetrievedChunk]) -> str:
    return "\n\n".join(chunk.content for chunk in chunks)


class LlamaServerGenerator:
    """Generate answers via llama-server OpenAI-compatible API."""

    def __init__(
        self,
        *,
        base_url: str,
        timeout: float = 120.0,
        opener: Any | None = None,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout
        self._opener = opener

    def generate(
        self,
        question: str,
        context: str,
        *,
        max_tokens: int = 256,
        enable_thinking: bool = False,
    ) -> str:
        prompt = (
            f"{GROUNDED_SYSTEM_PROMPT}\n\n"
            f"Context:\n{context}\n\n"
            f"Question:\n{question}\n\n"
            "Answer:"
        )
        body = {
            "model": "local",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens,
            "chat_template_kwargs": {"enable_thinking": enable_thinking},
        }
        url = f"{self._base_url}/chat/completions"
        req = urllib.request.Request(
            url,
            data=json.dumps(body).encode(),
            headers={"Content-Type": "application/json"},
        )
        try:
            if self._opener is not None:
                resp = self._opener.open(req, timeout=self._timeout)
            else:
                resp = urllib.request.urlopen(req, timeout=self._timeout)
            with resp:
                data = json.loads(resp.read().decode())
        except urllib.error.URLError as exc:
            raise RuntimeError(f"Cannot reach llama-server at {url}: {exc}") from exc
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode()[:500]
            raise RuntimeError(f"llama-server HTTP {exc.code}: {detail}") from exc

        message = data["choices"][0]["message"]
        content = message.get("content", "").strip()
        if not content and message.get("reasoning_content"):
            content = str(message["reasoning_content"]).strip()
        return content


class LocalRagPipeline:
    """End-to-end retrieve, rerank, threshold, and generate pipeline."""

    def __init__(
        self,
        *,
        bi_index: BiEncoderIndex | None = None,
        reranker: CrossEncoderReranker | None = None,
        generator: LlamaServerGenerator | None = None,
        retrieve_k: int = DEFAULT_RETRIEVE_K,
        top_k: int = DEFAULT_TOP_K,
        threshold: float = DEFAULT_RERANK_THRESHOLD,
    ) -> None:
        self._bi_index = bi_index or BiEncoderIndex()
        self._reranker = reranker or CrossEncoderReranker()
        self._generator = generator
        self.retrieve_k = retrieve_k
        self.top_k = top_k
        self.threshold = threshold

    @property
    def index(self) -> BiEncoderIndex:
        return self._bi_index

    def index_document(self, path: Path) -> None:
        chunks = load_and_chunk(path)
        self._bi_index.build(chunks)

    def retrieve(self, query: str) -> list[RetrievedChunk]:
        return self._bi_index.retrieve(query, k=self.retrieve_k)

    def rerank(self, query: str, chunks: list[RetrievedChunk]) -> list[RetrievedChunk]:
        return self._reranker.rerank(query, chunks, top_k=self.top_k)

    def retrieve_and_rerank(self, query: str) -> tuple[list[RetrievedChunk], list[RetrievedChunk]]:
        retrieved = self.retrieve(query)
        reranked = self.rerank(query, retrieved)
        return retrieved, reranked

    def answer(
        self,
        query: str,
        *,
        max_tokens: int = 256,
        enable_thinking: bool = False,
    ) -> RagAnswer:
        retrieved, reranked = self.retrieve_and_rerank(query)
        filtered = filter_by_threshold(reranked, threshold=self.threshold)

        if not filtered:
            return RagAnswer(
                answer=NO_CONTEXT_MESSAGE,
                sources=[],
                chunks=reranked,
                used_context=False,
            )

        if self._generator is None:
            raise RuntimeError("Generator is not configured")

        context = build_context(filtered)
        answer_text = self._generator.generate(
            query,
            context,
            max_tokens=max_tokens,
            enable_thinking=enable_thinking,
        )
        sources = sorted({chunk.source for chunk in filtered})
        return RagAnswer(
            answer=answer_text,
            sources=sources,
            chunks=filtered,
            used_context=True,
        )


def chunks_to_json(chunks: list[RetrievedChunk]) -> list[dict[str, Any]]:
    return [
        {
            "content": chunk.content,
            "source": chunk.source,
            "bi_score": chunk.bi_score,
            "rerank_score": chunk.rerank_score,
        }
        for chunk in chunks
    ]


def rag_answer_to_json(result: RagAnswer) -> dict[str, Any]:
    return {
        "answer": result.answer,
        "sources": result.sources,
        "chunks": chunks_to_json(result.chunks),
        "used_context": result.used_context,
    }
