# RAG Pipeline

The RAG pipeline converts documents into searchable vectors and uses retrieved context to answer user questions.

## Chunking and Embeddings

Configured in `backend/app/core/config.py` and implemented in `backend/app/rag/chunker.py`:

| Setting | Default |
|---------|---------|
| Chunk size | **700** characters |
| Chunk overlap | **120** characters |
| Embedding model | `text-embedding-3-small` |
| Vector dimensions | **1536** |
| FAISS index | `IndexFlatIP` on L2-normalized vectors |

Chunks are split on sentence boundaries when possible to keep runbook steps intact.

## Ingestion Flow

```text
Document
  -> load text
  -> clean text
  -> split into chunks (700 / 120 overlap)
  -> generate embeddings
  -> store in FAISS
```

## Query Flow

1. User asks a question (UI or `POST /api/chat`)
2. Backend receives and validates the request
3. Query is embedded with the same model used at index time
4. FAISS returns top-k similar chunks
5. Chunks below the score threshold are dropped; if none remain, return refusal without LLM
6. Remaining context is injected into a strict grounded prompt
7. LLM generates the answer; response includes sources and metadata

```text
User question
  -> embed question
  -> search FAISS
  -> filter weak matches
  -> build grounded prompt
  -> generate answer
  -> return answer and sources
```

## Hallucination Controls

The project reduces hallucination with:

- strict prompts (`prompt_builder.py` — use only provided context)
- score threshold filtering (`RETRIEVAL_SCORE_THRESHOLD`, default **0.25**)
- no-context response (fixed message, **no LLM call** when no chunk passes the filter)
- returned sources and `retrieved_chunks` for transparency
- `confidence` and `used_context` fields on every answer
- irrelevant question evaluation (Test 5 in `evaluation/evaluation_results.md`)

See the **Query pipeline and hallucination controls** section in the [main README](../README.md) for the decision flow diagram and UI behavior (**Context · Grounded** vs **Context · No match**).

## Why Custom Pipeline

A custom pipeline is used instead of hiding everything behind a framework. This makes the project easier to explain and proves understanding of loading, cleaning, chunking, embedding, retrieval, prompting, and answer generation.
