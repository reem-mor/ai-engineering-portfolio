# Repository Architecture

How [`ai-engineering-portfolio`](../../) is organized and why.

## Design principles

1. **Progressive complexity** — lectures → homework → projects
2. **Runnable artifacts** — each major folder has a README with run instructions
3. **Separation of concerns** — third-party IP in [`resources/MANIFEST.md`](../../resources/MANIFEST.md) only; code in `lectures/` and `homework/`; portfolio work in `projects/`
4. **Honest framing** — flagships extract to own repos; this archive links out via [`flagships/`](../../flagships/)
5. **Generated output stays untracked** — SPA bundles, `catboost_info/`, local indexes

## Top-level layout

```text
ai-engineering-portfolio/
├── README.md                 # Portfolio entry point (recruiters start here)
├── docs/                     # Meta-docs — start at docs/README.md
│   ├── SYLLABUS.md           # Canonical curriculum map
│   ├── setup.md              # Clone, venv, per-project deps
│   └── architecture/         # This file
├── lectures/                 # Lessons 01–11 (demos colocated)
├── homework/                 # Assignments hw01–hw07 (evidence colocated)
├── exercises/                # Lab index (links only — no duplicate code)
├── projects/                 # In-repo capstone + learning iteration ONLY
│   ├── incident-assistant-rag/   # Featured capstone (OpenAI + FAISS)
│   └── incident-rag-bedrock/     # Bedrock KB iteration
├── flagships/                # Pointers → external repos (PITER, HINDSIGHT, bot)
├── resources/MANIFEST.md     # Course slides/handouts (not committed — IP)
├── scripts/                  # setup-dev, MCP launcher, git-clone re-export
├── AGENTS.md / CLAUDE.md     # Cross-tool agent guidance
└── .github/workflows/ci.yml  # ruff + pytest matrix
```

## What lives where

| Folder | Contains | Does NOT contain |
|--------|----------|------------------|
| `lectures/` | Lesson notes + runnable demos | Graded submission evidence |
| `homework/` | Assignments + screenshots + SUBMISSION.md | Duplicate lecture code |
| `exercises/` | Navigation index only | Runnable code copies |
| `projects/` | End-to-end in-repo systems | Extracted flagship source trees |
| `flagships/` | README pointers + clone instructions | Application source code |
| `docs/` | Cross-cutting meta-docs | Course slide PDFs |

## Learning flow

See [`docs/SYLLABUS.md`](../SYLLABUS.md) and [`docs/diagrams/learning-path.mermaid`](../diagrams/learning-path.mermaid).

## Extraction status

| Product | In-archive pointer | External repo |
|---------|-------------------|---------------|
| PITER AiOps | [`flagships/piter-aiops/`](../../flagships/piter-aiops/) | [reem-mor/piter-aiops](https://github.com/reem-mor/piter-aiops) |
| course-assistant-bot | [`flagships/course-assistant-bot/`](../../flagships/course-assistant-bot/) | [reem-mor/course-assistant-bot](https://github.com/reem-mor/course-assistant-bot) |
| HINDSIGHT | [`flagships/hindsight/`](../../flagships/hindsight/) | [reem-mor/hindsight](https://github.com/reem-mor/hindsight) |

Runbooks: [`docs/extraction/README.md`](../extraction/README.md).

## Documentation map

| Question | Read |
|----------|------|
| Where do I start? | [`docs/README.md`](../README.md) |
| Full syllabus | [`SYLLABUS.md`](../SYLLABUS.md) |
| How do I run things? | [`setup.md`](../setup.md) |
| Screenshot index | [`screenshots/README.md`](../screenshots/README.md) |
| RAG progression | [`rag-notes.md`](../rag-notes.md) |
| Capstone architecture | [`projects/incident-assistant-rag/docs/`](../../projects/incident-assistant-rag/docs/) |

## Author

Re'em Mor — [github.com/reem-mor](https://github.com/reem-mor)
