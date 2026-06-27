# AGENTS.md

Canonical, cross-tool guidance for AI coding agents working in this repository
(Claude Code, Cursor, Codex, and others). Tool-specific files source this one:
`CLAUDE.md` includes it via `@AGENTS.md`. Keep agent guidance here — not duplicated
across tool configs.

## What this repository is

`amdocs-ai-course` is **Re'em Mor's course + learning archive** for the Amdocs / Lab17
AI-Augmented Software Engineering program. It is *not* the home of the flagship projects —
those live in their own repositories (see "Featured work" in the root `README.md`). Treat
this repo as a teaching/portfolio archive: keep it lean, honest, and reproducible.

## Repository map

- `lectures/` — per-lesson write-ups and runnable demos (01–09).
- `homework/` — graded assignments (hw01–hw06).
- `exercises/` — small standalone labs.
- `docs/` — course docs, architecture notes, audit, security remediation.
- `resources/` — manifest only; third-party Amdocs slides are **not** redistributed here.
- `projects/` — course projects:
  - `incident-assistant-rag/` — capstone (FastAPI + OpenAI + local FAISS).
  - `incident-rag-bedrock/` — earlier learning iteration (Flask + AWS Bedrock KB).
  - `piter-aiops/` — flagship (Bedrock **agent** + RAG); slated to extract to its own repo.
- `oz_veruach_bot/` — standalone async Telegram bot (its own product; **do not refactor**).

## Conventions

- **Python 3.12** across the repo (`.python-version`). Prefer `uv` where a project already
  uses it (`oz_veruach_bot`); plain `pip -r requirements.txt` elsewhere.
- **Lint/format:** `ruff` (config in root `pyproject.toml`). Run `ruff check .` before commits.
- **Tests:** `pytest` per project. CI (`.github/workflows/ci.yml`) runs ruff + pytest.
- **Encoding:** all text files UTF-8. Never reintroduce UTF-16.
- Keep diffs scoped and reviewable; use clear, logically grouped commits.

## Secrets & security (always applies)

- **Never hardcode secrets** (API keys, tokens, AWS keys) in code, configs, or MCP JSON.
  Reference them via environment-variable interpolation (`${env:VAR}`) or a gitignored
  `.env`. Only sanitized `.env.example` files are committed.
- For AWS, prefer `AWS_PROFILE` over raw access keys.
- Do not commit live infrastructure identifiers (Bedrock KB/agent IDs, EC2 instance IDs,
  public hostnames) into public-facing docs; parameterize them.
- See `.cursor/rules/secrets-and-mcp-security.mdc` for the full rule.

## Skills

The canonical agent **skill library lives in `.cursor/skills/`** (single source of truth):
`agent-development`, `browser-use`, `excalidraw-diagram`, `frontend-design`,
`mcp-integration`, `skill-development`. Do not fork a second copy under `.agents/`.

## MCP servers

Project MCP config is in `.mcp.json` (canonical) and mirrored in `.cursor/mcp.json` for
Cursor. Only integrations actually used by this repo are configured: `lovable`,
`n8n-workflows`, `aws-api`, `bedrock-kb`, `aws-knowledge`, `playwright`. All credentials
use env interpolation. Do not add servers without a usage.
