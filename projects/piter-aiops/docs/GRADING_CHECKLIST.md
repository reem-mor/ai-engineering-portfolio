# Grading checklist — course guideline alignment

Maps the course handout **bedrock_kb_flask_project_guideline.docx** (Bedrock KB + Flask + Docker + EC2) to this repository — **IncidentIQ mid-project with Bedrock Agent**.

## Topic and documents

| Requirement | Evidence |
|-------------|----------|
| Personal topic | **Incident Operations / NOC** — runbooks, escalation, on-call handoff |
| 5–15 meaningful documents | **17 files** in [`data/sample_documents/`](../data/sample_documents/) — see [`data/sample_documents/README.md`](../data/sample_documents/README.md) |
| Documents synced to KB | S3 prefix `projects/incidentIQ-midproject/data/sample_documents/` (or shared KB prefix) — screenshot `screenshots/02_bedrock_kb_data_source_synced.png` |

## Bedrock Knowledge Base + Agent

| Requirement | Evidence |
|-------------|----------|
| KB exists | `screenshots/01_bedrock_kb_overview.png`; `BEDROCK_KB_ID` in `.env.example` |
| Data source attached + synced | `screenshots/02_*`; [`docs/bedrock_kb_setup.md`](bedrock_kb_setup.md) |
| Bedrock Agent provisioned | [`docs/bedrock_agent_setup.md`](bedrock_agent_setup.md); `scripts/setup_bedrock_agent.py`; optional `screenshots/20_bedrock_agent_overview.png` |
| Lambda action group (ops tools) | [`docs/bedrock_action_group_setup.md`](bedrock_action_group_setup.md); `scripts/setup_action_group.py`; optional `screenshots/21_agent_action_group.png` |
| boto3 query from app | [`app/bedrock_agent_client.py`](../app/bedrock_agent_client.py) — `invoke_agent`; fallback [`app/bedrock_client.py`](../app/bedrock_client.py) |
| Live Q&A proof | `screenshots/08_*`, `evaluation/qa_showcase.md`, `scripts/agent_smoke_test.py` |

## Flask application

| Requirement | Evidence |
|-------------|----------|
| Home page, question, submit, answer | React SPA at `/` or legacy Jinja when `FORCE_LEGACY_UI=1` |
| Topic-themed design | NOC/incident palette — `screenshots/07_*`, `14_*` |
| Entry point `app.py` | [`app.py`](../app.py); production [`wsgi.py`](../wsgi.py) |

## Docker and EC2

| Requirement | Evidence |
|-------------|----------|
| Dockerfile + compose | [`Dockerfile`](../Dockerfile), [`docker-compose.yml`](../docker-compose.yml) |
| Public access | `screenshots/04_*`, `07_*` |
| Container running | `screenshots/06_docker_ps_on_ec2.png` |

## Automated verification

Run from **project root** (`projects/incidentIQ-midproject`):

```powershell
.\scripts\verify.ps1
# Offline only: .\scripts\verify.ps1 -SkipLiveAws -SkipE2e
```

| Command | Expectation |
|---------|-------------|
| `pytest -q` | **121+ passed** (offline, no live AWS) |
| `npm run build` | `app/static/spa/` updated |
| `scripts/agent_smoke_test.py` | **6/7+** (needs AWS + agent IDs in `.env`) |
| `scripts/agent_smoke_test.py --ops` | ops action group prompts (GIB status/alerts) |
| `scripts/kb_smoke_test.py` | fallback when `RAG_BACKEND=retrieve_and_generate` |

## Stretch goals

- Document upload + KB sync — `15_*` screenshots
- Follow-up via `session_id` on `/ask` (agent session)
- Workflow triage — `13_mvp_workflow.png`
- MCP tool wrapper (future) — expose `ask()` to Cursor agents
