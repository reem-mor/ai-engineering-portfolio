# Submission Screenshots

Captures for the RAG Application homework and demo walkthrough. Regenerate UI shots with:

```powershell
cd frontend
npm install -D playwright
npx playwright install chromium
cd ..
node scripts/capture_screenshots.mjs
```

**Prerequisites:** Backend on `http://127.0.0.1:8000`, frontend on `http://localhost:5173`, valid `OPENAI_API_KEY` in `backend/.env`, sample documents indexed (script calls `POST /api/documents/index-samples`).

| File | What it proves |
|------|----------------|
| `01_swagger_all_api_endpoints.png` | Full REST API surface in Swagger UI |
| `02_swagger_chat_endpoint.png` | `POST /api/chat` contract for RAG |
| `03_frontend_knowledge_base_before_index.png` | KB UI before indexing |
| `04_frontend_knowledge_base_index_success.png` | Successful FAISS build from sample corpus |
| `05_frontend_upload_document.png` | Document upload flow |
| `06_frontend_rag_chat_grounded.png` | **Homework §4** — grounded answer with sources and **Context · Grounded** |
| `07_frontend_rag_chat_irrelevant.png` | **Homework §3/5** — irrelevant question → **Context · No match**, no hallucination |
| `08_frontend_incident_analysis.png` | **Homework §4** — structured incident report (severity, checks, sources) |
| `09_backend_terminal_uvicorn_running.png` | Backend process running locally |
| `10_frontend_terminal_vite_running.png` | Frontend dev server running |
| `11_backend_tests_90_passed_pytest.png` | **90** automated pytest tests passing |
| `12_backend_evaluation_5_of_5.png` | Five evaluation questions (including irrelevant Q5) all **PASS** |
