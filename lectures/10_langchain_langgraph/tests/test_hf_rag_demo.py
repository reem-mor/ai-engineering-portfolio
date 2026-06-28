"""Offline tests for the PyTorch Hugging Face RAG demo."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from exercises.hf_rag_model import (
    build_faiss_index,
    build_hf_embeddings,
    get_embedding_device,
    load_text_document,
    retrieve_chunks,
    retrieved_chunks_to_json,
    split_documents,
)
from lecture_config import DATA_DIR


def test_get_embedding_device_respects_force_cpu() -> None:
    assert get_embedding_device(force_cpu=True) == "cpu"


def test_retrieved_chunks_to_json_format() -> None:
    from exercises.hf_rag_model import RetrievedChunk

    payload = retrieved_chunks_to_json(
        [
            RetrievedChunk(content="chunk one", score=0.91),
            RetrievedChunk(content="chunk two", score=0.72),
        ]
    )
    assert payload == [
        {"content": "chunk one", "score": 0.91},
        {"content": "chunk two", "score": 0.72},
    ]


def test_hf_rag_retrieves_report_date() -> None:
    report_path = DATA_DIR / "risk_analysis_report.txt"
    assert report_path.exists(), f"Expected sample document at {report_path}"

    embeddings = build_hf_embeddings(force_cpu=True)
    documents = load_text_document(report_path)
    splits = split_documents(documents)
    vectorstore = build_faiss_index(splits, embeddings)

    results = retrieve_chunks(
        vectorstore,
        "What is the date of the risk analysis report?",
        topk=3,
    )

    assert results
    combined = " ".join(item.content for item in results).lower()
    assert "june" in combined or "2025" in combined
    assert all(item.score >= 0.0 for item in results)
