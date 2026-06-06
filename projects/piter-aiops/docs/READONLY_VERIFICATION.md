# Read-only verification log

**Date:** 2026-06-03  
**Scope:** Local tests/build + AWS **read-only** describe/list (no create/update/delete/sync/deploy).

## Local

| Check | Result | Notes |
|-------|--------|-------|
| `pytest -q` | **PASS** | 140 tests, `.venv` Python 3.12 |
| `npm ci && npm run build` | **PASS** | Bundle `app/static/spa/assets/index-CVCjA5m8.js` |
| SPA contains `/api/workflow/triage` | **PASS** | Grep on built JS |
| `docker compose build` | **PASS** | Image `incidentiq-midproject:dev` |
| `.env` gitignored | **PASS** | `.gitignore` lists `.env`, `.env.production` |
| Secret scan (repo) | **PASS** | No `AKIA…` / API keys in tracked source; docs mention not putting keys on EC2 |

## AWS read-only (profile `reemmor`, `us-east-1`)

| Resource | ID / name | Status |
|----------|-----------|--------|
| Account | `329597159579` | `sts get-caller-identity` OK |
| Knowledge Base | `RBTJM6NIG9` (`incidentiq-course-kb`) | **ACTIVE** |
| Bedrock Agent | `HH4YGSLZUE` (`agent-quick-reemmnor`) | **PREPARED** |
| Agent alias `live` | `O2EM03R4R3` | Listed |
| Lambda `iiq-correlate` | — | Exists |
| Lambda `iiq-context` | — | Exists |
| Lambda `iiq-similar` | — | Exists |

## Live smoke (informational — not blocking polish)

| Script | Result | Notes |
|--------|--------|-------|
| `scripts/kb_smoke_test.py` | **1/7 PASS** | `RetrieveAndGenerate` failed with Marketplace/model access `403` on inference profile in local `.env`; agent path may still work via `invoke_agent` with different model binding |

Re-run after model subscription fix:

```powershell
$env:AWS_PROFILE="reemmor"
$env:AWS_REGION="us-east-1"
python scripts\kb_smoke_test.py
python scripts\agent_smoke_test.py
```

## Repo polish completed (this pass)

- Frontend: `EnrichmentPanel`, triage `session_id` + follow-up box
- SPA rebuilt to `app/static/spa/`
- `incidentiq_architecture.mermaid` + README agent diagram
- `docs/SUBMISSION_CHECKLIST.md`, agent screenshot list in `screenshots/README.md`

## Not performed (requires explicit approval)

- KB sync, Lambda deploy, agent prepare, EC2 launch, Gateway/Cognito, screenshot capture, teardown
