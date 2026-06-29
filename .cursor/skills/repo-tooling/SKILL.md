---
description: Repository MCP, CI, env, and config map for AI Engineer × SRE workflows
---

# Repo tooling

When the user asks about MCP setup, Cursor/Claude config, CI, `.env`, skills, or which file to edit:

1. Read [`docs/AGENT-TOOLING.md`](../../docs/AGENT-TOOLING.md) first.
2. MCP canonical file: [`.mcp.json`](../../.mcp.json) — not `.cursor/mcp.json` unless overriding locally.
3. Bootstrap: `scripts/setup-dev.ps1` (Windows) or `scripts/setup-dev.sh` (Unix).
4. Course-tools launcher: `scripts/run-mcp-course-tools.py` (cross-platform; no hardcoded Windows python path).
5. Keep [`AGENTS.md`](../../AGENTS.md) as single source of truth; update `CLAUDE.md` only for Claude-specific notes.

## CI matrix (offline pytest)

- `projects/incident-assistant-rag/backend`
- `projects/incident-rag-bedrock`
- `lectures/10_langchain_langgraph`
- `homework/hw07/open-webui-tools`

Always run `ruff check .` before claiming a change is ready.

## Do not

- Commit `.env`, `.cursor/mcp.json`, or API keys in MCP JSON.
- Add MCP servers without a documented use in this repo.
- Fork skills into `.agents/`.
