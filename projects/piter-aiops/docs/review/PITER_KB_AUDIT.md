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
Existing runbook sections already cover the canonical substance:

| Canonical section | Existing equivalent | Coverage |
| ----------------- | ------------------- | -------- |
| When to use | title + "Applies to" / "Alert name" + Symptoms | Covered (implicit) |
| Severity guidance | "Severity:" line + front matter `severity_applicable` | Covered |
| Prerequisites | bastion/connection notes in Detection checks | Light (implicit) |
| Investigation steps | "Symptoms" + "Detection checks" + "Detection/remediation SQL" | Covered (rich) |
| Triage decision tree | "Recommended steps" (ordered, with branch conditions) | Covered |
| Remediation | "Recommended steps" / "remediation SQL" | Covered |
| Verification | step conditions inside Recommended steps | Covered (implicit) |
| Rollback | "Dangerous actions" + RB-010 (dedicated rollback runbook) | Covered |
| Escalation | "Escalation path" | Covered (all runbooks) |
| Related | "Tags / services" | Covered |

> **Decision:** the runbooks are already complete and RAG-effective (verify_live_demo cites the
> Postgres CPU runbook successfully). I did **not** rename headings or inject new "Verification/
> Rollback/Prerequisites" prose, because deriving that text would risk introducing unverified
> operational steps — contrary to PITER's anti-hallucination principle. The only KB change in this
> pass is the `author` front-matter update. Explicit canonical-heading templating is recorded as an
> optional future enhancement to be authored from real operational sources, not generated.

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

## Status: PASS — front matter complete (author updated to "Re'em Mor"), sections cover all
canonical substance, no PII, RAG-effective. Heading re-templating deferred (optional, source-authored).
