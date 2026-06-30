# Repository Structure

How this archive is organized for reviewers (teachers, employers, collaborators).

> **On GitHub you see ~8 content folders.** Your local clone may also show `.venv/`, caches, and tool folders — those are gitignored and not part of the portfolio.

## Committed layout (what reviewers see)

```text
ai-engineering-portfolio/
│
├── README.md                 ← Start here (portfolio entry)
├── AGENTS.md                 ← AI agent guidance (Cursor, Claude Code, Codex)
├── CONTRIBUTING.md           ← Homework submission workflow
├── pyproject.toml            ← Root ruff + pytest config
├── requirements-dev.txt      ← CI tools (ruff, pytest) — install first
├── requirements.txt          ← Full course ML stack (optional, heavy)
│
├── docs/                     ← All meta-documentation
│   ├── README.md             ← Documentation hub
│   ├── SYLLABUS.md           ← Canonical curriculum (lectures + homework)
│   ├── STRUCTURE.md          ← This file
│   ├── setup.md              ← Clone, venv, bootstrap
│   └── architecture/         ← Design rationale
│
├── lectures/01–11/           ← Lesson notes + runnable demos (code stays here)
├── homework/hw01–07/         ← Graded work + screenshots + SUBMISSION.md
├── exercises/                ← Lab index → links into lectures/homework
│
├── projects/                 ← In-repo end-to-end work ONLY
│   ├── incident-assistant-rag/     Featured capstone (FastAPI + FAISS)
│   └── incident-rag-bedrock/       Bedrock KB learning iteration
│
├── flagships/                ← Pointers to external production repos
│   ├── piter-aiops/                → github.com/reem-mor/piter-aiops
│   ├── course-assistant-bot/       → github.com/reem-mor/course-assistant-bot
│   └── hindsight/                  → github.com/reem-mor/hindsight
│
├── resources/MANIFEST.md     ← Course slides/handouts index (PDFs not committed)
└── scripts/                  ← setup-dev.ps1, MCP launcher, git-clone re-export
```

## Design rules

| Rule | Rationale |
|------|-----------|
| **Code stays next to its lesson** | Stable import paths; demos colocated with README |
| **`projects/` = in-archive work only** | Flagships live in standalone GitHub repos |
| **`flagships/` = pointers only** | No duplicate source trees in the learning archive |
| **`docs/` = cross-cutting meta** | One syllabus, one setup guide, one architecture doc |
| **`exercises/` = thin index** | Avoid duplicating code; link to lecture folders |
| **Evidence colocated** | Screenshots live in `homework/hwXX/` or `projects/*/screenshots/` |

## Local-only folders (not on GitHub)

These may appear in VS Code but are **gitignored**:

| Folder | Purpose |
|--------|---------|
| `.venv/` | Python virtual environment |
| `.pytest_cache/`, `.ruff_cache/` | Test/lint caches |
| `catboost_info/` | ML training artifacts (lecture 10) |
| `.firecrawl/`, `.playwright-mcp/` | Tool session caches |
| `.agents/` | Duplicate skill mirror — use `.cursor/skills/` |
| `data/` (repo root) | Local Chroma/vector DB experiments |
| `projects/piter-aiops/` | **Do not keep** — clone [piter-aiops](https://github.com/reem-mor/piter-aiops) separately |

Clean local clutter:

```powershell
.\scripts\clean-workspace.ps1
```

## Dependency strategy

| File | Install when |
|------|--------------|
| `requirements-dev.txt` | Always (CI parity) |
| `requirements.txt` | Full lecture ML stack (torch, spacy, …) |
| `projects/*/requirements.txt` | Running that project only |

Details: [`REQUIREMENTS.md`](../REQUIREMENTS.md)

## Navigation by audience

| Audience | Path |
|----------|------|
| Recruiter | [`README.md`](../README.md) → [`flagships/`](flagships/) |
| Teacher / grader | [`docs/SYLLABUS.md`](SYLLABUS.md) → [`homework/`](homework/) |
| Technical reviewer | [`projects/incident-assistant-rag/`](../projects/incident-assistant-rag/) |
| Student | [`docs/setup.md`](setup.md) → [`lectures/01_jupyter_python_basics/`](../lectures/01_jupyter_python_basics/) |

## Related

- [`architecture/repository-architecture.md`](architecture/repository-architecture.md) — design principles
- [`docs/README.md`](README.md) — full documentation index
