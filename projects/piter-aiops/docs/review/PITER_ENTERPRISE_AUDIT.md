# PITER AiOps — Enterprise Audit

- **Author:** Re'em Mor
- **Date:** 2026-06-07
- **Scope:** `projects/piter-aiops` (read-only audit; no files deleted)
- **Method:** 3 parallel code-exploration passes + targeted `git grep` + baseline test/verify runs.

This is the Phase 1 repository audit. It complements (does not replace) the earlier audits already
present in `docs/review/` (`FINAL_AUDIT.md`, `LAMBDA_ACTION_GROUP_AUDIT.md`, `SECURITY_AUDIT.md`, etc.).

## Baseline confirmed at audit time
| Check | Result |
| ----- | ------ |
| `python -m pytest` | **238 passed** |
| `python scripts/verify_live_demo.py` | **28/29** in this sandbox — only `[A] served by bedrock` fails (no live AWS creds). Phase B local fallback = 14/14; all tool/citation/memory checks pass. True 29/29 needs a real `.env` + credentials. |
| `npm ci && npm run build` (frontend) | clean build into `app/static/spa` |
| `docker compose config` | `image: piter-aiops:dev`, `container_name: piter-aiops`, `8080:8080` |

> Note: one safe code fix was applied during baseline verification —
> `app/services/notification_dispatch.check_sms_account_ready` now degrades gracefully on
> `BotoCoreError` (no AWS credentials / no network) instead of raising. This makes the documented
> offline behaviour true and unblocks `/`, `/api/bootstrap`, and `/console` without AWS access.

## Findings

| Area | Finding | Evidence | Risk | Recommendation | Safe to change now? |
| ---- | ------- | -------- | ---- | -------------- | ------------------- |
| Secrets / PII | A personal phone (`+972-***-5754`) and two personal emails (`r***@gmail.com`, `f***@gmail.com`) committed as defaults/examples | `docs/free-tier-oncall-notifications.md`, `docs/notifications.md`, `docs/teacher_submission_email.md`, `infra/notifications_policy_resolved.json`, `scripts/diagnose_sms.py`, `scripts/fix_sms_subscription.py`, `scripts/setup_notifications.py`, `scripts/enable_sms.ps1`, `scripts/setup_free_tier_oncall.ps1` | High (PII exposure in a graded public repo) | Redact to placeholders / env-only (no hardcoded default). **Done in Commit 2.** | Yes |
| Secrets / Infra IDs | AWS account id `329597159579` and bucket `reem-amdocs-ai-artifacts-3331` appear in ~20 docs/infra/evaluation files | `README.md`, `PLAN.md`, `infra/*.json`, `docs/*`, `evaluation/*` | Low–Med (identifiers, not credentials) | User decision: **retain**; documented as accepted residual. No live `AKIA` keys exist. | No (kept by decision) |
| Credentials | No `AKIA…` access keys committed; `.env` is gitignored (only `.env.example` tracked) | `git grep -E "AKIA[0-9A-Z]{16}"` empty; `git check-ignore .env` → ignored | Low | None | n/a |
| Duplicate backend logic | Action-group business logic exists both in `app/enrichment_tools.py` and mirrored in each `action_groups/piter-*/lambda_function.py` (by design — Lambda packaging) | `app/enrichment_tools.py`, `action_groups/piter-*/` | Low | Document the single-source-of-truth pattern; keep | Yes (doc only) |
| Old branding (folders) | Legacy `action_groups/iiq-context`, `iiq-correlate`, `iiq-similar`, `incidentiq-ops` duplicate the 4 `piter-*` lambdas | `action_groups/` | Med (confusion); they map to **live AWS function names** | User decision: **keep + document as legacy**; listed in `PITER_PROPOSED_DELETIONS.md` (no delete) | No (kept by decision) |
| Old branding (text) | No capitalized `IncidentIQ` anywhere. Lowercase `iiq`/`incident-rag`/`incident-assistant` survive in archived docs, IAM names, S3 paths | `git grep -i` (see `PITER_BRANDING_AUDIT.md`) | Low | Label as historical; user-facing brand is already PITER AiOps | Partial (text only) |
| Frontend `lovable` refs | `lovable` appears only in `frontend/bun.lock`, `bunfig.toml`, and two `frontend/src` import paths (dev tooling, not user-facing branding) | `frontend/` | Low | Leave (build tooling) | n/a |
| Stale reports | Many `evaluation/*.md` and `docs/*STATUS*.md` are point-in-time captures | `evaluation/`, `docs/DEPLOY_STATUS.md`, `docs/UPGRADE_STATUS.md` | Low | List in `PITER_PROPOSED_DELETIONS.md`; do not delete without approval | No |
| Screenshots | `screenshots/` mixes KB/agent/lambda/EC2/console captures (some may be stale) | `screenshots/*.png` | Low | Keep for submission; re-capture UI shots after UI commit | Yes (additive) |
| Alert count | `data/source/alert_stream.csv` has **400** rows (not 399/500) | `wc -l` / generator | Low | Option A: label UI "~400 deterministic alerts" | Yes |
| KB front matter | Author is `"PITER AiOps"`; task requests `"Re'em Mor"` | `knowledge_base/**/*.md` | Low | Update author; verify section completeness | Yes |
| Hardcoded AWS IDs in code | None — all IDs/region read from env via `app/config.py` | `app/config.py`, `app/bedrock_*_client.py` | Low | None | n/a |
| Notification preflight crash | `check_sms_account_ready` raised on missing creds (now fixed) | `app/services/notification_dispatch.py` | Was High (broke offline demo) | **Fixed** (graceful degrade) | Done |
| MCP | No standalone MCP server; Bedrock action groups + app tool router only | `docs/mcp.md`, `config/mcp.json.example`; no `mcp/server.py` | Med (course asks to "demonstrate MCP/tools") | Add minimal read-only `mcp/` scaffold mapping the 4 PITER tools | Yes (additive) |

## Conclusion
The platform is fundamentally sound and course-aligned. The only **high-risk** finding is committed
personal PII, addressed in Commit 2. All other items are documentation, additive scaffolding, or
explicitly retained by user decision. No baseline-breaking changes are required.
