# Deprecated — canonical runbooks moved

**Source of truth:** [`data/sample_documents/`](../../data/sample_documents/)

RB-001 through RB-010 content has been merged into stable descriptive filenames
in the canonical corpus (for example `runbook_db_cpu.md` carries **RB-007**).
Local RAG and Bedrock KB both read from `data/sample_documents/` only.

The `RB-*.md` files in this directory are retained as historical references and
are **not** uploaded to S3 or indexed in Bedrock. See
[`evaluation/CORPUS_RECONCILIATION.md`](../../evaluation/CORPUS_RECONCILIATION.md).
