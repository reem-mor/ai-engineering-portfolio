# Homework 04 — Full RAG Application

**Status:** In progress

## Assignment

Build a complete Retrieval-Augmented Generation web application per the course handout:

[`resources/handouts/rag-application-homework-guidelines.docx`](../../resources/handouts/rag-application-homework-guidelines.docx)

## Requirements summary

1. Choose a meaningful topic (professional or personal interest)
2. Build a knowledge base and index with FAISS
3. Implement retrieval + LLM generation with grounding rules
4. Deliver a working web interface
5. Validate with test questions, including edge cases and irrelevant queries

## Current contents

```text
hw04/
├── README.md           # this file
└── my-rag-app/
    ├── Dockerfile      # container starter
    └── .dockerignore
```

Application source (`app.py`, `requirements.txt`, templates, data pipeline) is not yet committed.

## Suggested next steps

1. Scaffold Flask or FastAPI app under `my-rag-app/`
2. Add `requirements.txt` matching Dockerfile `COPY` expectations
3. Implement FAISS indexing and RAG query endpoint
4. Add README run instructions and validation questions
5. Run through [`docs/submission-checklist.md`](../../docs/submission-checklist.md)

## Related course material

- Lecture demos: [`lectures/04_nlp_rag/`](../../lectures/04_nlp_rag/)
- Flask RAG reference: [`lectures/06_flask_advanced_rag/`](../../lectures/06_flask_advanced_rag/)
- RAG notes: [`docs/rag-notes.md`](../../docs/rag-notes.md)
- Capstone reference (read-only): [`projects/incident-assistant-rag/`](../../projects/incident-assistant-rag/)
