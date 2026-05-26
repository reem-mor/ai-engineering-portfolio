# Edge Cases

## Document Edge Cases

- Empty TXT or MD file.
- CSV without headers.
- PDF with no extractable text.
- Empty DOCX.
- Unsupported extension.
- File larger than maximum upload size.

## RAG Edge Cases

- User asks before indexing documents.
- User asks an empty question.
- User asks a question outside the knowledge base.
- FAISS index and metadata count mismatch.
- Query embedding dimension mismatch.
- Low similarity scores.

## Incident Edge Cases

- Short or unclear incident description.
- Missing affected service.
- Missing environment.
- No retrieved context.
- LLM returns invalid JSON.
- Severity estimate differs from retrieved context.

## Frontend Edge Cases

- Backend unavailable.
- Indexing fails.
- Upload fails.
- Empty form submit.
- Large file selected.
