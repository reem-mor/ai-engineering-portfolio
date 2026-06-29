# Course Projects

End-to-end AI engineering work from the course archive. **Featured capstone** and **learning
iteration** live here; **flagship products** link out to their own repos.

| Project | Folder | Status | Stack | Tests |
|---------|--------|--------|-------|-------|
| **IncidentIQ** (capstone) | [`incident-assistant-rag/`](incident-assistant-rag/) | **Featured** — in archive | FastAPI · OpenAI · local FAISS · React · Docker | 90 (CI) |
| **Incident RAG (Bedrock)** | [`incident-rag-bedrock/`](incident-rag-bedrock/) | **Learning iteration** | Flask · Bedrock KB · React | 111 (CI) |
| **PITER AiOps** | [`piter-aiops/`](piter-aiops/) | **Pointer** → external repo | Flask · Bedrock **Agent** · tools · React | ~325 (external CI) |

## External flagships

| Project | Repo |
|---------|------|
| **PITER AiOps** | [reem-mor/piter-aiops](https://github.com/reem-mor/piter-aiops) |
| **course-assistant-bot** | [reem-mor/course-assistant-bot](https://github.com/reem-mor/course-assistant-bot) |
| **HINDSIGHT** | [reem-mor/hindsight](https://github.com/reem-mor/hindsight) |

Extraction runbooks: [`docs/extraction/`](../docs/extraction/).

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
