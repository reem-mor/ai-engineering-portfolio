# PITER Full Code Review

**Date:** 2026-06-08 | **Scope:** `projects/piter-aiops/` | **Mode:** Read-only

## Executive summary

The project meets its demo baseline (251 pytest, 29/29 `verify_live_demo.py`). Architecture is sound: Flask API + React SPA + Bedrock KB/Agent + local TF-IDF fallback + four enrichment tools. Main risks are **duplicate triage pipelines**, **session/follow-up drift**, **legacy IncidentIQ naming in AWS and action groups**, and **security posture (CSRF-exempt API, live notification mode in local `.env`)**.

## Findings table

| Area | Finding | Evidence | Risk | Recommendation | Safe to fix now? |
|------|---------|----------|------|----------------|----------------|
| Triage | Every `/api/triage` runs `analyze_incident()` **and** `run_plan()` (4 tools); analysis overwrites tool outputs but follow-up reads raw `tool_outputs` | `app/services/triage_service.py` ~84–96, 195–218 | Follow-up answers can disagree with triage card (escalation, deploy, impact) | Merge analysis into session store or skip `run_plan` when analysis succeeds | Yes (local) |
| Triage | `compose_piter_sections` calls `compose_piter_answer` internally; triage calls both | `incident_analysis.py` ~549–552, `triage_service.py` | Redundant CPU on hot path | Call sections only once | Yes |
| incident_analysis | Priority uses string compare `priority > "P2"` in one branch | `incident_analysis.py` ~227 | Fragile if labels change | Use `_rank()` helper consistently | Yes |
| incident_analysis | Runbook fallback hardcoded RB-011 only | `incident_analysis.py` ~348–350 | RB-012–014 may report `found: false` in analysis | Generalize runbook map | Yes |
| incident_analysis | `postgres` demo service absent from `data/source/service_owners.csv` | `triage_service.DEMO_ALERT`, `incident_analysis` owner lookup | Demo card missing structured `priority_rationale` / `escalation_policy` for default postgres query | Add postgres row or mark legacy-only | Yes |
| action_groups | `incidentiq-ops` uses env codes `GIB`, `NJ` vs canonical `GIB-UKGC`, `NJ-DGE` | `action_groups/incidentiq-ops/lambda_function.py` ~28–67 | Agent tool 400 on real env codes | Align with `data/source` | Yes (local); AWS deploy needs approval |
| action_groups | Deployed Lambdas: `iiq-correlate`, `iiq-context`, `iiq-similar` only; `piter-escalation` not in AWS | `aws lambda list-functions` | Fourth tool only local/Flask path | Deploy `piter-escalation` or document gap | AWS approval |
| action_groups | Duplicate `enrichment_tools.py` per Lambda folder vs `app/enrichment_tools.py` | `action_groups/iiq-*/enrichment_tools.py` | Drift on redeploy | Shared layer or code-gen | Larger refactor |
| Security | Entire `main_bp` CSRF-exempt | `app/__init__.py` ~68 | CSRF on exposed demo host | Document demo-only or enforce token on JSON POSTs | Yes (docs) / careful for API |
| Security | App-level guardrails only; no Bedrock Guardrails ID in config | `app/guardrails.py`; no `PITER_GUARDRAIL_*` | No managed Bedrock guardrail in production path | Add optional guardrail ARN + docs | AWS approval |
| Performance | `data_access` loaders uncached; repeated full CSV scans per triage | `data_access.py`, `incident_analysis.py`, `enrichment_tools.py` | Latency under load | `@lru_cache` or per-request snapshot | Yes |
| Performance | SNS preflight on every `GET /api/bootstrap` when AWS configured | `routes.py` ~117, `notification_dispatch.py` | Slow page load | Cache bootstrap SMS status | Yes |
| Frontend | Triple UI: HTMX `/`, Jinja `/console`, React SPA `/` | `app/templates/`, `frontend/src/App.tsx` | Maintenance burden | Keep `/console` until SPA parity signed off | Partial |
| Frontend | Two triage APIs: `/api/triage` vs `/api/workflow/triage` | `routes.py` | Inconsistent card shape | Unify or document | Docs first |
| Branding | AWS agent name `incidentiq-triage-agent`; alias description mentions IncidentIQ | `aws bedrock-agent get-agent` | Confusing in demo/console | Rename in AWS console | AWS approval |
| Branding | Stale `incident-rag-bedrock` paths in scripts/docs/infra | `scripts/kb_smoke_test.py`, `infra/bedrock_kb_s3_policy*.json`, `docs/ec2_deployment.md` | Wrong S3 prefix on ops | Update to `piter-aiops` prefix | Yes (docs/scripts) |
| Docs | `evaluation/qa_showcase.md` wrong S3 corpus path | line 5 | Misleading submission artifact | Fix path | Yes |
| Tests | Missing follow-up test after P1 storm triage | `tests/test_flask_routes.py` vs `test_agent.py` | Regression risk on session memory | Add test | Yes |
| Upload | `.json` not in `ALLOWED_UPLOAD_SUFFIXES` though user docs mention it | `app/upload_validators.py` | User confusion | Add `.json` or update docs | Yes |
| Upload | Upload does not update local TF-IDF index automatically | `upload_service.py`, `local_rag.py` | Uploaded docs invisible to local RAG until restart | Document or reload corpus | Docs / optional code |

## What is solid

- **`data_access` + `test_source_data.py`:** Schema validation, 400-row storm, single P1 trigger, runbook reference integrity.
- **Notification safety gates:** Allowlist, confirmation token, severity gate, masked preview (`piter-escalation`, `notification_dispatch`).
- **Upload hardening:** Suffix whitelist, size cap, `secure_filename`, timestamped S3 keys.
- **Bedrock clients:** Retries, structured citations, local fallback on `BedrockError`.
- **MCP story:** Accurate README — Action Groups ≠ MCP; local MCP mirrors contracts.
- **Docker branding:** `piter-aiops:dev`, container `piter-aiops`, port 8080.

## Code review + simplify (subagent synthesis)

**High:** Session follow-up vs triage card mismatch; `incidentiq-ops` env code mismatch.  
**Medium:** Duplicate triage brain; uncached dataset I/O; triple UI surfaces.  
**Low:** Legacy `iiq-*` naming; in-process idempotency in escalation Lambda.

No files were modified in this review document pass.
