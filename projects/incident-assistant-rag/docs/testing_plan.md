# Testing Plan

## Unit Tests

Unit tests cover document loading, cleaning, chunking, embeddings, FAISS, prompt building, RAG pipeline, severity classification, incident reasoning, and API validation.

## API Tests

API tests verify health, chat validation, incident validation, document listing, and error behavior.

## Evaluation Tests

The evaluation runner uses five questions:

1. Login failure after deployment.
2. Payment timeout and latency.
3. Database locks.
4. Structured incident analysis.
5. Irrelevant out-of-domain question.

## Manual Frontend Tests

Manual tests verify loading states, error messages, source cards, confidence display, indexing, chat, incident analysis, and upload.

## Docker Tests

Docker tests verify that the full application can run from localhost with Docker Compose.
