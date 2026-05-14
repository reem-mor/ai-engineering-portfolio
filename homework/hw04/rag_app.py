"""
HW04 — RAG Application starter scaffold.

Your task: implement the TODO sections below to build a working RAG pipeline.

Pipeline:
  1. load_corpus()   → read .txt files → split into sentence chunks
  2. embed_corpus()  → convert chunks to dense vectors via HuggingFace
  3. build_index()   → load vectors into FAISS for fast similarity search
  4. retrieve()      → embed query, find top-k matching chunks
  5. generate()      → pass retrieved context + question to Gemini → answer
  6. main()          → interactive Q&A loop

Reference implementations:
  - CLI demo:   lectures/04_nlp_rag/demos/rag_example.py
  - Web app:    lectures/06_flask_advanced_rag/rag_engine.py

Required environment variables:
    GEMINI_API_KEY   — https://aistudio.google.com/
    HF_TOKEN         — https://huggingface.co/settings/tokens
"""

import os
from pathlib import Path

# ---------------------------------------------------------------------------
# TODO 1: Import the libraries you need.
# Hints: faiss, numpy, nltk (sent_tokenize), google.genai, huggingface_hub
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# CONFIGURATION — adjust as needed
# ---------------------------------------------------------------------------

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
HF_TOKEN = os.environ.get("HF_TOKEN", "")

DATA_FOLDER = str(Path(__file__).parent.parent.parent / "lectures" / "04_nlp_rag" / "data")
HF_EMBEDDING_MODEL = "ibm-granite/granite-embedding-97m-multilingual-r2"
GEMINI_MODEL = "gemini-2.0-flash"
TOP_K = 3


# ---------------------------------------------------------------------------
# TODO 2: load_corpus(folder) → list[str]
#
# - List all .txt files in `folder`
# - Read each file and split it into sentences using sent_tokenize
# - Return a flat list of non-empty sentence strings (chunks)
# ---------------------------------------------------------------------------

def load_corpus(folder: str = DATA_FOLDER) -> list[str]:
    raise NotImplementedError("Implement load_corpus()")


# ---------------------------------------------------------------------------
# TODO 3: embed_corpus(chunks) → np.ndarray  shape: (N, dim)
#
# - Use InferenceClient(provider="hf-inference", api_key=HF_TOKEN)
# - Call client.feature_extraction(chunks, model=HF_EMBEDDING_MODEL)
# - Convert output to a float32 numpy array of shape (N, embedding_dim)
# - Handle the case where the API returns a 3-D array (batch × tokens × dim)
#   by averaging over the token dimension
# ---------------------------------------------------------------------------

def embed_corpus(chunks: list[str]):
    raise NotImplementedError("Implement embed_corpus()")


# ---------------------------------------------------------------------------
# TODO 4: build_index(embeddings) → faiss.IndexFlatIP
#
# - L2-normalise the embeddings with faiss.normalize_L2()
# - Create faiss.IndexFlatIP(embedding_dim)
# - Add the embeddings to the index
# - Return the index
# ---------------------------------------------------------------------------

def build_index(embeddings):
    raise NotImplementedError("Implement build_index()")


# ---------------------------------------------------------------------------
# TODO 5: retrieve(query, index, chunks) → list[str]
#
# - Embed the query string (single text, not a list)
# - L2-normalise the query embedding
# - Call index.search(query_embedding, TOP_K) → scores, indices
# - Return the corresponding text chunks (skip index == -1)
# ---------------------------------------------------------------------------

def retrieve(query: str, index, chunks: list[str]) -> list[str]:
    raise NotImplementedError("Implement retrieve()")


# ---------------------------------------------------------------------------
# TODO 6: generate(question, context_chunks) → str
#
# - Build a prompt that includes the retrieved context and the question
# - Call Gemini via genai.Client(api_key=GEMINI_API_KEY)
# - Return the model's answer as a string
# ---------------------------------------------------------------------------

def generate(question: str, context_chunks: list[str]) -> str:
    raise NotImplementedError("Implement generate()")


# ---------------------------------------------------------------------------
# main() — wire everything together
# ---------------------------------------------------------------------------

def main() -> None:
    if not GEMINI_API_KEY:
        raise RuntimeError("Set the GEMINI_API_KEY environment variable.")
    if not HF_TOKEN:
        raise RuntimeError("Set the HF_TOKEN environment variable.")

    print("Loading corpus...")
    chunks = load_corpus()
    print(f"  {len(chunks)} chunks loaded.")

    print("Embedding corpus...")
    embeddings = embed_corpus(chunks)
    print(f"  Embeddings shape: {embeddings.shape}")

    print("Building FAISS index...")
    index = build_index(embeddings)
    print(f"  {index.ntotal} vectors indexed.")

    print("\nRAG system ready. Type 'exit' to quit.\n")
    while True:
        question = input("Ask: ").strip()
        if question.lower() == "exit":
            break
        if not question:
            continue
        top_chunks = retrieve(question, index, chunks)
        answer = generate(question, top_chunks)
        print(f"\nAnswer: {answer}\n")


if __name__ == "__main__":
    main()
