# AGENTS.md — Oz Veruach Bot

Standalone Telegram bot product. **Do not refactor** core architecture during drive-by edits.

## Conventions

- **Python 3.12+** managed with **uv** (`pyproject.toml`, `uv.lock`)
- **Strict typing** — mypy + ruff; match existing patterns
- **Tests** — `uv run pytest`; keep business logic deterministic
- **Secrets** — `.env` gitignored; Telegram/OpenAI keys via env only

## Scope guard

This is a shipped product, not coursework. Avoid coupling to the course archive or unrelated projects.
