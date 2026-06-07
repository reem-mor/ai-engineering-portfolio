# PITER AiOps — Cleanup Plan

Read-only proposal · 2026-06-06 · **Awaiting approval before any deletion or moves.**

## P0 — Blocks teacher requirement / demo / security / misleading claims

| ID | Item | Action | Risk if ignored |
|----|------|--------|-----------------|
| P0-1 | Teacher expects **`invoke_agent` demo**; live `.env` uses **`retrieve_and_generate`** | For submission video: run `scripts/agent_smoke_test.py` first; if ≥7/7, switch `RAG_BACKEND=agent` for recording segment **or** explicitly demo agent in terminal while keeping console on direct RAG | Grader may mark agent requirement unmet |
| P0-2 | UI shows `mode=bedrock` for both backends | Add `agent` / `retrieve_and_generate` / `local` in API + console (code change — separate PR) | Misleading “which path ran?” |
| P0-3 | `.env` must never be committed | Verify before any `git add .` checkpoint | Credential leak |
| P0-4 | `docs/LIVE_DEMO_CHECKLIST.md` references **`/healthz`** | Fix to **`/health`** | Demo prep failure |

## P1 — Top grade / doc mismatch / stale build / config

| ID | Item | Action |
|----|------|--------|
| P1-1 | README vs live demo backend conflict | Add “Live demo config” callout: direct RAG for reliability; agent for teacher alignment |
| P1-2 | `.env.example` says `RAG_BACKEND=agent` | Add comment that course demo may use `retrieve_and_generate` |
| P1-3 | `infra/bedrock_kb_s3_policy.json` stale prefix | Update S3 prefix to current bucket layout (do not delete file) |
| P1-4 | `frontend/src/App.tsx` code snippet shows only `retrieve_and_generate` | Add agent snippet or label “direct KB path” |
| P1-5 | Archive historical status docs | Move to `docs/archive/` after approval (see deletion table) |
| P1-6 | `.gitignore` gaps | Add `lambda-out.json`, `evaluation/pytest_output.txt`, `.ec2_instance_id.txt`, `.sg_id.txt` |
| P1-7 | Rebuild SPA if frontend changed | `cd frontend && npm ci && npm run build` → copy to `app/static/spa/` per project convention |

## P2 — Maintainability

| ID | Item | Action |
|----|------|--------|
| P2-1 | Dual corpus (`data/sample_documents/` vs `knowledge_base/runbooks/`) | Document in README; follow `evaluation/CORPUS_RECONCILIATION.md` |
| P2-2 | `MEMORY_ENABLED` unused in branching | Wire or remove from docs |
| P2-3 | `docs/review/_gen_inventory.py` | Delete after inventory approved |
| P2-4 | Consolidate authoritative docs | Map: README, architecture, LIVE_DEMO_CHECKLIST, GRADING_CHECKLIST, TEARDOWN |

## P3 — Polish

| ID | Item | Action |
|----|------|--------|
| P3-1 | Install ruff/mypy in dev deps | Optional CI quality gate |
| P3-2 | Rename `incidentiq-ops` folder | Defer — scripts depend on path |
| P3-3 | Security headers on EC2 | Reverse proxy / Talisman |

---

## Proposed deletions (approval required)

### Path: `lambda-out.json`

- **Reason:** Captured Lambda debug output; not referenced by runtime, tests, or Docker.
- **References checked:** `rg lambda-out` — documentation only.
- **Tests protecting deletion:** None.
- **Risk:** Low — no rebuild needed.
- **Recovery:** Re-invoke Lambda manually if needed.

### Path: `evaluation/pytest_output.txt`

- **Reason:** Stale captured pytest log.
- **References checked:** No script reads this file.
- **Tests protecting deletion:** None.
- **Risk:** Low.
- **Recovery:** `pytest -q > evaluation/pytest_output.txt` if desired.

### Path: `.ec2_instance_id.txt` (local only)

- **Reason:** EC2 helper artifact; should not be in repo.
- **References checked:** Not imported; may be gitignored.
- **Risk:** Low locally.
- **Recovery:** Re-run `scripts/launch_ec2_demo.ps1`.

### Path: `.sg_id.txt` (local only)

- **Reason:** Same as above.
- **Risk:** Low.
- **Recovery:** Re-run launch script.

### Path: `docs/review/_gen_inventory.py`

- **Reason:** One-off inventory generator after `REPOSITORY_INVENTORY.md` is accepted.
- **References checked:** None outside `docs/review/`.
- **Risk:** Low — regenerate inventory manually if needed.

---

## Proposed archive moves (approval required)

| From | To | Reason |
|------|-----|--------|
| `docs/PHASE0_AUDIT.md` | `docs/archive/PHASE0_AUDIT.md` | Superseded by `docs/review/` |
| `docs/UPGRADE_STATUS.md` | `docs/archive/UPGRADE_STATUS.md` | Point-in-time |
| `docs/DEPLOY_STATUS.md` | `docs/archive/DEPLOY_STATUS.md` | Point-in-time |
| `docs/cleanup_log.md` | `docs/archive/cleanup_log.md` | Historical |

**Do not delete** archived files unless explicitly requested.

---

## Explicitly do NOT delete

- `app/bedrock_agent_client.py`, `app/bedrock_client.py`, `app/rag_factory.py`
- `app/local_agent.py`, `app/enrichment_tools.py`
- All `action_groups/iiq-*` and `incidentiq-ops/`
- `app/static/spa/` (committed production build)
- `scripts/verify_live_demo.py`, `agent_smoke_test.py`, `kb_smoke_test.py`
- Full test suite and evaluation JSON
- Knowledge corpora under `data/` and `knowledge_base/`

---

## Post-approval execution checklist (Phase 19)

1. Create git checkpoint on branch `cleanup/piter-aiops-audit` (exclude `.env`).
2. Delete approved files only.
3. Move approved docs to `docs/archive/`.
4. Update `.gitignore` / `.dockerignore` if approved.
5. Apply P0/P1 doc fixes if approved separately.
6. Rebuild frontend → `app/static/spa/` if needed.
7. `python -m pytest`
8. `docker compose build && docker compose up -d && docker compose ps`
9. `python scripts/verify_live_demo.py` (with current `.env`)
10. `git status` summary to user.

---

## Smallest safe top-grade change set (recommended order)

1. Fix `/healthz` → `/health` in live demo checklist.
2. Document dual-backend policy in README (one paragraph).
3. Surface `RAG_BACKEND` value in `/api/triage` response + console badge.
4. Run agent smoke; record agent segment if passing.
5. Delete `lambda-out.json` + add `.gitignore` entries.
6. Archive four historical status docs.

No AWS deploy or `.env` flip without your explicit go-ahead.
