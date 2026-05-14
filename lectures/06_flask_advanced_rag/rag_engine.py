"""
RAG engine: document loading, Hugging Face embeddings, FAISS search, Gemini LLM.

Required environment variables:
    GEMINI_API_KEY  — Google AI Studio key
    HF_TOKEN        — HuggingFace access token (with Inference API access)
"""

import os
import time
import threading

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

DATA_FOLDER = os.path.join(os.path.dirname(__file__), "data")
HF_EMBEDDING_MODEL = "ibm-granite/granite-embedding-97m-multilingual-r2"
GEMINI_MODEL = "gemini-2.0-flash"
TOP_K = 3
BATCH_SIZE = 8


def _log(msg: str) -> None:
    print(f"[rag] {msg}", flush=True)


# ==========================================================
# NLTK SETUP
# ==========================================================

def setup_nltk() -> None:
    nltk.download("punkt", quiet=True)
    nltk.download("punkt_tab", quiet=True)


# ==========================================================
# DOCUMENT LOADING
# ==========================================================

def load_documents(folder: str = DATA_FOLDER) -> tuple[list[str], list[str]]:
    """Load .txt files from folder, split into sentences. Returns (chunks, sources)."""
    if not os.path.exists(folder):
        raise FileNotFoundError(
            f"Data folder '{folder}' not found. "
            "Create it and add .txt files, then restart the app."
        )

    chunks, sources = [], []
    for file_name in sorted(os.listdir(folder)):
        if not file_name.endswith(".txt"):
            continue
        with open(os.path.join(folder, file_name), "r", encoding="utf-8") as f:
            text = f.read()
        for sentence in sent_tokenize(text):
            sentence = sentence.strip()
            if sentence:
                chunks.append(sentence)
                sources.append(file_name)

    if not chunks:
        raise ValueError(f"No text found in '{folder}'.")
    return chunks, sources


# ==========================================================
# EMBEDDINGS (HuggingFace)
# ==========================================================

def _normalize_embedding_output(raw_output, expected_count: int) -> np.ndarray:
    arr = np.array(raw_output, dtype="float32")
    if arr.ndim == 1:
        arr = arr.reshape(1, -1)
    elif arr.ndim == 2:
        if arr.shape[0] != expected_count and expected_count == 1:
            arr = arr.mean(axis=0, keepdims=True)
    elif arr.ndim == 3:
        arr = arr.mean(axis=1)
    else:
        raise ValueError(f"Unexpected embedding dimensions: {arr.ndim}")
    if arr.shape[0] != expected_count:
        raise ValueError(
            f"Embedding count mismatch: expected {expected_count}, got {arr.shape[0]}"
        )
    return arr.astype("float32")


# ==========================================================
# RAG ENGINE
# ==========================================================

class RAGEngine:
    """Encapsulates the full RAG pipeline as a single in-memory object."""

    def __init__(self, data_folder: str = DATA_FOLDER) -> None:
        self.data_folder = data_folder
        self.chunks: list[str] = []
        self.sources: list[str] = []
        self.index = None
        self.ready = False
        self.status = "not_initialised"
        self.progress: dict = {"current": 0, "total": 0}
        self._lock = threading.Lock()

        gemini_key = os.environ.get("GEMINI_API_KEY", "")
        hf_token = os.environ.get("HF_TOKEN", "")
        if not gemini_key:
            raise RuntimeError(
                "GEMINI_API_KEY environment variable is not set. "
                "Copy .env.example to .env and fill in your keys."
            )
        if not hf_token:
            raise RuntimeError(
                "HF_TOKEN environment variable is not set. "
                "Copy .env.example to .env and fill in your keys."
            )

        self.gemini_client = genai.Client(api_key=gemini_key)
        self.hf_client = InferenceClient(provider="hf-inference", api_key=hf_token)

    # ---------- initialisation ----------

    def initialise(self) -> None:
        """Load docs, build embeddings, build FAISS index. Idempotent."""
        with self._lock:
            if self.ready:
                return

            self.status = "downloading_nltk"
            _log("Setting up NLTK tokenizer...")
            setup_nltk()

            self.status = "loading_documents"
            _log(f"Loading documents from '{self.data_folder}'...")
            self.chunks, self.sources = load_documents(self.data_folder)
            _log(f"Loaded {len(self.chunks)} sentences from {len(set(self.sources))} file(s).")

            self.status = "embedding_documents"
            _log("Embedding documents via HuggingFace...")
            embeddings = self._embed_texts(self.chunks)

            self.status = "building_index"
            _log("Building FAISS index...")
            self.index = self._create_faiss_index(embeddings)

            self.ready = True
            self.status = "ready"
            _log(f"Ready. {self.index.ntotal} vectors indexed.")

    # ---------- embeddings ----------

    def _hf_feature_extraction_with_retries(
        self, inputs, expected_count: int, max_retries: int = 5
    ) -> np.ndarray:
        for attempt in range(1, max_retries + 1):
            try:
                result = self.hf_client.feature_extraction(inputs, model=HF_EMBEDDING_MODEL)
                return _normalize_embedding_output(result, expected_count)
            except Exception as exc:
                _log(f"Embedding attempt {attempt}/{max_retries} failed: {exc}")
                if attempt == max_retries:
                    raise
                wait = attempt * 3
                _log(f"Retrying in {wait}s...")
                time.sleep(wait)
        raise RuntimeError("Embedding failed after all retries.")

    def _embed_texts(self, texts: list[str], batch_size: int = BATCH_SIZE) -> np.ndarray:
        all_embeddings = []
        total_batches = (len(texts) + batch_size - 1) // batch_size
        self.progress = {"current": 0, "total": total_batches}
        for start in range(0, len(texts), batch_size):
            batch = texts[start:start + batch_size]
            batch_num = start // batch_size + 1
            _log(f"  batch {batch_num}/{total_batches} ({len(batch)} items)...")
            all_embeddings.append(
                self._hf_feature_extraction_with_retries(batch, len(batch))
            )
            self.progress = {"current": batch_num, "total": total_batches}
        return np.vstack(all_embeddings).astype("float32")

    def _embed_query(self, query: str) -> np.ndarray:
        return self._hf_feature_extraction_with_retries(query, expected_count=1).astype("float32")

    # ---------- FAISS ----------

    @staticmethod
    def _create_faiss_index(embeddings: np.ndarray) -> faiss.IndexFlatIP:
        faiss.normalize_L2(embeddings)
        index = faiss.IndexFlatIP(embeddings.shape[1])
        index.add(embeddings)
        return index

    def retrieve(self, query: str, k: int = TOP_K) -> list[dict]:
        """Return top-k chunks with score and source filename."""
        if not self.ready:
            raise RuntimeError("RAG engine is not ready yet.")
        q_emb = self._embed_query(query)
        faiss.normalize_L2(q_emb)
        scores, indices = self.index.search(q_emb, k)
        return [
            {
                "text": self.chunks[idx],
                "source": self.sources[idx] if idx < len(self.sources) else None,
                "score": float(score),
            }
            for score, idx in zip(scores[0], indices[0])
            if idx != -1
        ]

    # ---------- Gemini ----------

    def ask_gemini(self, context: str, question: str, history: list[dict] | None = None) -> str:
        history_text = ""
        if history:
            history_text = "\n".join(
                f"{'User' if m['role'] == 'user' else 'Assistant'}: {m['content']}"
                for m in history
            )

        prompt = f"""You are a helpful RAG assistant.

Use the provided context and conversation history to answer the user's latest question.

Rules:
1. Answer using only the provided context.
2. If the context is insufficient, say: "I do not have enough information in the documents, but based on general knowledge..."
3. Keep the answer simple and clear.
4. Do not invent facts from the documents.
5. Use conversation history only to resolve references like "it" or "the previous one".

Conversation so far:
{history_text if history_text else "(no previous messages)"}

Context retrieved from documents:
{context}

User's latest question:
{question}

Answer:"""

        response = self.gemini_client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.3,
                max_output_tokens=500,
                thinking_config=types.ThinkingConfig(thinking_budget=0),
            ),
        )
        return response.text.strip()

    # ---------- high-level helper ----------

    def answer(self, question: str, history: list[dict] | None = None, k: int = TOP_K) -> dict:
        """Full retrieve + generate flow."""
        retrieved = self.retrieve(question, k=k)
        context = "\n".join(item["text"] for item in retrieved)
        answer_text = self.ask_gemini(context=context, question=question, history=history or [])
        return {"answer": answer_text, "context": retrieved}
