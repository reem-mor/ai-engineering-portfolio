# Knowledge base

## Layout

```
knowledge_base/
├── runbooks/       RB-001 … RB-014 (YAML front matter required)
├── environments/   ENV-*
├── policies/       POL-*
├── incidents/      INC-*
└── glossary/       GLO-*
```

## Front matter

Every markdown file (except `README.md`) must include:

`title`, `doc_type`, `services`, `environments`, `severity_applicable`, `tags`, `last_updated`, `author`, `version`

Validated by `tests/test_knowledge_base.py`.

## Runtime corpus

- **Bedrock / S3 sync:** `data/sample_documents/`
- **Local RAG fallback:** same directory
- **Manifest API:** `GET /api/kb/manifest` reads `knowledge_base/` metadata

## Sync policy

Improve structured docs under `knowledge_base/`, then mirror content into `data/sample_documents/` for RAG.
One-way sync only — do not copy volatile on-call or deployment data into markdown.

## Demo-critical docs

- `RB-011-bet-service-outage.md` — P1 storm scenario for GIB-UKGC
- `RB-012-wallet-transaction-failures.md` — wallet tier-0 transaction failures
- `RB-013-payment-provider-degradation.md` — payment provider routing degradation
- `RB-014-game-provider-latency.md` — game launch and provider handoff latency
- `RB-007-postgres-cpu-high.md` — verify_live_demo postgres scenario
- `POL-001-severity-and-escalation.md` — severity and notification safety
