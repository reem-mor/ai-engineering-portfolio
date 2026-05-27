# Run API locally



Use your course venv and install deps once.



## 0. Normalize folder layout (if needed)



From **`...\incident-assistant-rag\backend`** (the directory that contains `data/` **and should** contain `app/`):



```powershell

python flatten_layout.py

```



Afterward you work only in **`...\backend`** — not **`backend\backend`**.



Until you flatten, **`app`** only exists under this deeper folder (`backend\backend`): use **that** as cwd for sections 3–4, or fix layout with step 0.



## 1. Activate venv & install packages



PowerShell:



```powershell

Set-Location -LiteralPath '<repo-root>'

.\.venv\Scripts\Activate.ps1

pip install -r projects\incident-assistant-rag\backend\requirements.txt

```



(If nesting is **not** fixed yet, the requirements file path ends with `\backend\backend\requirements.txt` instead.)



## 2. OpenAI key (real key here only)



Put **`.env`** next to **`app/`** (after flatten: `...\incident-assistant-rag\backend\.env`):



Copy [`.env.example`](.env.example) → `.env` in **this folder** (same folder as `app/`). Set:



```env
OPENAI_API_KEY=sk-...your-real-key...
EMBEDDING_MODEL=text-embedding-3-small
EMBEDDING_DIMENSIONS=1536
ANSWER_MODEL=gpt-4o-mini
```

After changing embedding model or dimensions, re-index sample documents before chat or evaluation (see README).



Do **not** commit `.env`. Do **not** paste secrets into Cursor chat.



## 3. Start the server



Cwd must be the directory that contains the **`app`** package:



```powershell

Set-Location -LiteralPath '<repo>\projects\incident-assistant-rag\backend'

python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

```



Check: [http://127.0.0.1:8000/api/health](http://127.0.0.1:8000/api/health), [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)



## 3b. Frontend (Vite)



From **`...\incident-assistant-rag\frontend`**:



```powershell

npm run dev

```



Open the UI at **[http://localhost:5173](http://localhost:5173)** (recommended). **`http://127.0.0.1:5173`** also works—the backend CORS list includes both hostnames.



If the dashboard shows **Failed to fetch**, you usually opened `127.0.0.1` before CORS was updated, or the API is not running. Confirm **`/api/health`** responds, then hard-refresh the browser.



## 4. Pytest



```powershell

python -m pytest tests -v --tb=short

```



`tests/conftest.py` loads `./.env` first, then uses a harmless placeholder **only if** keys are unset.


