# Course Projects

End-to-end AI engineering work from the course archive. **Featured capstone** and **learning
iteration** live here; **flagship products** link out via [`flagships/`](../flagships/).

| Project | Folder | Status | Stack | Tests |
|---------|--------|--------|-------|-------|
| **IncidentIQ** (capstone) | [`incident-assistant-rag/`](incident-assistant-rag/) | **Featured** — in archive | FastAPI · OpenAI · local FAISS · React · Docker | 90 (CI) |
| **Incident RAG (Bedrock)** | [`incident-rag-bedrock/`](incident-rag-bedrock/) | **Learning iteration** | Flask · Bedrock KB · React | 111 (CI) |

## External flagships

All pointers and clone instructions: [`flagships/README.md`](../flagships/README.md)

| Project | Repo |
|---------|------|
| **PITER AiOps** | [reem-mor/piter-aiops](https://github.com/reem-mor/piter-aiops) |
| **course-assistant-bot** | [reem-mor/course-assistant-bot](https://github.com/reem-mor/course-assistant-bot) |
| **HINDSIGHT** | [reem-mor/hindsight](https://github.com/reem-mor/hindsight) |

Legacy redirect: removed — use [`flagships/piter-aiops/`](../flagships/piter-aiops/) only.

Extraction runbooks: [`docs/extraction/`](../docs/extraction/)

## RAG progression (honest arc)

```text
incident-rag-bedrock  →  piter-aiops (external)
  (managed Bedrock KB)     (Bedrock Agent + tools + memory)

incident-assistant-rag  — parallel capstone track (OpenAI + local FAISS, no AWS)
```

## Course handouts

Third-party assignment briefs are **not** in this repo — indexed in [`resources/MANIFEST.md`](../resources/MANIFEST.md).

## Submission

[`CONTRIBUTING.md`](../CONTRIBUTING.md) · [`docs/submission-checklist.md`](../docs/submission-checklist.md)
