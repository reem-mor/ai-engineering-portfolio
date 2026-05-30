# Testing & Dev Server

**Canonical setup:** [`docs/setup.md`](docs/setup.md)

Preferred layout: `projects/incident-assistant-rag/backend/` contains `app/`, `tests/`, and `requirements.txt` in the **same** directory.

## Run the API on localhost

```powershell
cd backend
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

## Python version (Windows)

Use **Python 3.12** for local backend work. System Python **3.14** may fail on pinned packages such as `pydantic-core`.

```powershell
cd backend
py -3.12 -m venv .venv312
.\.venv312\Scripts\python.exe -m pip install -r requirements.txt
.\.venv312\Scripts\python.exe -m pytest tests -v --tb=short
```

## Pytest

From `backend/`:

```powershell
python -m pip install -r requirements.txt
python -m pytest tests -v --tb=short
```

From project root (root `pytest.ini` sets `testpaths = backend/tests`):

```powershell
pytest
```

[`backend/tests/conftest.py`](backend/tests/conftest.py) loads `./.env` first, then sets a harmless placeholder OpenAI key if unset.

Collect-only:

```powershell
cd backend
python -m pytest tests --collect-only -q
```

## How many tests?

The `tests/` tree currently has **90** collected items. Use `--collect-only` for the exact count.

Key modules:

- `tests/test_chat_integration.py` — happy-path chat and missing FAISS index
- `tests/test_document_index_routes.py` — `index-samples` / `index-uploaded`
- `tests/test_document_loader.py` — sample PDF, DOCX, and CSV fixtures

Submission screenshot: `node scripts/capture_screenshots.mjs --pytest-only` from project root → `screenshots/11_backend_tests_90_passed_pytest.png`.

## Evaluation runner

From project root:

```powershell
$env:PYTHONPATH="backend"
python scripts/run_evaluation.py
```

Writes `evaluation/evaluation_results.json` and `evaluation/evaluation_results.md`. Optional dependency: `pip install python-dotenv` if the eval script import fails.

If you change `EMBEDDING_MODEL` or `EMBEDDING_DIMENSIONS` in `backend/.env`, remove `data/faiss_index/incidentiq.index` and `incidentiq_metadata.json`, then re-index.

## Collection errors

| Symptom | Cause |
|---------|-------|
| `ModuleNotFoundError: No module named 'app'` | Wrong cwd — run from `backend/` (directory containing `app/`) |
| `ERROR collecting ...` | Import error in a test module |
| IDE shows partial tests | Wrong working directory or filtered run profile |
