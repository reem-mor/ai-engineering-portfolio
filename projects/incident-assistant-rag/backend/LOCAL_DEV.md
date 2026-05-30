# Run API locally

Extended local dev notes. **Start here:** [`../docs/setup.md`](../docs/setup.md)

## 1. Activate venv and install

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Or use the course venv and `scripts/dev_local.ps1`.

## 2. OpenAI key

Copy [`.env.example`](.env.example) → `.env` in **this folder** (same folder as `app/`):

```env
OPENAI_API_KEY=sk-your-openai-api-key-here
EMBEDDING_MODEL=text-embedding-3-small
EMBEDDING_DIMENSIONS=1536
ANSWER_MODEL=gpt-4o-mini
```

Do **not** commit `.env`. After changing embedding settings, re-index sample documents.

## 3. Start the server

```powershell
cd backend
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Check: http://127.0.0.1:8000/api/health, http://127.0.0.1:8000/docs

## 4. Frontend (Vite)

```powershell
cd frontend
npm run dev
```

Open http://localhost:5173. If the dashboard shows **Failed to fetch**, confirm `/api/health` responds and hard-refresh.

## 5. Pytest

```powershell
cd backend
python -m pytest tests -v --tb=short
```

See [`../TESTING.md`](../TESTING.md).
