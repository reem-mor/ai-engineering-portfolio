# PITER AiOps — Final Audit Report

Read-only audit · 2026-06-06 · Branch `piter-aiops` · Commit `e473e952200b59849ded98594c1994263164e63e`

## 1. Overall readiness score: **82 / 100**

| Dimension | Score | Notes |
|-----------|------:|-------|
| Flask app + Docker | 95 | Builds; 190 tests pass; health at `/health` |
| RAG (direct KB) | 90 | 7/7 smoke; 29/29 live demo |
| Bedrock Agent (`invoke_agent`) | 65 | Implemented + tested; live flaky 5–6/7 |
| Lambda / action groups | 88 | 3 enrichment + 1 ops; deployed per eval |
| Memory / follow-up | 85 | App session store + follow-up routing |
| Documentation | 70 | Strong guides; backend naming conflicts |
| Security hygiene | 85 | `.env` ignored; minor artifact leaks |
| Repo cleanliness | 75 | Few delete candidates; dual corpus complexity |

---

## 2. Teacher-requirement compliance

| Requirement | Status | Evidence |
|-------------|--------|----------|
| Working Flask web app | **Real** | `/console`, `/api/triage`, Docker |
| RAG over documents | **Real** | Bedrock KB + local TF-IDF fallback |
| MCP/tools concept | **Partial / honest** | Action groups + app tool router; not native MCP server |
| Docker | **Real** | `Dockerfile`, `docker-compose.yml` |
| Python data processing | **Real** | pandas/CSV/JSON in enrichment + datasets |
| Clean GitHub repo | **Mostly** | Minor artifacts (`lambda-out.json`) |
| README + run instructions | **Real** | `README.md`, checklists |
| Working live demo | **Real** | `verify_live_demo.py` 29/29 on direct RAG |
| Six-slide presentation | **Present** | `docs/presentation_outline.md` |
| Demonstrable RAG + tool use | **Real** | Console triage + 4 tool sections |
| Bedrock KB → Agent | **Real (AWS)** | Agent + KB IDs configured; association per setup docs |
| `invoke_agent` via boto3 | **Real (code)** | `app/bedrock_agent_client.py` |
| Memory / conversation history | **Real (app layer)** | `session_memory.py`, follow-up API |
| 3–4 Lambda functions | **Real** | `iiq-correlate`, `iiq-context`, `iiq-similar`, optional ops |
| Explain system prompt | **Ready** | `SYSTEM_PROMPT_REVIEW.md` |

---

## 3. Bedrock Agent status

- **Code:** Complete — streaming, traces, citations, action-group merge, retries.
- **Config:** Agent ID + alias present in environment (values not reproduced here).
- **Live:** Ops smoke 3/3; full agent smoke 5–6/7; ungrounded answers possible without exception → no auto-fallback.
- **Recommendation:** Demo agent in a **controlled terminal segment** (`agent_smoke_test.py --ops` minimum) even if console stays on direct RAG.

## 4. Direct Knowledge Base status

- **Active live path:** `RAG_BACKEND=retrieve_and_generate`
- **Smoke:** 7/7 reliable after temperature/top_p fix
- **Keep:** Required for demo-safe grounded citations

## 5. boto3 status

- **Clients:** `bedrock-agent-runtime` for both backends; correct API separation verified in `BEDROCK_BACKEND_AUDIT.md`

## 6. Knowledge Base quality

- **Corpus:** 24 sample docs + 10 RB runbooks in Docker image path
- **Categories:** Runbooks, escalation, ownership, incidents, architecture largely covered
- **Gaps:** Duplicate naming across corpora; some eval questions need multi-doc synthesis — see `KNOWLEDGE_BASE_AUDIT.md`

## 7. Lambda / action-group status

- **3 enrichment Lambdas** + **1 ops mock** — see `LAMBDA_ACTION_GROUP_AUDIT.md`
- App-layer tools always run on triage; agent path can additionally invoke action groups

## 8. MCP status

- **Not** a standalone MCP server in-repo
- **Yes** Bedrock action groups + tool-router abstraction — see `MCP_TOOLS_AUDIT.md`

## 9. Memory / history status

- In-process session store; single gunicorn worker by design
- Follow-ups use stored tool outputs for classified questions
- See Mermaid diagram in `MEMORY_AND_HISTORY_AUDIT.md`

## 10. Docker status

- `docker compose config` valid
- Image builds as `piter-aiops:dev`
- `.dockerignore` excludes tests/docs; includes `knowledge_base/`

## 11. Test status

- **190 passed** (`pytest -q`, 2026-06-06)
- `compileall app` OK
- ruff/mypy not installed in venv
- Live AWS smokes not re-run this session (cost/rule)

## 12. Security status

- `.env` gitignored; no keys in tracked source
- Delete candidates: `lambda-out.json`, local EC2 txt files
- See `SECURITY_AUDIT.md`

## 13. Live-demo reliability

- **High** on current config (`retrieve_and_generate` + app tools)
- Offline path: `USE_BEDROCK=false`

## 14. Unused-file findings

- **4 safe deletes**, **4 archive moves** — `UNUSED_FILES_REPORT.md`, `CLEANUP_PLAN.md`
- **No source modules** flagged for deletion

## 15. Documentation contradictions

| Topic | Conflict |
|-------|----------|
| Primary backend | README/architecture = agent; live `.env` = direct RAG |
| Health URL | Checklist `/healthz` vs app `/health` |
| MCP wording | Sometimes “MCP” for tool router — clarify for graders |
| S3 policy prefix | `incidentIQ-midproject` vs `piter-aiops` paths |

## 16. Files proposed for deletion (pending approval)

1. `lambda-out.json`
2. `evaluation/pytest_output.txt`
3. `.ec2_instance_id.txt` (local)
4. `.sg_id.txt` (local)
5. `docs/review/_gen_inventory.py` (after inventory sign-off)

## 17. Smallest safe top-grade change set

See `CLEANUP_PLAN.md` — doc fixes + mode badge + optional agent video segment + artifact cleanup. **No deletions until you approve.**

## 18. Commands before recording teacher video

```powershell
cd C:\dev\amdocs-ai-course\projects\piter-aiops

# Checkpoint (exclude .env)
git switch -c cleanup/piter-aiops-audit
git add docs/review/
git commit -m "docs: add read-only repository audit reports"

# Verify local quality gate
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m compileall app

# Docker smoke (stop when done)
docker compose build
docker compose up -d
curl http://localhost:8080/health
.\.venv\Scripts\python.exe scripts\verify_live_demo.py

# Optional AWS agent proof (uses Bedrock — your approval)
.\.venv\Scripts\python.exe scripts\agent_smoke_test.py --ops
.\.venv\Scripts\python.exe scripts\agent_smoke_test.py

# Direct KB proof
.\.venv\Scripts\python.exe scripts\kb_smoke_test.py

docker compose down
```

For agent-primary recording only if smoke passes:

```powershell
# After backup .env — set RAG_BACKEND=agent, restart app, re-run verify_live_demo.py
```

---

## Verdict

| Question | Answer |
|----------|--------|
| **Ready for tomorrow’s teacher video?** | **Conditional yes** — console + 29/29 verify path is strong. **Prepare a 2-minute `invoke_agent` terminal demo** (`agent_smoke_test.py --ops` at minimum) to satisfy explicit Bedrock Agent requirement. |
| **Ready for next week’s classroom demo?** | **Yes**, with current `retrieve_and_generate` + offline fallback rehearsal. |
| **Current live path** | **`retrieve_and_generate`** (not `invoke_agent`) |
| **Mandatory features** | |

| Feature | Real | Mocked | Partial | Missing |
|---------|:----:|:------:|:-------:|:-------:|
| Flask + Docker | ✓ | | | |
| KB RAG (boto3) | ✓ | | | |
| Agent invoke (boto3) | ✓ | | flaky live | |
| 4 tools / Lambdas | ✓ | ops mock | app+AWS split | |
| Memory / follow-up | ✓ | | | |
| MCP server | | | conceptual | ✓ |
| Presentation / README | ✓ | | | |

### Must fix before submission (minimum)

1. **Narrate dual backend policy** in README or grading email (agent = teacher path; direct RAG = demo reliability).
2. **Fix `/healthz` typo** in live demo checklist.
3. **Demonstrate `invoke_agent`** on video (terminal or switch env after smoke pass).
4. **Approve and run cleanup** for `lambda-out.json` + `.gitignore` entries.

---

## Audit artifact index

| Document | Path |
|----------|------|
| Repository inventory | `docs/review/REPOSITORY_INVENTORY.md` |
| Unused files | `docs/review/UNUSED_FILES_REPORT.md` |
| Bedrock backends | `docs/review/BEDROCK_BACKEND_AUDIT.md` |
| Knowledge base | `docs/review/KNOWLEDGE_BASE_AUDIT.md` |
| Datasets | `docs/review/DATASET_AUDIT.md` |
| Lambda / action groups | `docs/review/LAMBDA_ACTION_GROUP_AUDIT.md` |
| MCP / tools | `docs/review/MCP_TOOLS_AUDIT.md` |
| Memory / history | `docs/review/MEMORY_AND_HISTORY_AUDIT.md` |
| System prompts | `docs/review/SYSTEM_PROMPT_REVIEW.md` |
| Security | `docs/review/SECURITY_AUDIT.md` |
| Cleanup plan | `docs/review/CLEANUP_PLAN.md` |
| This report | `docs/review/FINAL_AUDIT.md` |

**Phase 19 (deletions, archive moves, code fixes) is blocked until you approve the deletion list in `CLEANUP_PLAN.md`.**
