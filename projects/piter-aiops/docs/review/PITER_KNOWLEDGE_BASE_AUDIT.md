# PITER Knowledge Base Audit

## Structure

```
knowledge_base/
├── runbooks/     (RB-001 … RB-014 + README)
├── environments/ (if present)
├── policies/
├── incidents/
└── glossary/
```

**S3 sync corpus:** `data/sample_documents/` (mirrors runbooks + legacy demo docs)  
**Prefix:** `projects/piter-aiops/data/sample_documents` (per `.env`)

## Runbooks (14 technical RB files)

| ID | File | In sample_documents | AWS indexed (last sync) |
|----|------|-------------------|-------------------------|
| RB-001–010 | Present | Mirrored | Yes (prior ingestion) |
| RB-011 | `RB-011-bet-service-outage.md` | `runbook_bet_service_outage.md` | Yes (4 new in last job) |
| RB-012–014 | New wallet/payment/game | Mirrored | Yes |

Last ingestion (prior session, read-only): 28 scanned, 4 new, 1 modified, 0 failed.

## Front matter / sections

RB-011 upgraded to PITER standard (v2.0). RB-012–014 created in session. Spot-check recommended for full YAML front matter on all 14 files — older RB-001–010 may predate strict template.

**Required sections checklist:** Apply `tests` or lint script for missing "When to use", "Escalation", etc. — not fully automated today.

## Quality checks

| Check | Status |
|-------|--------|
| No secrets in KB markdown | PASS (spot + source tests) |
| No raw phone/email in KB | PASS in sampled runbooks |
| No IncidentIQ wording in runbooks | PASS in RB-011–014 |
| Duplicate docs | `knowledge_base/` vs `sample_documents/` intentional mirror |
| Dataset runbook refs resolve | PASS (`test_source_data.py`) |

## Decision

**Keep both** `knowledge_base/runbooks/` (authoring) and `data/sample_documents/` (RAG + S3). Do not delete either.

## Gaps

- Automate front-matter validation in CI
- Fix evaluation doc S3 paths still pointing at `incident-rag-bedrock`
- Optional: deprecate redundant files only in `sample_documents` that are not mirrored in `knowledge_base`
