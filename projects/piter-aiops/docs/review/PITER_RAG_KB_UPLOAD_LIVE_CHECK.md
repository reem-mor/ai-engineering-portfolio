# PITER RAG, KB, and Upload Live Check

**Date:** 2026-06-08

## Knowledge Base (AWS)

- KB ID: `RBTJM6NIG9`
- Live retrieve_and_generate: citations returned (3+ in verify_live_demo Phase A)
- Agent path: citations in agent smoke (7/7 PASS)

## Active KB content

- Runbooks under `knowledge_base/` — no IncidentIQ branding in active docs
- S3 sync documented in prior `PITER_KB_S3_ALIGNMENT.md`

## Upload flow

| Check | Result |
|-------|--------|
| Allowed types | `.md`, `.txt`, `.csv`, `.json`, `.pdf`, `.docx` (per bootstrap) |
| Size limit | Configurable `max_upload_mb` (default 5) |
| Path traversal | Blocked — `tests/test_upload_validators.py` |
| Invalid type | Rejected — tests pass |
| Bedrock KB sync from UI | **Not implemented** |

**Demo wording:** Uploaded locally for demo/local RAG. Bedrock Knowledge Base sync is a separate step.

## UI

- Knowledge Base page lists manifest from `/api/kb/manifest`
- Upload via agent panel + KB page
- Screenshot: `screenshots/final/12_upload_document_flow.png`
