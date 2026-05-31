# Deployment validation — 2026-05-31

Automated checks run from Cursor terminal after EC2 launch.

## Local (Docker)

| Check | Result |
|-------|--------|
| `py -3.12 -m pytest` | 43 passed |
| `http://localhost:8080/health` | `{"status":"ok"}` |
| Container health | `Up (healthy)` |
| `py -3.12 scripts/kb_smoke_test.py` | 5/5 PASS |
| Screenshots | `07`, `08`, `09`, `11`, `12` regenerated |

## Public EC2

| Item | Value |
|------|--------|
| Instance | `i-0ff0a902311a5943b` (`incident-rag-demo`) |
| Public URL | http://ec2-13-222-142-122.compute-1.amazonaws.com/ |
| `/health` | HTTP 200, `{"status":"ok"}` |
| Homepage | HTTP 200 |
| `/ask` via raw POST | 400 — CSRF token required (expected; use browser or HTMX form) |

## Bedrock KB

| Item | Value |
|------|--------|
| Knowledge base ID | `RBTJM6NIG9` |
| Ingestion job | `INLETQWUDQ` — COMPLETE (8 new, 2 modified docs) |
| S3 prefix | `s3://reem-amdocs-ai-artifacts-3331/projects/incident-assistant-rag/knowledge-base/sample-documents/` |

## Manual screenshots still needed

Capture in browser/AWS Console per assignment:

- `01_bedrock_kb_overview.png`
- `02_bedrock_kb_data_source_synced.png`
- `07_app_homepage_public.png`
- `08_app_question_and_answer.png` (submit via UI for CSRF)
- `04_ec2_instance_running.png`
- `06_docker_ps_on_ec2.png`

## Cleanup performed

See [`docs/cleanup_log.md`](../docs/cleanup_log.md) for resources removed after validation.
