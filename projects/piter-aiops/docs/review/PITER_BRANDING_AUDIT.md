# PITER Branding Audit

**Target brand:** **PITER AiOps** — Priority, Investigation, Triage, Escalation, Resolution  
**Inspiration only:** Dropzone / incident-iq-compass (do not copy branding)

## Search results summary

| Pattern | Count (approx) | Severity |
|---------|----------------|----------|
| `IncidentIQ` / `incidentiq` | 50+ hits | Medium — mostly AWS names, action groups, docs |
| `incident-rag-bedrock` | 40+ hits | Medium — legacy S3/ECR/docs paths |
| `incident-assistant-rag` | Few | Low — IAM policy legacy ARNs |
| `iiq-*` | Widespread in Lambdas/action groups | Low — documented as AWS legacy names |
| `Dropzone` | Few in docs (inspiration notes) | OK if labeled inspiration |

## User-facing surfaces

| Surface | Current | Action |
|---------|---------|--------|
| React SPA title/branding | PITER AiOps | **OK** |
| `app/templates/console.html` | PITER branding in recent versions | Verify on record |
| README | PITER AiOps primary; maps `iiq-*` as AWS names | **OK** with footnote |
| AWS Bedrock Agent | Name: `incidentiq-triage-agent` | **FAIL** user-facing AWS console |
| Agent alias description | "IncidentIQ Flask demo app" | **FAIL** |
| docker-compose | `piter-aiops:dev` | **OK** |

## Safe local updates (no AWS)

- Fix S3 path strings in `evaluation/qa_showcase.md`, `scripts/kb_smoke_test.py` → `projects/piter-aiops/data/sample_documents`
- Update `docs/teacher_submission_email.md`, `docs/code_review.md` headers from incident-rag-bedrock → piter-aiops
- Add historical note on archived `screenshots/README.md` paths

## Requires AWS approval

- Rename Bedrock agent and alias description
- Rename Lambda functions `iiq-*` → `piter-*` (or leave and document)

## Dropzone

No Dropzone logos or copy detected in `frontend/src`. Design inspiration references in docs only — acceptable.
