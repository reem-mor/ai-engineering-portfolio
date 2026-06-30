# Incident Assistant RAG — Backend

FastAPI backend for IncidentIQ. **Full setup:** [`../docs/setup.md`](../docs/setup.md)

Work in this directory: `projects/incident-assistant-rag/backend` (contains `app/`, `tests/`, `requirements.txt`).

## Quick start

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
# Set OPENAI_API_KEY in .env

uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

- Health: http://127.0.0.1:8000/api/health  
- Swagger: http://127.0.0.1:8000/docs  

## Helper scripts (optional)

From `backend/scripts/`:

- `dev_local.ps1` — uses repo-root `.venv` at `ai-engineering-portfolio/.venv`
- `check_health.ps1` — curls `/api/health`

## Environment

Copy [`.env.example`](.env.example) → `.env`. OpenAI keys stay here only — never in the frontend.

## Tests

```powershell
python -m pytest tests -v --tb=short
```

See [`../TESTING.md`](../TESTING.md) and [`../docs/setup.md`](../docs/setup.md).

## Docs

- [`../README.md`](../README.md) — project overview  
- [`../docs/architecture.md`](../docs/architecture.md)  
- [`LOCAL_DEV.md`](LOCAL_DEV.md) — extended local notes  
