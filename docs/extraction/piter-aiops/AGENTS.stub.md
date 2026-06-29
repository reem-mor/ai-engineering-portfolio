# AGENTS.md — PITER AiOps

Standalone flagship repo extracted from the course archive. Agent guidance for coding tools.

## What this repository is

Production-minded **agentic incident-response** stack: Bedrock Agent + Action Groups, RAG,
Flask API, React SPA, Docker, pytest.

## Conventions

- **Python 3.12** — `requirements-dev.txt` for dev/test deps
- **Frontend** — `frontend/` source; `npm run build` → `app/static/spa/` (gitignored)
- **Lint/test** — ruff + pytest in CI; run `pytest -q` before PRs
- **Secrets** — env vars only; `.env` gitignored; parameterize AWS resource IDs in docs

## Do not

- Commit SPA build output, `.env`, or live infrastructure identifiers
- Hardcode API keys or Bedrock resource IDs in tracked files
