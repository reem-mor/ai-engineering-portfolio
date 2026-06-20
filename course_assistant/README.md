# OzVaRoah AI Agent Course Bot

A bilingual (Hebrew / English) **Telegram** assistant for students of the *Oz VeRuach*
(עוז ורוח) AI-Augmented Software Engineering course (Amdocs Learning Center, Cohort 1).

> **Source of truth:** [`docs/source/MVP_Spec.docx`](docs/source/MVP_Spec.docx). The MVP
> governs scope. This build targets the MVP exactly: Drive retrieval + RAG + homework email.

## What it does (MVP scope)

- **Drive retrieval** — fetch homework files, instructor code-file links, and recording
  links from the course Google Drive, so students don't have to dig through Drive.
- **Course materials Q&A (RAG)** — answer questions from the ingested Drive materials,
  with a pointer to the source.
- **Homework submission** — explain the exact submission procedure, then draft a
  submission email and **send it only after the student approves** (To: Alex, CC: Sagy,
  using the prescribed subject/body format).

Guardrails: never fabricate course facts — answer from Drive/materials or say so; cite
sources; stay on course topics.

## Tech stack

- Python 3.11+, `src/` layout, typed, docstrings.
- **LangGraph** agent orchestration.
- **RAG** over a local **Chroma** store (behind a `VectorStore` interface; Pinecone is a
  swappable upgrade).
- **LLM**: Claude Sonnet by default (`claude-sonnet-4-6`), provider/model configurable via
  env. Mocked in tests — no paid calls in CI.
- **Telegram** interface (thin adapter over the agent core).
- Config via `.env` + `pydantic-settings`. Secrets never hardcoded or committed.

## Architecture

> A Mermaid architecture diagram lands in Phase 6 (Hardening), once the tools, RAG
> pipeline, agent graph, and Telegram interface are all in place.

## Project layout

```
course_assistant/
├── src/course_assistant/
│   ├── config/        # typed pydantic-settings (Phase 1)
│   ├── drive/         # read-only Drive access (Phase 2)
│   ├── rag/           # vector-store interface + ingestion/retrieval (Phase 1/3)
│   ├── tools/         # agent tools (Phases 2–4)
│   ├── agent/         # LangGraph agent graph (Phase 5)
│   └── interface/     # Telegram adapter (Phase 5)
├── tests/             # pytest (external services mocked)
├── docs/source/       # MVP spec, syllabus, homework procedure (source of truth)
└── data/              # local Chroma store + structured seeds
```

## Setup

```bash
cd course_assistant
cp .env.example .env          # then fill in secrets
uv venv && uv pip install -e ".[dev]"
```

## Run

### Build / refresh the RAG index

```bash
uv run course-assistant-ingest   # walks the Drive materials → chunks → embeds → Chroma
```

Ingestion is **idempotent** — it clears and rebuilds the local index each run, so
re-run it whenever new lessons or files are uploaded. It reads Drive **read-only**
and never downloads recordings (videos).

### Run the bot

```bash
uv run course-assistant-bot   # Telegram long-polling
```

Free-text questions go to the LangGraph agent (recordings/slides/homework/code by
lesson, course-content Q&A, how to submit). `/submit` runs the guided homework
flow, which previews the email and **sends only after you reply 'confirm'**.

## How to add new course materials

1. Upload the file to the course Drive under the right `Lesson N` folder
   (`מצגות/Lesson N` for slides/homework/code, `הקלטות/Lesson N` for recordings).
2. Re-run `uv run course-assistant-ingest` to re-index. New slides, homework, and
   code files become searchable via `search_course_materials`; the new links are
   served immediately by `drive_lookup` (no re-index needed for link lookups).

Supported material types for RAG: PDF, Word (`.docx`), PowerPoint (`.pptx`), and
plain-text/code files. Recordings are surfaced as links only (never ingested).

## Tests

```bash
uv run pytest          # all external services mocked — no live network calls
uv run ruff check .
uv run mypy
```

## Environment variables

See [`.env.example`](.env.example) for the full, documented contract. Every secret is an
environment variable; nothing is hardcoded.

## How to add new course materials

> Documented in Phase 3, once the re-runnable ingestion command exists.

## Build phases

| Phase | Scope | Status |
|-------|-------|--------|
| 1 | Scaffold & config | ✅ |
| 2 | Drive retrieval (`drive_lookup`) | ✅ |
| 3 | RAG pipeline (`search_course_materials`) | ✅ |
| 4 | Homework submission (explain + email send-after-approval) | ✅ |
| 5 | Agent graph (LangGraph) + Telegram interface | ✅ |
| 6 | Hardening (tests, Dockerfile, README + Mermaid) | ⏳ |
