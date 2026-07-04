# HW07 Submission Summary

## Project

Netflix KB + Local Tool Server Homework

This project demonstrates:

- Open WebUI Knowledge Base built from a Kaggle Netflix CSV dataset.
- Local Flask tool server on `http://localhost:5005`.
- Open WebUI Workspace Tool that calls the local server for live country data via RapidAPI.

## Local Model Setup

- Open WebUI: `http://localhost:8080`
- Open WebUI version: `v0.10.2`
- Ollama runtime: Windows host, reached from Open WebUI Docker through `http://host.docker.internal:11434`
- Ollama models installed:
  - `llama3.2:3b` for chat
  - `nomic-embed-text` for Knowledge Base embeddings
  - `mistral:latest` also available

## Knowledge Base

- Open WebUI document title: `Netflix Shows KB`
- Collection name: `netflix_shows_kb`
- Indexed evidence: `9619` embeddings in Chroma
- Source dataset in repo: `data/netflix_titles.csv`

Note: the full Kaggle CSV is included in the repo. For local Open WebUI indexing performance, the live KB was indexed from an 800-row Kaggle-derived subset with the same schema and demo country coverage.

## Tool

- Tool name: `Netflix Country Info`
- Tool ID: `netflix_country_info`
- Source file: `openwebui_function_tool.py`
- Local server: `tools_server.py`
- Health endpoint: `GET /health`
- Country endpoint: `GET /country/<country_name>`

## System Prompt

Saved in Open WebUI as:

- Command: `/netflix_hw07_system`
- Title: `Netflix HW07 System Prompt`

Source file:

- `system_prompt.txt`

## Verification

Final automated checks:

```text
pytest: 15 passed, 1 warning
ruff: all checks passed
tools-server: healthy
Open WebUI: healthy
Ollama: running on Windows host
Open WebUI chat smoke test: `llama3.2:3b` answered successfully
```

## Important Edge Cases Verified

- Missing or placeholder `RAPIDAPI_KEY` returns structured JSON error.
- RapidAPI timeout returns `503`.
- Upstream 401/429/500 responses return structured JSON errors.
- Unknown country, e.g. `Atlantis`, returns `404`.
- Accented country input, e.g. `Côte d'Ivoire`, matches API spelling `Cote D'Ivoire (Ivory Coast)`.
- Open WebUI container can reach the tool server through `host.docker.internal:5005`.
- Open WebUI container can reach host Ollama through `host.docker.internal:11434`.

## Submission Files

- `README.md`
- `requirements.txt`
- `.env.example`
- `tools_server.py`
- `test_tools_server.py`
- `system_prompt.txt`
- `openwebui_function_tool.py`
- `screenshots_checklist.md`
- `data/netflix_titles.csv`
- `submission/QA_INPUT_OUTPUT.md`
- `submission/QA_AFTER_UPGRADE.md`
- `submission/evidence.json`
- `submission/evidence-after-upgrade.json`
- `submission/evidence-after-upgrade-db.json`
- `submission/final-evidence-host-ollama.json`
- `submission/edge-case-results-after-upgrade.json`
- `submission/EMAIL_TO_ALEX.md`

