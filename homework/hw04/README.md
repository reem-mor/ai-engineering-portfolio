# Homework 04 — Full RAG Application

**Status:** Scaffold only — **capstone reference:** [`projects/incident-assistant-rag/`](../../projects/incident-assistant-rag/)

The graded handout targets a standalone RAG web app. The full implementation lives in the
**IncidentIQ capstone** (FastAPI + OpenAI + FAISS + React, 90 tests). This folder keeps the
original Docker scaffold for syllabus traceability.

## Assignment

Build a complete Retrieval-Augmented Generation web application per the course handout:

[`resources/handouts/rag-application-homework-guidelines.docx`](../../resources/MANIFEST.md)

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

Application source (`app.py`, `requirements.txt`, templates, data pipeline) is not committed here.

## Where to review the full implementation

| Deliverable | Location |
|-------------|----------|
| **IncidentIQ capstone** | [`projects/incident-assistant-rag/`](../../projects/incident-assistant-rag/) |
| Flask RAG reference (lecture) | [`lectures/06_flask_advanced_rag/`](../../lectures/06_flask_advanced_rag/) |
| RAG progression notes | [`docs/rag-notes.md`](../../docs/rag-notes.md) |

## Related course material

- Lecture demos: [`lectures/04_nlp_rag/`](../../lectures/04_nlp_rag/)
- Submission checklist: [`docs/submission-checklist.md`](../../docs/submission-checklist.md)
