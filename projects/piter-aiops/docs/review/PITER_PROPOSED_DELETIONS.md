# PITER AiOps — Proposed Deletions (NO deletion performed)

- **Author:** Re'em Mor
- **Date:** 2026-06-07
- **Status:** Proposal only. Nothing deleted. High-risk items require explicit approval.

| Path | Reason | Replacement | References checked | Risk | Recovery | Tests required |
| ---- | ------ | ----------- | ------------------ | ---- | -------- | -------------- |
| `action_groups/iiq-context/` | Legacy duplicate of `piter-service-context` | `action_groups/piter-service-context/` | Referenced by `scripts/setup_action_group.py`, tests, docs; **maps to live AWS Lambda** | HIGH | git history | pytest + live verify |
| `action_groups/iiq-correlate/` | Legacy duplicate of `piter-recent-deployments` | `piter-recent-deployments` | Same as above | HIGH | git history | pytest + live verify |
| `action_groups/iiq-similar/` | Legacy duplicate of `piter-similar-incidents` | `piter-similar-incidents` | Same as above | HIGH | git history | pytest + live verify |
| `action_groups/incidentiq-ops/` | Legacy mock-ops 4th function | (optional; not in core 4) | `setup_action_group.py`, `test_lambda_action_handler.py` | HIGH | git history | pytest |
| `evaluation/*.md` (point-in-time captures) | Stale smoke/run reports | superseded by `docs/review/PITER_*` | Some linked from docs | LOW | git history | none |
| `docs/DEPLOY_STATUS.md`, `docs/UPGRADE_STATUS.md` | Point-in-time status | `PITER_FINAL_READINESS_REPORT.md` | linked in places | LOW | git history | none |
| `.playwright-mcp/` (root) | Tooling artifact (outside project scope) | — | — | n/a | git history | none — **out of workspace scope; not touched** |

## Decision (this pass)
- **Keep all `iiq-*` / `incidentiq-ops` folders** (user decision) — they correspond to deployed AWS
  function names. Deleting them and renaming AWS functions is a separate, AWS-coordinated step,
  gated on explicit approval.
- Stale `evaluation/*` and `*STATUS*` docs: **retained** for submission history; deletion deferred.
- No deletions executed. Re-run `pytest` + `verify_live_demo.py` before any future deletion.
