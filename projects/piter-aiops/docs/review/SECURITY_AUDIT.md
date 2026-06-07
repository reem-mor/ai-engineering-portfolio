# PITER AiOps — Security Audit

Read-only audit · 2026-06-06 · No secrets reproduced.

## Summary

| Area | Status | Notes |
|------|--------|-------|
| `.env` gitignored | **Pass** | `.gitignore` L1 |
| AWS keys in repo | **Pass** | No AKIA patterns in tracked source |
| Credentials in docs | **Pass** | IDs/regions in eval docs — no raw keys |
| Docker image secrets | **Pass** | `.dockerignore` excludes `.env` |
| Local `.aws` mount | **By design** | `docker-compose.yml` read-only mount for Bedrock dev |
| `.ec2_instance_id.txt` | **Risk** | Listed in `.gitignore`; delete if tracked |
| Debug mode | **OK** | `FLASK_ENV=development` in local `.env` — use production for public EC2 |
| CSRF | **Partial** | CSRF on forms; API routes exempt (`csrf.exempt(main_bp)`) — acceptable for JSON demo API |
| CORS | **Dev-only** | Restricted to `FRONTEND_DEV_ORIGIN` when `FLASK_ENV=development` |
| Upload validation | **Pass** | `upload_validators`, `MAX_UPLOAD_BYTES` |
| Path traversal uploads | **Mitigated** | Service-layer validation (see upload tests) |
| Prompt injection | **Partial** | KB-only instructions; no input sanitization beyond length/stopwords |
| PII in datasets | **Low** | Synthetic fictional corpus per README |
| IAM least privilege | **Documented** | `docs/bedrock_action_group_setup.md`, infra JSON templates |
| Lambda resource policies | **Documented** | Setup scripts grant Bedrock invoke |
| Dependency scan | **Not run** | Minimal deps: Flask, boto3, pandas, pytest |
| `lambda-out.json` | **Info leak risk** | Contains API response shape — delete candidate |

## `.gitignore` gaps

Recommend adding (after approval):

```
lambda-out.json
evaluation/pytest_output.txt
.ec2_instance_id.txt
.sg_id.txt
```

## `.dockerignore`

Present and reasonable. Excludes `tests/`, `docs/`, `.env`. **Note:** excluding all `*.md` except `knowledge_base/**` — OK for image size.

## docker compose secret exposure

`docker compose config` merges `.env` into printed config locally. **Do not** commit compose debug output. For shared demos, use `.env.example` only in docs.

## Logging

Bedrock errors logged with exception traces; user-facing errors sanitized via `BedrockError.user_message`.

## Recommendations

| Priority | Action |
|----------|--------|
| P0 | Ensure `.env` never committed (verify before any checkpoint commit) |
| P1 | Remove `lambda-out.json` from tree after approval |
| P2 | Add security headers for production EC2 (reverse proxy or Flask-Talisman) — optional |
| P2 | Document that `/api/*` is unauthenticated demo API |
