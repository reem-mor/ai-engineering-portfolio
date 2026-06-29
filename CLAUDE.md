# CLAUDE.md

Claude Code entry point for this repository. **Canonical guidance lives in [`AGENTS.md`](AGENTS.md)** — imported below.

@AGENTS.md

## Claude Code — repo-specific notes

### Before you edit

- Read [`docs/AGENT-TOOLING.md`](docs/AGENT-TOOLING.md) for MCP catalog, skills, and CI matrix.
- Load the relevant [`.cursor/skills/`](.cursor/skills/) skill when the task matches (MCP, browser, diagrams, agents).

### Subagents worth invoking

| Task | Subagent |
|------|----------|
| Pre-PR review | `code-reviewer` |
| Tests / TDD | `test-engineer` |
| FastAPI / Flask APIs | `python-backend` |
| RAG pipeline tuning | `rag-engineer` |
| MCP wiring | `mcp-integrator` |
| Docker / CI / AWS infra | `devops-infra` |
| Incident-style debugging | `sre-incident-responder` |

### Commands (Claude Code)

Use `/review` before PRs, `/test` after logic changes, `/commit` only when the user asks to commit.

### MCP

Project servers are in [`.mcp.json`](.mcp.json). Never paste secrets into MCP JSON — use `${env:VAR}` and gitignored `.env`.

### Scope guard

- Flagship code lives in external repos ([piter-aiops](https://github.com/reem-mor/piter-aiops), [course-assistant-bot](https://github.com/reem-mor/course-assistant-bot)) — edit those clones, not pointer folders here.
- This archive is portfolio-facing — prefer docs and hygiene over rewrites of working project code.
