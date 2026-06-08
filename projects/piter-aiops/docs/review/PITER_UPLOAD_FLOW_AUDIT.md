# PITER Upload Flow Audit

## Route

`POST /documents/upload` → `DocumentUploadService.upload()` (`app/upload_service.py`)

## Supported types

**Implemented:** `.md`, `.txt`, `.csv`, `.docx`, `.pdf` (`app/upload_validators.py`)

**Documented but NOT implemented:** `.json`, `.xlsx` — update docs or extend validator.

## Security

| Control | Status |
|---------|--------|
| Filename validation | PASS — non-empty, suffix whitelist |
| Size limit | PASS — `MAX_UPLOAD_BYTES` (default 5 MiB) |
| Path traversal | PASS — `secure_filename` + `_SAFE_KEY` sanitization |
| S3 key | Timestamp-prefixed under `PITER_S3_PREFIX` |

## Bedrock KB sync

- Optional `sync_kb=true` on upload starts `start_ingestion_job` when `BEDROCK_DATA_SOURCE_ID` set
- On failure: upload succeeds with `sync_warning` / `partial: true`
- **Local RAG:** Uploaded files are **not** auto-indexed into TF-IDF corpus — requires restart or manual copy into `sample_documents/` + rebuild

## User messaging

SPA should state: *"Uploaded to S3; Bedrock KB sync when enabled. Local demo corpus is separate unless file is added under data/sample_documents."*

## Citations after upload

Bedrock path: available after ingestion completes (async). Local path: not available until corpus reload.

## Gaps

1. Add `.json` to allowed suffixes if required for course demo
2. Document local vs Bedrock ingestion clearly in UI
3. Optional: trigger `LocalRetriever` cache clear after local file drop
