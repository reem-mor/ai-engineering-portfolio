"""Local Hugging Face embedding helpers for PyTorch-backed RAG demos and tests."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import torch
from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import CharacterTextSplitter

DEFAULT_EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
DEFAULT_CHUNK_SIZE = 500
DEFAULT_CHUNK_OVERLAP = 50


@dataclass(frozen=True)
class RetrievedChunk:
    content: str
    score: float


def get_embedding_device(*, force_cpu: bool = False) -> str:
    if force_cpu:
        return "cpu"
    return "cuda" if torch.cuda.is_available() else "cpu"


def build_hf_embeddings(
    *,
    force_cpu: bool = False,
    model_name: str = DEFAULT_EMBEDDING_MODEL,
) -> HuggingFaceEmbeddings:
    device = get_embedding_device(force_cpu=force_cpu)
    return HuggingFaceEmbeddings(
        model_name=model_name,
        model_kwargs={"device": device},
        encode_kwargs={"normalize_embeddings": True},
    )


def load_text_document(path: str | Path) -> list[Document]:
    loader = TextLoader(str(path), encoding="utf-8")
    return loader.load()


def split_documents(
    documents: list[Document],
    *,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
) -> list[Document]:
    splitter = CharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )
    return splitter.split_documents(documents)


def build_faiss_index(
    documents: list[Document],
    embeddings: HuggingFaceEmbeddings,
) -> FAISS:
    return FAISS.from_documents(documents, embeddings)


def retrieve_chunks(
    vectorstore: FAISS,
    query: str,
    *,
    topk: int = 3,
) -> list[RetrievedChunk]:
    results = vectorstore.similarity_search_with_score(query, k=topk)
    return [
        RetrievedChunk(content=doc.page_content, score=float(score))
        for doc, score in results
    ]


def retrieved_chunks_to_json(chunks: list[RetrievedChunk]) -> list[dict[str, Any]]:
    return [{"content": item.content, "score": item.score} for item in chunks]
