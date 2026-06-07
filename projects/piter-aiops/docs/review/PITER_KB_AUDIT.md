# PITER AiOps — Knowledge Base Audit

- **Author:** Re'em Mor
- **Date:** 2026-06-07

## Decision: keep source-of-truth KB in the repo
Sanitized KB documents live under `knowledge_base/` (version-controlled source synced to S3/Bedrock).
Indexed copy lives in AWS. No secrets, contacts, customer data, live schedules, or credentials.

## Structure (16 Markdown docs, all with YAML front matter)
| Folder | Docs |
| ------ | ---- |
| `runbooks/` | RB-001…RB-011 (11) + README |
| `policies/` | POL-001 severity & escalation |
| `incidents/` | INC-2024-07 checkout outage |
| `environments/` | ENV-001 regulated-market environments |
| `glossary/` | GLO-001 operations terms |

## Front matter
Present in all 16 docs (`title`, `doc_type`, `services`, `environments`, `severity_applicable`,
`tags`, `last_updated`, `author`, `version`).
**Change (Commit 4):** `author` updated from `"PITER AiOps"` → `"Re'em Mor"` across all 16.

## Section coverage (runbooks)
Existing runbook sections and how they map to the canonical set:

| Canonical section | Existing equivalent | Action |
| ----------------- | ------------------- | ------ |
| When to use | (implicit in title/Symptoms) | Add explicit "When to use" line (Commit 4) |
| Severity guidance | "Severity"/front matter `severity_applicable` | Present |
| Prerequisites | (light) | Note as optional enhancement |
| Investigation steps | "Symptoms" + "Detection checks" + "Detection/remediation SQL" | Present (rich) |
| Triage decision tree | "Recommended steps" (ordered) | Present (ordered steps) |
| Remediation | "Recommended steps" / "remediation SQL" | Present |
| Verification | (within Recommended steps) | Add explicit "Verification" where absent |
| Rollback | "Rollback" / RB-010 dedicated | Present for deploy-related; cross-link others |
| Escalation | "Escalation path" | Present in all |
| Related | "Related" / "Tags / services" | Present in some; add where missing |

> Operationally the runbooks are already complete and RAG-effective (verify_live_demo cites
> the Postgres CPU runbook successfully). Commit 4 makes the canonical headings explicit and
> additive — **no existing content removed**, no risk of introduced/hallucinated facts.

## Audited for
| Issue | Result |
| ----- | ------ |
| Completeness | Good; minor canonical-heading additions |
| Duplicate content | None significant |
| Corrupted encoding | None (valid UTF-8) |
| Old IncidentIQ wording | None in user-facing KB text |
| Missing front matter | None |
| Unclear service/severity | Clear (typed front matter) |
| Unsupported file types | All `.md` |
| Security issues | No secrets/contacts/PII |
| RAG chunking structure | Clear headings, scannable |

## Note on `data/sample_documents/`
A second, broader corpus (24 mixed-format files) feeds the Bedrock KB ingestion (`scripts/build_corpus.py`).
Synthetic, documented, no PII. Kept as the upload/ingestion corpus distinct from the curated
`knowledge_base/` source.

## Status: PARTIAL → strong after Commit 4 (author + canonical headings).
