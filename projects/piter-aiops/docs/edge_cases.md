# Edge cases — PITER AiOps (Flask + HTMX + Bedrock KB)

Application-level behavior for validation, retrieval, and UI. Corpus ingestion edge cases (empty PDF, malformed DOCX) are handled by Bedrock during sync; the app documents how those show up at query time.

## Input validation

| Case | Server | UI |
|------|--------|-----|
| Empty / whitespace-only question | `400` · `empty_question` | Error card in `#answer` or workflow panel |
| Question shorter than 3 characters | `400` · `short_question` | Client-side block before HTMX + server 400 |
| Question longer than 500 characters | `400` · `oversize_question` | Character counter + `maxlength=500` on inputs |
| Stopwords-only (e.g. "the and or") | `400` · `stopwords_only` | Inline validation message; no AWS call |

Validation is centralized in `app/validators.py` and shared by `/ask` and `/workflow/triage`.

## Retrieval and grounding

| Case | Behavior |
|------|----------|
| Off-topic question (no KB hits) | Amber **Not in knowledge base** badge; refusal text; `grounded=false` |
| Grounded answer with citations | Green badge; `source_label` (basename) as primary citation title; full S3 URI in tooltip |
| Duplicate citation chunks | Deduped by `(source_uri, snippet_prefix)` before render |
| Empty citation snippets | Filtered in `BedrockRagClient` before response |

## Workflow triage (MVP)

| Case | Behavior |
|------|----------|
| Ungrounded KB response | Decision overridden to **escalate**; reason explains insufficient context |
| Grounded response | Alert metadata `decision` / `decision_reason` shown; action bullets parsed from answer lines (`-`, `*`, numbered lists) — heuristic, not a second LLM call |
| Bedrock throttling / IAM / config | `502` error card with retry hint |

## Transport and client errors

| Case | Behavior |
|------|----------|
| HTMX network / 5xx failure | `htmx:responseError` handler in `app.js` → friendly “Service unavailable” snippet |
| JSON API (`Accept: application/json` or `?format=json`) | Same validation and Bedrock errors as HTML; structured `ok` / `reason` / `message` or full `RagAnswer` payload |
| Unicode / RTL text in questions | Accepted when length rules pass; rendered with Jinja autoescape (no raw model HTML) |

## Corpus / ingestion (documented expectations)

| Case | Expected at query time |
|------|-------------------------|
| Empty or unreadable uploaded file | May yield no citations → ungrounded refusal |
| CSV / mixed formats in S3 | Bedrock indexes supported types; citations show basename from S3 URI regardless of corpus |
| Stale KB (sync not run) | Answers may miss new docs until data source sync completes |

## Document upload (S3 + optional KB sync)

| Case | Server | UI |
|------|--------|-----|
| No file selected | `400` · `missing_file` | Client alert + server error card |
| Unsupported extension (e.g. `.exe`) | `400` · `unsupported_type` | Client block + server error card |
| Empty file (0 bytes) | `400` · `empty_file` | Client alert before submit |
| File larger than `MAX_UPLOAD_BYTES` | `400` · `file_too_large` | Client alert (5 MB default) |
| `S3_BUCKET` not configured | `400` · `upload_disabled` | Error card — upload disabled in env |
| S3 `AccessDenied` / network | `502` · mapped boto3 code | Error card with IAM hint |
| Upload OK, sync unchecked | `200` | Success card — S3 URI + manual sync note |
| Upload OK + **Sync to KB** checked | `200` | Success card — ingestion job id when configured |
| Sync requested but no `BEDROCK_DATA_SOURCE_ID` | `502` · `kb_sync_not_configured` | File saved; sync instructions in message |
| S3 OK, ingestion job fails | `202` · `partial` + `sync_warning` | File in S3; user sees actionable warning |

Allowed types: `.md`, `.txt`, `.csv`, `.docx`, `.pdf` — aligned with Bedrock S3 connector support.

## API codes (upload)

- `missing_file`, `unsupported_type`, `empty_file`, `file_too_large`, `upload_disabled`
- `kb_sync_not_configured`, `kb_sync_failed` (HTTP 502)

## API codes (validation)

- `empty_question`
- `short_question`
- `oversize_question`
- `stopwords_only`

Bedrock failures use typed codes from `app/errors.py` (e.g. throttling, access denied) with HTTP `502`.
