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

The `tests/` tree targets **80+** collected items. Use `--collect-only` for the exact count.

## Collection errors

| Symptom | Cause |
|---------|------|
| `ModuleNotFoundError: No module named 'app'` | Wrong cwd — use the folder that directly contains **`app/`** (after flatten: `...\backend`). If nesting remains, **`cd`** into **`backend\backend`** *or* run [`flatten_layout.py`](flatten_layout.py). |
| `ERROR collecting ...` | Import error in a test module. |
| IDE shows partial tests | Wrong working directory or filtered run profile. |
