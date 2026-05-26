# Code Review Checklist

## Architecture

- Frontend and backend are separated.
- Backend owns API keys and AI calls.
- RAG logic is separated into loader, cleaner, chunker, embeddings, vector store, retriever, prompt builder, and generator.
- Incident reasoning is separate from normal chat.
- Supabase is optional and cannot break the main RAG flow.

## Error Handling

- Empty uploads are rejected.
- Unsupported file types are rejected.
- Large uploads are rejected.
- Empty extracted text raises a clear error.
- Missing FAISS index returns a friendly message.
- Invalid top_k is rejected by Pydantic.
- Bad JSON from the LLM uses a fallback response.
- Database errors do not block user answers.

## Retrieval Quality

- Text is cleaned before chunking.
- Chunks use overlap to preserve context.
- Search results include score and source file.
- Low-score chunks are filtered.
- No-context answers avoid hallucination.

## Security

- `.env` is ignored by Git.
- API keys are never sent to the frontend.
- Uploaded files are renamed with UUID.
- Supabase service role key stays only in the backend.

## Demo Readiness

- Sample documents exist.
- Index Sample Documents works.
- RAG Chat returns sources.
- Incident Analysis returns structured output.
- Docker Compose runs the app from localhost.
