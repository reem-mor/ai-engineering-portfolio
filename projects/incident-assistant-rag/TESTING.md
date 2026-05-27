# Testing & dev server (Incident Assistant RAG)

Preferred layout: **`projects/incident-assistant-rag/backend/`** contains `app/`, `tests/`, `data/`, and `requirements.txt` in the **same** directory.

If your tree still has an extra **`backend/backend/app`** nesting, fix it once (from the folder that contains `data/`):

```powershell
Set-Location -LiteralPath '<repo>\projects\incident-assistant-rag\backend'
python flatten_layout.py
```

## Run the API on localhost

Start Uvicorn from the directory that contains the **`app/`** package (after flatten, that is `...\incident-assistant-rag\backend`):

```powershell
Set-Location -LiteralPath '<repo>\projects\incident-assistant-rag\backend'
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

## Python version (Windows)

Use **Python 3.12** for local backend work. System Python **3.14** may fail on pinned packages such as `pydantic-core`.

```powershell
Set-Location -LiteralPath '<repo>\projects\incident-assistant-rag\backend'
py -3.12 -m venv .venv312
.\.venv312\Scripts\python.exe -m pip install -r requirements.txt
.\.venv312\Scripts\python.exe -m pytest tests -v --tb=short
```

## Pytest

[`pytest.ini`](pytest.ini) uses `testpaths = tests` and `pythonpath = .` relative to that same directory.

```powershell
Set-Location -LiteralPath '<repo>\projects\incident-assistant-rag\backend'
python -m pip install -r requirements.txt
python -m pytest tests -v --tb=short
```

[`tests/conftest.py`](tests/conftest.py) loads `./.env` first, then sets a harmless placeholder OpenAI key if unset — real keys belong in `.env` only (via [`.env.example`](.env.example)).

Collect-only:

```powershell
python -m pytest tests --collect-only -q
```

## How many tests?

The `tests/` tree currently has **90** collected items (including PDF/DOCX loader, chat/index integration, and document index route tests). Use `--collect-only` for the exact count.

Additional modules:

- `tests/test_chat_integration.py` — happy-path chat and missing FAISS index
- `tests/test_document_index_routes.py` — `index-samples` / `index-uploaded`
- `tests/test_document_loader.py` — sample PDF, DOCX, and CSV fixtures

## Evaluation runner

From project root (loads `backend/.env` automatically):

```powershell
Set-Location -LiteralPath '<repo>\projects\incident-assistant-rag'
$env:PYTHONPATH = '<repo>\projects\incident-assistant-rag\backend'
python scripts/run_evaluation.py
```

Or from `backend/`:

```powershell
Set-Location -LiteralPath '<repo>\projects\incident-assistant-rag\backend'
$env:PYTHONPATH = '.'
python ..\scripts\run_evaluation.py
```

Writes `evaluation/evaluation_results.json` and `evaluation/evaluation_results.md`. Without a real `OPENAI_API_KEY`, the script uses offline fake embeddings and generators and rebuilds the sample index automatically.

If you run offline evaluation first, delete `data/faiss_index/incidentiq.index` and `incidentiq_metadata.json` before live evaluation, or let the script rebuild when embedding dimensions no longer match `EMBEDDING_DIMENSIONS`.

## After changing embedding settings

If you change `EMBEDDING_MODEL` or `EMBEDDING_DIMENSIONS` in `backend/.env`, remove `data/faiss_index/incidentiq.index` and `incidentiq_metadata.json`, then index again before chat or evaluation:

```powershell
# From UI: Knowledge Base → Index Sample Documents
# Or API:
curl -X POST http://localhost:8000/api/documents/index-samples
```

## Collection errors

| Symptom | Cause |
|---------|------|
| `ModuleNotFoundError: No module named 'app'` | Wrong cwd — use the folder that directly contains **`app/`** (after flatten: `...\backend`). If nesting remains, **`cd`** into **`backend\backend`** *or* run [`flatten_layout.py`](flatten_layout.py). |
| `ERROR collecting ...` | Import error in a test module. |
| IDE shows partial tests | Wrong working directory or filtered run profile. |
