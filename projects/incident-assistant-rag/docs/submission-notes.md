# Submission Notes

Homework and portfolio submission checklist for **Incident Assistant RAG** (IncidentIQ).

## Course alignment

Built for the **Amdocs AI-Augmented Software Engineering** course — RAG Application homework (Lesson 5).

| Requirement | Evidence |
|-------------|----------|
| Meaningful operational topic | NOC/DevOps/SRE runbooks, incidents, escalation |
| Knowledge base + FAISS | `data/sample_documents/` + user uploads; FAISS index in `data/faiss_index/` |
| RAG pipeline | Retrieve → filter → grounded prompt → LLM; see [rag_pipeline.md](rag_pipeline.md) |
| Web application | React UI: chat, KB, upload, incident analysis |
| Validation | 90 pytest tests; 5-question eval harness (5/5 PASS) |
| Documentation | README, architecture, setup, screenshots |

## Demo script

Follow [demo_script.md](demo_script.md) for a grader-friendly walkthrough:

1. Index sample documents (Knowledge Base)
2. Ask a grounded runbook question (RAG Chat)
3. Ask an irrelevant question (no-context refusal)
4. Run incident analysis
5. Show Swagger and evaluation results

## Screenshots

All submission PNGs are in [`../screenshots/`](../screenshots/). Regenerate with:

```powershell
node scripts/capture_screenshots.mjs
```

Pytest-only screenshot:

```powershell
node scripts/capture_screenshots.mjs --pytest-only
```

| File | Proves |
|------|--------|
| `01_swagger_all_api_endpoints.png` | API surface |
| `06_frontend_rag_chat_grounded.png` | Grounded RAG with sources |
| `07_frontend_rag_chat_irrelevant.png` | Hallucination control |
| `08_frontend_incident_analysis.png` | Structured incident output |
| `04_frontend_knowledge_base_index_success.png` | FAISS indexing |
| `11_backend_tests_90_passed_pytest.png` | 90 automated tests |
| `12_backend_evaluation_5_of_5.png` | Evaluation harness |

## Evaluation proof

Live run documented in [`../evaluation/evaluation_results.md`](../evaluation/evaluation_results.md): **5/5 PASS**, including irrelevant question (Test 5).

Questions: [`../evaluation/test_questions.json`](../evaluation/test_questions.json)

## Beyond minimum requirements

- Incident reasoning endpoint with severity and escalation
- Trust UI (grounded / no-match badges, source cards)
- Hallucination controls (threshold, no-LLM refusal path)
- Edge-case documentation ([edge_cases.md](edge_cases.md))
- Docker Compose full-stack deployment
- Optional Supabase integration (disabled by default)

## What to submit

- Source code (this repository path)
- [`../README.md`](../README.md) as entry point
- [`architecture.md`](architecture.md), [`reflection.md`](reflection.md)
- Screenshot folder and evaluation results
- No secrets — only `.env.example` placeholders

## Author

Re'em Mor — [github.com/reem-mor](https://github.com/reem-mor)
