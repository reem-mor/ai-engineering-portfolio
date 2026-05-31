# Code review — document upload + RAG stack (2026-05-31)

Self-review after adding S3 upload, KB sync option, and expanded test coverage.

## Strengths

- **Separation of concerns:** `upload_validators.py` (pure validation), `upload_service.py` (boto3 S3 + Bedrock Agent), `routes.py` (HTTP only).
- **Consistent error model:** All user-facing failures use `BedrockError` with stable `code` values; S3/boto3 mapped via `translate()` in `errors.py`.
- **Testability:** Upload routes tested with injected `_FakeUploadService`; validators covered independently; Bedrock client still uses Stubber (no live AWS in unit tests).
- **Security:** CSRF on upload form; `secure_filename` + timestamp prefix for S3 keys; allowed suffix whitelist; size cap; IAM policy scoped to single bucket prefix pattern.
- **UX:** HTMX partial for upload result; client-side pre-checks mirror server rules; optional KB sync checkbox only default-checked when `BEDROCK_DATA_SOURCE_ID` is set.

## Risks / follow-ups (acceptable for course MVP)

| Item | Severity | Notes |
|------|----------|-------|
| Partial sync failure | Low | File lands in S3 before ingestion job; user gets explicit 502 with S3 URI |
| No upload progress | Low | Fine for ≤5 MB course corpus |
| Duplicate filenames | Low | Timestamp prefix avoids overwrite |
| Local AWS creds in Docker | Info | Documented; EC2 uses instance profile |
| `11_pytest_43_passed.png` legacy name | Info | Renamed to `11_pytest_passed.png` in capture script |

## Verification performed

- `pytest`: 73 passed
- KB data source prefix: `projects/incident-rag-bedrock/data/sample_documents/`
- Edge cases documented in [`edge_cases.md`](edge_cases.md)
