"""PyTorch-backed RAG demo: local Hugging Face embeddings + FAISS retrieval (offline)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import torch

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from exercises.hf_rag_model import (
    build_faiss_index,
    build_hf_embeddings,
    load_text_document,
    retrieve_chunks,
    retrieved_chunks_to_json,
    split_documents,
)
from lecture_config import DATA_DIR

FORCE_CPU = False
TOPK = 3
DEFAULT_QUERY = "What is the date of the risk analysis report?"
DEFAULT_DOCUMENT = DATA_DIR / "risk_analysis_report.txt"


def main() -> None:
    document_path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_DOCUMENT
    query = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_QUERY

    device = "cpu" if FORCE_CPU else ("cuda" if torch.cuda.is_available() else "cpu")
    print("CUDA available:", torch.cuda.is_available())
    print("Embedding device:", device)
    print("Document path:", document_path)
    print("Query:", query)

    embeddings = build_hf_embeddings(force_cpu=FORCE_CPU)
    documents = load_text_document(document_path)
    splits = split_documents(documents)
    vectorstore = build_faiss_index(splits, embeddings)

    results = retrieve_chunks(vectorstore, query, topk=TOPK)
    print(json.dumps(retrieved_chunks_to_json(results), indent=2))


if __name__ == "__main__":
    main()
