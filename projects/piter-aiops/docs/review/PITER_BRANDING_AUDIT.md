# PITER AiOps — Branding Audit

- **Author:** Re'em Mor
- **Date:** 2026-06-07
- **Final user-facing brand:** **PITER AiOps**

## Method
Case-insensitive `git grep` across all tracked files for legacy/external brand terms.

| Term | Tracked files | Classification |
| ---- | ------------- | -------------- |
| `IncidentIQ` / `incidentiq` | 12 | Historical review docs + infra/IAM identifiers (`incidentiq-lambda-role`, `incidentIQ-midproject` S3 prefix) + `action_groups/incidentiq-ops/` folder. **Not user-facing.** |
| `incident-iq` | 1 | `README.md` reference to `incident-iq-compass` design inspiration (clearly labeled). Keep. |
| `incident-assistant` | 2 | Archived S3 policy paths (`infra/bedrock_kb_s3_policy*.json`). Not user-facing. |
| `incident-rag` | 20 | Predecessor project name in docs/scripts/infra (KB setup history). Archived/historical. |
| `iiq` | 46 | Legacy AWS Lambda/action-group names (`iiq-context`, `iiq-correlate`, `iiq-similar`) + demo events + docs. **Map to live AWS resources** — kept by user decision. |
| `Dropzone` | 1 | CSS comment in `frontend/src/styles.css` ("DropZone-style SOC"). Inspiration only — wording neutralized in branding commit. |
| `lovable` | 6 | Frontend dev tooling only (`bun.lock`, `bunfig.toml`, two `frontend/src` import paths). Not branding. |

## User-facing surfaces — verified
- `frontend/src/**`, `app/templates/**`, `app/static/spa/index.html`: brand is **PITER AiOps**.
  No capitalized product name "IncidentIQ" rendered to users.
- SPA `<title>` / meta description: "PITER AiOps …" (correct).

## Actions taken (Commit 3 — branding)
1. `frontend/src/styles.css`: rename comment "DropZone-style SOC" → neutral "enterprise SOC palette"
   (avoid copying an external brand name even in comments). No visual change.
2. Verified no user-facing string requires change (brand already PITER AiOps).

## Intentionally NOT changed
- Legacy `iiq-*` / `incidentiq-ops` action-group folders and IAM/S3 identifiers — they correspond to
  **deployed AWS resources**; renaming is an AWS-coordinated change (out of scope, gated).
- Historical references inside `docs/review/*` and predecessor-project docs — labeled historical.
- `incident-iq-compass` / Dropzone mentions as *design inspiration* (not copied branding).

## Result
No user-facing legacy branding remains. Remaining matches are historical docs or live-AWS
identifiers, all documented above.
