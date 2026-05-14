"""
CLI RAG pipeline: load .txt files → embed (HuggingFace) → index (FAISS) → answer (Gemini).

Required environment variables:
    GEMINI_API_KEY  — Google AI Studio key
    HF_TOKEN        — HuggingFace access token

Data folder: lectures/04_nlp_rag/data/  (relative to this script: ../data)
"""
import os
import time
from pathlib import Path

import faiss
import numpy as np
import nltk

from google import genai
from google.genai import types
from huggingface_hub import InferenceClient
from nltk.tokenize import sent_tokenize


# ==========================================================
# CONFIGURATION
# ==========================================================

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
HF_TOKEN = os.environ.get("HF_TOKEN", "")

DATA_FOLDER = str(Path(__file__).parent.parent / "data")
HF_EMBEDDING_MODEL = "ibm-granite/granite-embedding-97m-multilingual-r2"
GEMINI_MODEL = "gemini-2.0-flash"
TOP_K = 3
BATCH_SIZE = 1  # increase to 4–8 once you confirm connectivity


# ==========================================================
# CLIENTS
# ==========================================================

def _make_clients():
    if not GEMINI_API_KEY:
        raise RuntimeError("GEMINI_API_KEY is not set.")
    if not HF_TOKEN:
        raise RuntimeError("HF_TOKEN is not set.")
    return (
        genai.Client(api_key=GEMINI_API_KEY),
        InferenceClient(provider="hf-inference", api_key=HF_TOKEN),
    )


# ==========================================================
# NLTK SETUP
# ==========================================================

def setup_nltk() -> None:
    nltk.download("punkt", quiet=True)
    nltk.download("punkt_tab", quiet=True)


# ==========================================================
# DOCUMENT LOADING
# ==========================================================

def load_documents(folder: str = DATA_FOLDER) -> list[str]:
    if not os.path.exists(folder):
        raise FileNotFoundError(
            f"Data folder '{folder}' not found. "
            "Place .txt files in lectures/04_nlp_rag/data/"
        )
    chunks = []
    for file_name in os.listdir(folder):
        if file_name.endswith(".txt"):
            path = os.path.join(folder, file_name)
            with open(path, "r", encoding="utf-8") as f:
                text = f.read()
            for sentence in sent_tokenize(text):
                sentence = sentence.strip()
                if sentence:
                    chunks.append(sentence)
    if not chunks:
        raise ValueError(f"No text found in '{folder}'.")
    print(f"Loaded {len(chunks)} chunks from '{folder}'.")
    return chunks


# ==========================================================
# EMBEDDINGS (HuggingFace)
# ==========================================================

def _normalize(raw_output, expected_count: int) -> np.ndarray:
    arr = np.array(raw_output, dtype="float32")
    if arr.ndim == 1:
        arr = arr.reshape(1, -1)
    elif arr.ndim == 2:
        if arr.shape[0] != expected_count and expected_count == 1:
            arr = arr.mean(axis=0, keepdims=True)
    elif arr.ndim == 3:
        arr = arr.mean(axis=1)
    return arr.astype("float32")


def _embed_with_retries(hf_client, inputs, expected_count: int, max_retries: int = 5) -> np.ndarray:
    for attempt in range(1, max_retries + 1):
        try:
            result = hf_client.feature_extraction(inputs, model=HF_EMBEDDING_MODEL)
            return _normalize(result, expected_count)
        except Exception as exc:
            print(f"Embedding attempt {attempt}/{max_retries} failed: {exc}")
            if attempt == max_retries:
                raise
            time.sleep(attempt * 3)


def embed_texts(hf_client, texts: list[str], batch_size: int = BATCH_SIZE) -> np.ndarray:
    all_embeddings = []
    total = (len(texts) + batch_size - 1) // batch_size
    for i, start in enumerate(range(0, len(texts), batch_size), 1):
        batch = texts[start:start + batch_size]
        print(f"  Embedding batch {i}/{total}...")
        all_embeddings.append(_embed_with_retries(hf_client, batch, len(batch)))
    return np.vstack(all_embeddings).astype("float32")


# ==========================================================
# FAISS INDEX
# ==========================================================

def build_index(embeddings: np.ndarray) -> faiss.IndexFlatIP:
    faiss.normalize_L2(embeddings)
    index = faiss.IndexFlatIP(embeddings.shape[1])
    index.add(embeddings)
    print(f"FAISS index built with {index.ntotal} vectors.")
    return index


def retrieve(query: str, hf_client, index: faiss.IndexFlatIP, chunks: list[str], k: int = TOP_K) -> list[str]:
    q_emb = _embed_with_retries(hf_client, query, expected_count=1)
    faiss.normalize_L2(q_emb)
    scores, indices = index.search(q_emb, k)
    return [chunks[idx] for idx in indices[0] if idx != -1]


# ==========================================================
# GEMINI LLM
# ==========================================================

def ask_gemini(gemini_client, context: str, question: str) -> str:
    prompt = f"""You are a helpful RAG assistant.

Use the provided context to answer the question.
If the context is insufficient, say: "I do not have enough information in the documents, but based on general knowledge..."

Context:
{context}

Question:
{question}

Answer:"""

    response = gemini_client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.3,
            max_output_tokens=500,
            thinking_config=types.ThinkingConfig(thinking_budget=0),
        ),
    )
    return response.text.strip()


# ==========================================================
# MAIN
# ==========================================================

def main() -> None:
    setup_nltk()
    gemini_client, hf_client = _make_clients()

    print("Loading documents...")
    chunks = load_documents()

    print("Computing embeddings...")
    embeddings = embed_texts(hf_client, chunks)

    print("Building FAISS index...")
    index = build_index(embeddings)

    print("\nRAG system ready. Type 'exit' to quit.\n")
    while True:
        question = input("Ask: ").strip()
        if question.lower() == "exit":
            break
        if not question:
            continue
        context = "\n".join(retrieve(question, hf_client, index, chunks))
        print("\n--- Context ---")
        print(context)
        print("\n--- Answer ---")
        print(ask_gemini(gemini_client, context, question))
        print()


if __name__ == "__main__":
    main()
