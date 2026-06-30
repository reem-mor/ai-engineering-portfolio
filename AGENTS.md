# AGENTS.md

Canonical guidance for **Cursor**, **Claude Code**, **Codex**, and other coding agents.
Tool-specific files source this document — do not duplicate long sections elsewhere.

**Owner context:** Re'em Mor — **AI Engineer × SRE** · production ops in regulated environments.

## What this repository is

`ai-engineering-portfolio` is a **course + learning archive** (Amdocs / Lab17 AI-Augmented Software
Engineering). Flagship products extract to their own repos — see root [`README.md`](README.md)
Featured work. Keep this tree lean, honest, and reproducible.

## Repository map

| Path | Role |
|------|------|
| `lectures/` | Lessons **01–11** — demos colocated with notes |
| `homework/` | Assignments **hw01–hw07** |
| `exercises/` | Lab index (links only) |
| `docs/` | Meta-docs · [`AGENT-TOOLING.md`](docs/AGENT-TOOLING.md) for MCP/skills/CI |
| `resources/MANIFEST.md` | Third-party slides — **not** in repo (IP) |
| `projects/` | [`projects/README.md`](projects/README.md) — capstone / learning iteration |
| `flagships/` | [`flagships/README.md`](flagships/README.md) — pointers to external repos (PITER, HINDSIGHT, bot) |
| `scripts/` | Dev bootstrap, MCP launcher, project extraction |

## Engineering conventions (2026)

| Area | Standard |
|------|----------|
| Python | **3.12** (`.python-version`) · pydantic v2 where used |
| Package mgmt | `pip -r requirements.txt` per folder; `uv` in extracted [course-assistant-bot](https://github.com/reem-mor/course-assistant-bot) |
| Lint | `ruff check .` — config in [`pyproject.toml`](pyproject.toml) |
| Tests | `pytest` per project; CI in [`.github/workflows/ci.yml`](.github/workflows/ci.yml) |
| Encoding | UTF-8 only — never UTF-16 |
| SPA | `app/static/spa/` gitignored — `cd frontend && npm run build` before Flask/Docker |
| Commits | Conventional commits; scoped diffs; **do not push** unless asked |
| Secrets | Env vars / `${env:VAR}` in MCP JSON — see [secrets rule](.cursor/rules/secrets-and-mcp-security.mdc) |

## Agent workflow

1. **Read** relevant README + [`docs/AGENT-TOOLING.md`](docs/AGENT-TOOLING.md) before editing.
2. **Audit** — understand scope; minimal diffs only in this archive (flagships live in external repos).
3. **Implement** minimal diff; match surrounding style.
4. **Verify** — `ruff check .` and project `pytest` for touched areas.
5. **Report** honestly if tests fail — never claim green when red.

### SRE-minded defaults

- Structured errors over silent failures; log context for ops paths.
- RAG: grounded answers, source attribution, **no-context refusal** — not hallucinated runbooks.
- AWS: `AWS_PROFILE` + least privilege; parameterize resource IDs in docs.
- Never run destructive prod workflows (n8n live flows, EC2 terminate) unless explicitly asked.

## MCP servers

Canonical config: [`.mcp.json`](.mcp.json). Cursor may also read gitignored `.cursor/mcp.json` for local overrides.

| Server | Use in this repo |
|--------|------------------|
| `course-tools` | Lecture 08 stdio demo |
| `playwright` | E2E / UI capture |
| `kaggle` | hw07 datasets |
| `aws-knowledge` | AWS documentation |
| `aws-api` / `bedrock-kb` | Bedrock / AWS labs & projects |
| `n8n-workflows` | hw06 / lecture 09 |
| `lovable` | Optional UI experiments |

Bootstrap: `python scripts/run-mcp-course-tools.py` · Full catalog: [`docs/AGENT-TOOLING.md`](docs/AGENT-TOOLING.md).

**Do not add MCP servers without a concrete repo usage.**

## Skills

Single library: [`.cursor/skills/`](.cursor/skills/) — read `SKILL.md` before applying.

| Skill | Use when |
|-------|----------|
| `repo-tooling` | MCP, env, CI, config file locations |
| `hw07-open-webui` | Homework 07 — Open WebUI KB, local tools server, RapidAPI |
| `mcp-integration` | New MCP server or auth debugging |
| `agent-development` | Agents, tools, prompts |
| `browser-use` | Playwright automation |
| `excalidraw-diagram` | Architecture diagrams |
| `frontend-design` | React/Vite UI |
| `skill-development` | Authoring skills |

## Dependencies

See [`REQUIREMENTS.md`](REQUIREMENTS.md) — root `requirements.txt` is the **course ML stack**;
use [`requirements-dev.txt`](requirements-dev.txt) for ruff/pytest only.

## Related files

| File | Purpose |
|------|---------|
| [`CLAUDE.md`](CLAUDE.md) | Claude Code entry (sources this file) |
| [`.env.example`](.env.example) | Sanitized env template |
| [`docs/setup.md`](docs/setup.md) | Human setup guide |
| [`.cursor/rules/`](.cursor/rules/) | Cursor agent rules |
