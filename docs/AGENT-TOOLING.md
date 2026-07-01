# Agent & MCP tooling (2026)

Single guide for **Cursor**, **Claude Code**, **Codex**, and other agents working in this repo.
Canonical agent rules: [`AGENTS.md`](../AGENTS.md) · Security: [`.cursor/rules/secrets-and-mcp-security.mdc`](../.cursor/rules/secrets-and-mcp-security.mdc).

## One-time setup

```powershell
# From repo root (Windows)
.\scripts\setup-dev.ps1

# macOS / Linux
./scripts/setup-dev.sh
```

This creates root `.venv`, installs `requirements-dev.txt`, copies `.env.example` → `.env` if missing, and installs lecture-08 MCP deps.

### Environment

1. Copy [`.env.example`](../.env.example) → `.env` (gitignored).
2. Fill only the keys for what you run — never commit `.env`.
3. AWS: use `AWS_PROFILE` + SSO; no static keys in MCP JSON.

### MCP in Cursor

| Config file | Role |
|-------------|------|
| **`.cursor/mcp.json`** | **What Cursor actually loads** (project-scoped; gitignored — copy from example below) |
| [`.mcp.json`](../.mcp.json) | Canonical list for **Claude Code** / docs / team reference (committed) |
| [`.cursor/mcp.json.example`](../.cursor/mcp.json.example) | Template pointer — hw07 servers live in `.cursor/mcp.json` after setup |

**Important:** Editing only `.mcp.json` at repo root does **not** update Cursor. Copy or sync servers into `.cursor/mcp.json`, then **Developer: Reload Window** (or restart Cursor).

Quick hw07 bootstrap:

```powershell
# From repo root — copies hw07 MCP block into .cursor/mcp.json (safe; uses ${env:...} only)
Copy-Item .cursor\mcp.json.example .cursor\mcp.json -ErrorAction SilentlyContinue
# Then add any local-only server overrides OR run setup-dev.ps1
```

**Verify:** Settings → **Tools & MCP** — `kaggle`, `openwebui`, `rapidapi`, `playwright` should appear. Red = missing env var or server failed to start.

## MCP server catalog

Only servers with a real use in this repo are configured. Do not add unused integrations.

| Server | Type | Used for | Required env |
|--------|------|----------|--------------|
| `course-tools` | stdio | Lecture 08 demo (`get_weather`, `get_joke`) | lecture 08 venv via [`scripts/run-mcp-course-tools.py`](../scripts/run-mcp-course-tools.py) |
| `playwright` | stdio | Browser automation, hw07/e2e, UI capture | Node 18+ |
| `kaggle` | HTTP | hw07 dataset access | `KAGGLE_API_TOKEN` |
| `openwebui` | stdio | hw07 KB upload / OWUI automation | `OWUI_URL`, `OWUI_API_KEY` in repo `.env` (launcher maps to `OPENWEBUI_*`) |
| `rapidapi` | stdio | RapidAPI marketplace MCP bridge | `RAPIDAPI_KEY`, `RAPIDAPI_HOST` in repo `.env` |
| `aws-knowledge` | HTTP | AWS docs Q&A (no auth) | — |
| `aws-api` | stdio | AWS API calls via profile | `AWS_PROFILE`, `AWS_REGION` |
| `bedrock-kb` | stdio | Bedrock KB retrieval demos | `AWS_PROFILE`, optional `BEDROCK_KB_ID` |
| `n8n-workflows` | stdio | hw06 / lecture 09 automation | `N8N_API_URL`, `N8N_API_KEY` |
| `lovable` | HTTP | UI prototyping (optional) | `LOVABLE_CLIENT_ID` |

**Hugging Face (Cursor plugin):** Not in `.mcp.json` — enable the **Hugging Face** MCP plugin in Cursor Settings. Tools: `hub_repo_details`, `hf_doc_search`, `hf_whoami`. Requires `HF_TOKEN` in `.env` or user environment. Used for lecture 11 model discovery and hw07 dataset repos.

Launcher for stdio course server (cross-platform):

```bash
python scripts/run-mcp-course-tools.py
```

## Skills (`.cursor/skills/`)

Read the matching `SKILL.md` before using a capability:

| Skill | When |
|-------|------|
| `repo-tooling` | MCP setup, CI, env, which config file to edit |
| `local-models` | Qwen3.6, llama-cpp-python, Ollama/Open WebUI, Intel Arc tuning |
| `hw07-open-webui` | Homework 07 Docker stack, KB, tool server |
| `mcp-integration` | Adding or debugging MCP servers |
| `agent-development` | Building agents, system prompts, tool design |
| `browser-use` | Playwright / browser automation |
| `excalidraw-diagram` | Architecture diagrams for docs |
| `frontend-design` | React/Vite UI work |
| `skill-development` | Authoring new skills |

Do **not** fork skills under `.agents/` — one library only.

## Cursor rules (`.cursor/rules/`)

| Rule | Scope |
|------|--------|
| `secrets-and-mcp-security.mdc` | Always — no hardcoded keys |
| `python-sre-quality.mdc` | Always — tests, logging, failure modes |
| `ai-engineering-rag.mdc` | Agent — RAG grounding, refusal |
| `scope-and-diffs.mdc` | Agent — minimal diffs, no drive-by refactors |

## Claude Code

[`CLAUDE.md`](../CLAUDE.md) sources `@AGENTS.md` and adds Claude-specific subagent hints.

## CI (agents must keep green)

```bash
ruff check .
cd projects/incident-assistant-rag/backend && pytest -q
```

Full matrix: [`.github/workflows/ci.yml`](../.github/workflows/ci.yml).

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| MCP `course-tools` fails | `pip install -r lectures/08_mcp/requirements.txt` in lecture venv |
| AWS MCP auth errors | `aws sso login --profile $AWS_PROFILE` |
| Kaggle 401 | Regenerate token at kaggle.com/settings |
| n8n timeout | Check `N8N_API_URL` ends without trailing path; key scopes |
| Secrets in git status | Never commit `.env` / `.cursor/mcp.json` — see security rule |
| Playwright MCP red / no tools | Install Node 18+; run `npx -y @playwright/mcp@latest --help`; `npx playwright install chromium`; restart Cursor |
