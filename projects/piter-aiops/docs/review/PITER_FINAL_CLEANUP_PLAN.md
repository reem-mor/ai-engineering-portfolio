# PITER Final Cleanup Plan

Audit of cleanup candidates for the enterprise upgrade. **No deletions** have been performed — this document is the gate for future archive/remove decisions.

## Decision rules

- Do not delete working routes, tests, datasets, or KB docs without explicit approval.
- Do not remove `/console` until SPA storm flow passes equivalent verification (`scripts/verify_spa_demo.py`).
- AWS-deployed `iiq-*` action groups stay until a rename/deploy is approved.

## Candidate inventory

| Path | Problem | Used by | Action | Risk |
|------|---------|---------|--------|------|
| `frontend/src/components/DemoDashboard.tsx` | Orphan UI from prior iteration | Not imported by `App.tsx` | Archive after SPA wiring reuses patterns | Low |
| `frontend/src/components/EnrichmentPanel.tsx` | Orphan UI | Not imported by `App.tsx` | Archive after SPA wiring reuses patterns | Low |
| `frontend/src/components/FormattedAnswer.tsx` | Orphan UI | Not imported by `App.tsx` | Archive after SPA wiring reuses patterns | Low |
| `frontend/src/components/AppTopBar.tsx` | Orphan UI | Not imported by `App.tsx` | Archive after SPA wiring reuses patterns | Low |
| `frontend/src/routes/` | Unused TanStack routing scaffold | Not in `main.tsx` entry | Delete after confirming no imports | Low |
| `frontend/.lovable/`, `bun.lock` | Legacy generator artifacts | None critical | Archive `bun.lock` if npm-only | Low |
| `app/templates/*` (except `console.html`) | Legacy Jinja UI duplicate | Fallback when SPA missing | Keep until SPA-only verified | Medium |
| `app/static/css`, `app/static/js` | Legacy static for Jinja | Jinja templates | Keep with templates | Medium |
| `action_groups/iiq-*` | Old naming + triplicated data/tools | AWS deploy scripts, Bedrock agent | Keep (deployed); document as legacy | High |
| `action_groups/piter-*` | Target final four tools | Tests (`test_piter_lambdas.py`) | Keep — canonical local source | Low |
| `action_groups/incidentiq-ops/` | Old branding folder | `setup_action_group.py` | Keep; rename only with AWS approval | High |
| `knowledge_base/runbooks/RB-*.md` | Were missing YAML front matter | KB manifest, Bedrock sync | Improved in Phase 4 | Medium |
| `data/sample_documents/` vs `knowledge_base/` | Dual corpus | Local RAG + Bedrock S3 sync | Keep both; one-way KB → sample sync | Medium |
| `data/agent_data/` vs `data/source/` | Two deploy schemas | Runtime enrichment vs generator | Keep both; `bet-service` added to agent_data for storm | Medium |
| `infra/ec2_user_data_*.sh` | References old ECR image names | EC2 deploy docs | Doc-only alignment when approved | Medium |
| `docs/TEARDOWN.md`, `evaluation/*` | Real AWS IDs, point-in-time smoke | Reference | Keep; redact in new docs if needed | Low |
| `screenshots/archive/` | Stale captures | Submission history | Archive after re-capture | Low |
| `.env`, `.env.production` | Secrets on disk | Local runtime | Never commit | Critical |

## Completed in enterprise upgrade (no cleanup required)

| Deliverable | Status |
|-------------|--------|
| SPA wired to `/api/alert-stream`, `/api/triage`, `/api/follow-up`, `/api/kb/manifest` | Done |
| 399 alert storm labels from live API | Done |
| RB runbook YAML front matter + RB-011 | Done |
| OpenAPI for `piter-*` action groups | Done |
| `scripts/verify_spa_demo.py` (36 checks) | Done |
| `/console` redirect gated by `PITER_CONSOLE_REDIRECT_SPA=false` | Done |

## Recommended next cleanup (post-demo, user approval)

1. Move orphan React components to `frontend/src/_archive/` or delete after extracting reusable pieces.
2. Remove `frontend/src/routes/` if still unused.
3. Archive legacy Jinja templates once `/console` redirect is enabled and verified manually.
4. Deduplicate `action_groups/*/enrichment_tools.py` into shared module at Lambda deploy time.

## Out of scope without explicit approval

- AWS resource changes, Lambda deploy, Bedrock Agent/KB/Guardrails/S3/IAM changes
- Real SNS/SES sends
- GitHub push or force operations on main
