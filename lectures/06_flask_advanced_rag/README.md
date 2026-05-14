# Lecture 06 — Flask Advanced & RAG Web App

**Slides:** [`resources/lecture05_flask_advanced.pdf`](../../resources/lecture05_flask_advanced.pdf)

---

## Topics Covered

- Flask REST API design: `jsonify()`, HTTP status codes, error responses
- SQLite with the `sqlite3` standard library (no ORM)
- Thread-local database connections (`threading.local`)
- Background initialisation with `threading.Thread`
- CRUD operations over REST: sessions and messages
- The `RAGEngine` class: encapsulated state, `initialise()`, `retrieve()`, `answer()`
- FAISS index inside a long-lived in-memory object
- Polling pattern for async startup: `GET /api/status`
- Frontend: vanilla JS fetch, session management, typing indicator, toast notifications
- Secret management: environment variables via `.env` / `os.environ`

---

## Key Concepts You Must Know

### REST API Design

| Method | Path | Action |
|--------|------|--------|
| GET | `/api/sessions` | List all sessions |
| POST | `/api/sessions` | Create new session |
| GET | `/api/sessions/<id>` | Get session + messages |
| PATCH | `/api/sessions/<id>` | Rename session |
| DELETE | `/api/sessions/<id>` | Delete session |
| POST | `/api/sessions/<id>/messages` | Send a chat message |
| GET | `/api/status` | RAG engine readiness |

Rules followed here:
- Use nouns for resource paths, not verbs.
- POST returns `201 Created`; successful DELETE returns `{"ok": True}`.
- Missing resource returns `404`; bad input returns `400`; engine not ready returns `503`.

### SQLite without ORM

```python
import sqlite3
import threading

_local = threading.local()   # per-thread connection storage

def get_connection():
    conn = getattr(_local, "conn", None)
    if conn is None:
        conn = sqlite3.connect("chat.db", check_same_thread=False)
        conn.row_factory = sqlite3.Row   # rows accessible by column name
        conn.execute("PRAGMA foreign_keys = ON;")
        _local.conn = conn
    return conn
```

Why per-thread? Flask may handle concurrent requests in different threads; SQLite connections are not safe to share across threads without the WAL journal mode.

### Background Initialisation Pattern

RAG startup (downloading NLTK, computing embeddings) takes 10–60 s. Blocking the server would timeout the first request.

```python
def _start_background_init():
    database.init_db()
    thread = threading.Thread(target=_initialise_engine_background, daemon=True)
    thread.start()

_start_background_init()   # called at module import time
```

The frontend polls `GET /api/status` every 1.5 s until `ready: true`.

### RAGEngine Architecture

```python
class RAGEngine:
    chunks: list[str]         # sentence-level text corpus
    sources: list[str]        # filename for each chunk
    index: faiss.IndexFlatIP  # in-memory vector index
    ready: bool
    status: str               # human-readable phase string
    progress: dict            # {"current": N, "total": M}

    def initialise(self) -> None: ...    # load → embed → index
    def retrieve(self, query, k) -> list[dict]: ...
    def ask_gemini(self, context, question, history) -> str: ...
    def answer(self, question, history, k) -> dict: ...
```

The engine is created once at module level and initialised in a background thread. All Flask routes interact with the same instance.

### Environment Variables

Never commit API keys. Provide a `.env.example` and load from environment:

```python
import os
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
HF_TOKEN       = os.environ.get("HF_TOKEN", "")
```

For local development, create a `.env` file (gitignored) and load it:
```bash
pip install python-dotenv
```
```python
from dotenv import load_dotenv
load_dotenv()
```

### Conversation History in the Prompt

The LLM has no memory between API calls. To simulate multi-turn conversation, include previous turns in every prompt:

```
Conversation so far:
User: What are the top risks?
Assistant: The top risks are R-01, R-02, R-03...

Context retrieved from documents:
<FAISS top-k chunks>

User's latest question:
Who is responsible for R-02?
```

---

## Running the App

```bash
cd lectures/06_flask_advanced_rag

# 1. Set API keys
cp .env.example .env
# Edit .env with real keys

# 2. Add corpus
mkdir -p data
cp ../04_nlp_rag/data/risk_analysis_report.txt data/

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run
python app.py
# Open http://127.0.0.1:5000/
```

---

## Exercises

### Exercise 1 — Source Attribution
The `retrieve()` method already returns `source` (filename) and `score` per chunk.
Add source attribution to the rendered message in the frontend: show which file each answer was derived from.

### Exercise 2 — Add a GET /api/sessions/<id>/messages Endpoint
Currently sessions return messages embedded in `GET /api/sessions/<id>`.
Add a dedicated `GET /api/sessions/<id>/messages` route that returns only the message list.
This is better REST design and allows paginating messages independently.

### Exercise 3 — Rate Limiting
Add a simple in-memory counter that limits each session to 20 messages.
Return `429 Too Many Requests` when the limit is exceeded.

### Exercise 4 — Add Document Upload
Add a `POST /api/documents` endpoint that accepts a `.txt` file upload (`request.files`),
saves it to `data/`, and triggers a re-initialisation of the RAG engine.

---

## Common Pitfalls

| Mistake | Fix |
|---------|-----|
| `sqlite3.ProgrammingError: Cannot operate on a closed database` | Use per-thread connections, not a global one |
| App freezes on startup | Move heavy init to a background thread; poll `/api/status` |
| FAISS index is `None` when first request arrives | Check `engine.ready` before processing; return `503` if not ready |
| `os.environ.get("KEY")` returns `None` | Check key is exported in your shell or `.env` loaded |
| CSS/JS not updating in browser | Hard-refresh (`Ctrl+Shift+R`) or disable browser cache in DevTools |
