# Course Projects

End-to-end AI engineering work from the course archive. **Featured capstone** and **learning
iterations** live here; the **flagship agentic stack** is extraction-ready to its own repo.

| Project | Folder | Status | Stack | Tests |
|---------|--------|--------|-------|-------|
| **IncidentIQ** (capstone) | [`incident-assistant-rag/`](incident-assistant-rag/) | **Featured** — keep in archive | FastAPI · OpenAI · local FAISS · React · Docker | 90 (CI) |
| **Incident RAG (Bedrock)** | [`incident-rag-bedrock/`](incident-rag-bedrock/) | **Learning iteration** — Bedrock KB predecessor | Flask · Bedrock KB · React | 111 (CI) |
| **PITER AiOps** | [`piter-aiops/`](piter-aiops/) | **Extraction-ready** — flagship copy | Flask · Bedrock **Agent** · tools · React | ~325 (local) |

## External flagships (not duplicated here)

| Project | Repo |
|---------|------|
| **HINDSIGHT** | [reem-mor/hindsight](https://github.com/reem-mor/hindsight) |
| **PITER AiOps** (target) | [reem-mor/piter-aiops](https://github.com/reem-mor/piter-aiops) — *repo not created yet; see [`EXTRACTION.md`](piter-aiops/EXTRACTION.md)* |

Extraction runbooks: [`docs/extraction/`](../docs/extraction/).

## RAG progression (honest arc)

```text
incident-rag-bedrock  →  piter-aiops
  (managed Bedrock KB)     (Bedrock Agent + tools + memory)

incident-assistant-rag  — parallel capstone track (OpenAI + local FAISS, no AWS)
```

## Course handouts

Third-party assignment briefs are **not** in this repo — indexed in [`resources/MANIFEST.md`](../resources/MANIFEST.md).

## Submission

[`CONTRIBUTING.md`](../CONTRIBUTING.md) · [`docs/submission-checklist.md`](../docs/submission-checklist.md)
