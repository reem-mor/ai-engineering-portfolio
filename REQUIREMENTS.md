# Requirements strategy

How Python dependencies are organized in this archive (2026).

## Tiers

| File | Purpose | When to install |
|------|---------|-----------------|
| [`requirements-dev.txt`](../requirements-dev.txt) | **ruff**, **pytest** — CI and agent workflows | Always in root `.venv` |
| [`requirements.txt`](../requirements.txt) | Course lecture stack (NLP, Flask, torch, FAISS, …) | Full course / lecture demos |
| Per-project `requirements.txt` | Capstone, homework, lectures | `cd` into that folder only |

**Rule:** Do not install the heavy root `requirements.txt` into every subproject. Each capstone and homework folder owns its own lockfile.

## Per-area entry points

| Area | Dependencies |
|------|----------------|
| CI lint | `pip install ruff` (see [`.github/workflows/ci.yml`](../.github/workflows/ci.yml)) |
| CI tests | Each matrix dir's `requirements.txt` |
| [`lectures/08_mcp/`](../lectures/08_mcp/requirements.txt) | MCP demo server (`course-tools` MCP) |
| [`homework/hw07/`](homework/hw07/) | Open WebUI + live tools server | [`requirements.txt`](homework/hw07/requirements.txt) |
| [`projects/incident-assistant-rag/backend/`](../projects/incident-assistant-rag/backend/requirements.txt) | Capstone API |
| [`projects/incident-rag-bedrock/`](../projects/incident-rag-bedrock/requirements.txt) | Bedrock iteration |
| **PITER AiOps** (external) | [reem-mor/piter-aiops](https://github.com/reem-mor/piter-aiops) |
| **course-assistant-bot** (external) | [reem-mor/course-assistant-bot](https://github.com/reem-mor/course-assistant-bot) — **uv** + `pyproject.toml` |

## Python version

**3.12** everywhere — see [`.python-version`](../.python-version).

## Encoding

All requirement files must be **UTF-8**. Never commit UTF-16 `requirements.txt`.

## Virtual environments

| Path | Scope |
|------|--------|
| `.venv/` (repo root) | Course work + dev tools |
| `lectures/*/.venv` | Optional per-lecture isolation |
| `projects/*/.venv` | Per-project (recommended for capstones) |

All `venv` paths are gitignored.

## Node.js

Frontends and Playwright e2e use local `package.json` + `npm ci`. Never commit `node_modules/`.

## Quick bootstrap

```powershell
.\scripts\setup-dev.ps1
```

See [`docs/setup.md`](setup.md) and [`docs/AGENT-TOOLING.md`](AGENT-TOOLING.md).
