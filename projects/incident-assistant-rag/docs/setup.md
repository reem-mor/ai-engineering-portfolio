# Setup Guide

Canonical setup for **Incident Assistant RAG** (IncidentIQ). For architecture and RAG details, see [architecture.md](architecture.md) and [rag_pipeline.md](rag_pipeline.md).

## Prerequisites

| Requirement | Notes |
|-------------|-------|
| Python **3.12+** | Python 3.14 may fail on pinned packages (e.g. `pydantic-core`) |
| Node.js **18+** | For Vite frontend |
| OpenAI API key | Backend only — set in `backend/.env` |
| Docker (optional) | Docker Compose for full-stack container run |

## 1. Clone and enter the project

```powershell
cd projects\incident-assistant-rag
```

## 2. Backend setup

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
```

Edit `backend/.env` and set `OPENAI_API_KEY` to your key. Never commit `.env`.

Start the API:

```powershell
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Verify:

- Health: http://127.0.0.1:8000/api/health  
- Swagger: http://127.0.0.1:8000/docs  

### Optional: course-wide venv

If you use the repo-root venv at `%USERPROFILE%\amdocs-ai-course\.venv`:

```powershell
cd backend\scripts
.\dev_local.ps1
```

## 3. Frontend setup

In a second terminal:

```powershell
cd frontend
npm install
npm run dev
```

Open **http://localhost:5173** (preferred). `http://127.0.0.1:5173` also works — backend CORS allows both.

Copy `frontend/.env.example` to `frontend/.env` only if the API is not on `http://localhost:8000/api`.

## 4. First run — index the knowledge base

Before RAG Chat works, build the FAISS index:

1. Open the UI → **Knowledge Base**
2. Click **Index Sample Documents**

Or via API:

```powershell
curl -X POST http://localhost:8000/api/documents/index-samples
```

Sample corpus lives in `data/sample_documents/`.

## 5. Docker Compose

From project root:

```powershell
docker compose build
docker compose up
```

Requires `backend/.env` with a valid OpenAI key. `./data` is mounted into the backend container.

| Service | URL |
|---------|-----|
| Frontend | http://localhost:3000 |
| Backend Swagger | http://localhost:8000/docs |

## 6. Evaluation runner

From project root (requires real `OPENAI_API_KEY` for live mode):

```powershell
$env:PYTHONPATH="backend"
python scripts/run_evaluation.py
```

Writes `evaluation/evaluation_results.json` and `evaluation/evaluation_results.md`.

**Note:** `scripts/run_evaluation.py` uses `python-dotenv`. If import fails, install it in your venv: `pip install python-dotenv` (optional; not required for pytest).

If you changed `EMBEDDING_MODEL` or `EMBEDDING_DIMENSIONS`, delete `data/faiss_index/incidentiq.index` and `incidentiq_metadata.json`, then re-index.

## 7. Testing

```powershell
cd backend
python -m pytest tests -v --tb=short
```

From project root: `pytest` (uses root `pytest.ini`).

Frontend build check:

```powershell
cd frontend
npm run build
```

Details: [../TESTING.md](../TESTING.md)

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| `ModuleNotFoundError: No module named 'app'` | Run uvicorn/pytest from `backend/` (directory containing `app/`) |
| Chat returns “no match” for valid questions | Index sample documents first; check FAISS files under `data/faiss_index/` |
| Frontend “Failed to fetch” | Confirm backend `/api/health` responds; hard-refresh browser |
| Embedding dimension mismatch | Re-index after changing `EMBEDDING_DIMENSIONS` in `.env` |
| Docker backend unhealthy | Ensure `backend/.env` exists and OpenAI key is set |

## Security

- Secrets live in `backend/.env` only
- Do not paste API keys into chat, commits, or screenshots
- Use placeholders from `.env.example` when sharing config
