# IncidentIQ - Incident Assistant RAG Application

IncidentIQ is a full-stack Retrieval-Augmented Generation application for technical incident analysis. It helps NOC, DevOps, backend, and support teams ask operational questions, retrieve relevant runbooks, and receive grounded incident recommendations based on an indexed knowledge base.

## Main Features

- Upload incident documents.
- Ingest sample documents in MD, TXT, CSV, PDF, and DOCX formats.
- Clean and preprocess text.
- Split documents into overlapping chunks.
- Generate embeddings with OpenAI.
- Store vectors in FAISS.
- Ask grounded RAG questions.
- Analyze incidents with structured reasoning output.
- Show retrieved sources, chunk scores, confidence, and no-context behavior.
- Store metadata and history in Supabase Postgres, optional.
- Run locally with Docker Compose.

## Tech Stack

### Backend

- Python
- FastAPI
- Pydantic
- OpenAI API
- FAISS
- Supabase Postgres, optional
- Pytest

### Frontend

- React
- TypeScript
- Vite
- Nginx

### Infrastructure

- Docker
- Docker Compose

## Architecture

```text
User
  |
  v
React Frontend
  |
  v
FastAPI Backend
  |
  +--> Document Loader
  +--> Text Cleaner
  +--> Text Chunker
  +--> OpenAI Embeddings
  +--> FAISS Vector Store
  +--> Retriever
  +--> Prompt Builder
  +--> OpenAI Answer Generator
  +--> Supabase Metadata and History
```

## RAG Pipeline Flow

```text
Document
  -> Extract text
  -> Clean text
  -> Split into chunks
  -> Generate embeddings
  -> Store vectors in FAISS
  -> User asks question
  -> Embed question
  -> Retrieve relevant chunks
  -> Build grounded prompt
  -> Generate answer
  -> Return answer, sources, confidence, and retrieved chunks
```

## Incident Reasoning Flow

```text
Incident description
  -> Estimate severity
  -> Retrieve relevant runbooks from FAISS
  -> Build structured incident prompt
  -> Generate JSON analysis
  -> Validate or fallback
  -> Return severity, causes, checks, missing info, next action, escalation, sources, confidence
```

## Supported File Types

- `.md`
- `.txt`
- `.csv`
- `.pdf`
- `.docx`

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/health` | Backend health check |
| POST | `/api/upload` | Upload document |
| GET | `/api/documents/samples` | List sample documents |
| POST | `/api/documents/index-samples` | Build FAISS index from sample documents |
| GET | `/api/documents/uploaded` | List uploaded documents |
| POST | `/api/documents/index-uploaded` | Build FAISS index from uploaded documents |
| POST | `/api/chat` | Ask a RAG question |
| POST | `/api/incident/analyze` | Analyze an incident |

## Environment Variables

Create `backend/.env`:

```env
OPENAI_API_KEY=your_openai_api_key_here
APP_NAME=IncidentIQ RAG API
APP_VERSION=0.1.0
ENVIRONMENT=local
EMBEDDING_MODEL=text-embedding-3-small
EMBEDDING_DIMENSIONS=1536
SUPABASE_URL=your_supabase_project_url
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key
DATABASE_ENABLED=false
```

Use `DATABASE_ENABLED=true` only after running [`backend/docs/supabase_schema.sql`](backend/docs/supabase_schema.sql) in the Supabase SQL Editor.

## Run Without Docker

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

On Windows PowerShell:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Backend runs at:

```text
http://localhost:8000
```

Swagger:

```text
http://localhost:8000/docs
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at:

```text
http://localhost:5173
```

## Run With Docker

From the project root:

```bash
docker compose build
docker compose up
```

Open:

```text
Frontend: http://localhost:3000
Backend docs: http://localhost:8000/docs
Health check: http://localhost:8000/api/health
```

## Recommended Demo Flow

1. Open `http://localhost:3000`.
2. Go to Knowledge Base.
3. Click `Index Sample Documents`.
4. Go to RAG Chat.
5. Ask: `What should I check when users cannot log in after deployment?`
6. Confirm answer, confidence, used context, and retrieved sources.
7. Go to Incident Analysis.
8. Enter: `Many users cannot log in after the latest production deployment.`
9. Use `affected_service: auth-service` and `environment: production`.
10. Confirm severity, likely causes, recommended checks, missing information, next action, escalation, and sources.

## Evaluation

Evaluation questions are stored in:

```text
evaluation/test_questions.json
```

Run evaluation after indexing sample documents:

Windows PowerShell:

```powershell
$env:PYTHONPATH="backend"
python scripts/run_evaluation.py
```

macOS/Linux:

```bash
PYTHONPATH=backend python scripts/run_evaluation.py
```

Generated reports:

```text
evaluation/evaluation_results.json
evaluation/evaluation_results.md
```

## Testing

Run backend tests:

```bash
cd backend
pytest
```

Expect **81 passed** (with deps installed from `requirements.txt`).

Build frontend (required before relying on Step 10 / Supabase changes):

```bash
cd frontend
npm install
npm run build
```

Build runs **`tsc --noEmit`** then **`vite build`**; output is under **`frontend/dist/`**.

## Edge Cases Covered

- Empty upload file.
- Unsupported file type.
- Missing file extension.
- Large file validation.
- Empty CSV.
- Encrypted or unreadable PDF.
- PDF with no extractable text.
- Empty DOCX.
- Empty question.
- Invalid `top_k`.
- Missing FAISS index.
- Low-confidence retrieval.
- Irrelevant questions.
- Bad JSON returned by the LLM during incident reasoning.
- Database unavailable.
- Supabase disabled mode.
- Query embedding dimension mismatch.
- FAISS metadata mismatch.

## Security Notes

- API keys are stored only in `.env`.
- `.env` files are ignored by Git.
- Supabase service role key is used only by the backend.
- Frontend never receives secret keys.
- Uploaded files are renamed using UUIDs.
- Generated FAISS and embedding files are not committed.

## Additional Documentation

- `docs/architecture.md`
- `docs/rag_pipeline.md`
- `docs/incident_reasoning.md`
- `docs/testing_plan.md`
- `docs/reflection.md`
- `docs/demo_script.md`
- `docs/code_review_checklist.md`
- `docs/edge_cases.md`

## Future Production Improvements

- Replace local FAISS only if you deliberately move beyond this coursework deployment model (assignment requires **FAISS**).
- Move ingestion to Inngest or Celery for background processing.
- Add retries and rate limiting for OpenAI calls.
- Add structured logs and observability.
- Add authentication and user-specific chat history.
- Add incremental indexing instead of full FAISS rebuilds.
