# PITER Proposed Deletions / Archives

**Rule:** No deletions executed in this audit. Approval required for high-risk items.

| Path | Reason | Replacement | References checked | Risk | Recovery | Tests required |
|------|--------|-------------|-------------------|------|----------|----------------|
| `action_groups/iiq-*/data/*.csv` (duplicates) | Duplicate of `data/source` | Canonical `data/source/` | Lambdas import local copies | **High** — breaks Lambda deploy package | Git restore | `test_piter_lambdas`, deploy smoke |
| `data/agent_data/` | Legacy postgres demo catalog | `data/source/` + fallback in `enrichment_tools` | `verify_live_demo`, enrichment tests | **Medium** | Git restore | `test_enrichment_tools` |
| `app/templates/index.html` HTMX landing | Superseded by SPA when built | React SPA at `/` | `FORCE_LEGACY_UI=true` path | **Medium** | Git restore | SPA + grading checklist |
| `app/templates/console.html` | Duplicate of SPA triage UX | React SPA + redirect flag `PITER_CONSOLE_REDIRECT_SPA` | `verify_live_demo`, `GRADING_CHECKLIST` | **High** | Git restore | 29/29 verify script |
| `action_groups/incidentiq-ops-test` (AWS) | Disabled test group on agent | Remove from agent | AWS list shows DISABLED | Low | Recreate in console | Agent smoke |
| `screenshots/archive/*` | Stale captures | Regenerate with `scripts/capture_*.mjs` | README only | Low | Git history | Visual |
| `infra/ec2_user_data*.sh` legacy image names | `incident-rag-bedrock` image refs | GHCR `piter-aiops` or doc-only | EC2 terminated per cleanup_log | Low | Edit not delete | — |
| `evaluation/CORPUS_RECONCILIATION.md` | Historical merge log | `docs/knowledge_base.md` | Reference only | Low | Archive to `docs/review/archive/` | — |
| Duplicate `enrichment_tools.py` in 3× iiq folders | Copy-paste drift | Shared module / Lambda layer | Lambda handlers | **High** | Git restore | Lambda tests |

## Do NOT delete

- `data/sample_documents/` — local RAG + S3 sync source
- `knowledge_base/runbooks/` — canonical KB authoring
- `action_groups/piter-*` — target Lambda source
- `app/static/spa/` — production UI bundle
- Any route used by `verify_live_demo.py`
