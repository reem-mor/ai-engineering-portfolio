# Incident Assistant RAG — backend

Work here: **`.../projects/incident-assistant-rag/backend`** (same folder as `app/`, `data/`, `requirements.txt`).

## Quick start (Windows + course venv)

Use **`%USERPROFILE%\amdocs-ai-course\.venv`** so activation paths stay valid even if your username contains an apostrophe.

**Terminal 1 — install deps & API:**

```powershell
Set-Location -LiteralPath '<repo>\projects\incident-assistant-rag\backend\scripts'
.\dev_local.ps1
```

**Terminal 2 — confirm localhost:**

```powershell
Set-Location -LiteralPath '<repo>\projects\incident-assistant-rag\backend\scripts'
.\check_health.ps1
```

Alternate **cmd**:

```bat
<repo>\projects\incident-assistant-rag\backend\scripts\dev_local.cmd
```

Expected health URL: **`http://127.0.0.1:8000/api/health`** (OpenAPI at **`http://127.0.0.1:8000/docs`**).

Secrets: **`backend\.env`** (copy from [`.env.example`](.env.example)); never commit it.

Manual equivalent:

```powershell
Set-Location -LiteralPath '<repo>\projects\incident-assistant-rag\backend'
& (Join-Path $env:USERPROFILE 'amdocs-ai-course\.venv\Scripts\Activate.ps1')
pip install -r requirements.txt
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

Docs: [`TESTING.md`](TESTING.md), [`LOCAL_DEV.md`](LOCAL_DEV.md).

If something still nests `backend/backend/`, run **`python flatten_layout.py`** once from **`backend`** (next to **`data/`**).
