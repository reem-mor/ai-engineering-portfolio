# Demo Script

## 1. Start the Application

Run:

```bash
docker compose build
docker compose up
```

Open:

```text
http://localhost:3000
```

## 2. Show Knowledge Base

Explain that the app includes sample incident documents in MD, TXT, CSV, PDF, and DOCX formats. Click `Index Sample Documents`.

## 3. Show RAG Chat

Ask:

```text
What should I check when users cannot log in after deployment?
```

Explain that the app retrieves relevant chunks from FAISS and answers only from the retrieved context.

Show the **Context · Grounded** badge and source filenames/chunks.

Screenshot: `screenshots/06_frontend_rag_chat_grounded.png`

## 3b. Show Irrelevant Question (Hallucination Control)

Ask:

```text
What is the best restaurant in Tokyo?
```

Explain that weak retrieval triggers a **fixed refusal** — no LLM call, `used_context: false`, **Context · No match** in the UI. This is evaluation Test 5 (see `evaluation/evaluation_results.md`).

Screenshot: `screenshots/07_frontend_rag_chat_irrelevant.png`

## 4. Show Incident Analysis

Use:

```text
Description: Many users cannot log in after the latest production deployment.
Affected service: auth-service
Environment: production
```

Show severity, likely causes, checks, missing information, next action, escalation, and sources.

Screenshot: `screenshots/08_frontend_incident_analysis.png`

## 5. Show Swagger

Open:

```text
http://localhost:8000/docs
```

Show the API endpoints.

## 5b. Show Evaluation and Tests (Optional)

- Open `evaluation/evaluation_results.md` — **5/5 PASS** including irrelevant question.
- Screenshot: `screenshots/12_backend_evaluation_5_of_5.png`
- Run `pytest` in `backend/` — **90 passed**. Screenshot: `screenshots/11_backend_tests_90_passed_pytest.png`

## 6. Explain Architecture

Mention:

- React frontend
- FastAPI backend
- OpenAI embeddings and generation
- FAISS vector search
- Supabase metadata and history
- Docker Compose
