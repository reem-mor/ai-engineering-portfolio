# Deployment validation — 2026-05-31

Automated checks after S3/KB alignment and EC2 relaunch.

## Local (Docker)

| Check | Result |
|-------|--------|
| `py -3.12 -m pytest` | 89 passed |
| `http://localhost:8080/health` | `{"status":"ok"}` |
| `py -3.12 scripts/kb_smoke_test.py` | 6/6 PASS |
| `py -3.12 scripts/verify_e2e.py` | 22/22 PASS |

## Bedrock KB

| Item | Value |
|------|--------|
| Knowledge base ID | `RBTJM6NIG9` |
| Data source ID | `YICXAB6WOG` |
| S3 prefix | `s3://reem-amdocs-ai-artifacts-3331/projects/incident-rag-bedrock/data/sample_documents/` |
| Last ingestion | `PESWBFWL1V` — 10 indexed, 0 failed |

## Public EC2 (teardown complete)

| Item | Value |
|------|--------|
| Instance | `i-03d3c5a59e849e5cf` (`incident-rag-demo`) — **terminated** |
| Public URL | http://ec2-100-53-32-194.compute-1.amazonaws.com/ |
| `/health` | HTTP 200 during demo |
| Grounded `/ask` | Verified via Playwright on public URL |

## Screenshots

**Tier 1 (submit):** 11 files at `screenshots/` root (`01`–`10` + `08b`). **Tier 2:** `11`–`19`. **Extras:** `extras/partA_*`. **Archive:** `archive/` (not for submission).

Regenerate:

```powershell
cd scripts
node capture_aws_proof.mjs      # 01–03
node capture_ec2_proof.mjs      # 04–06 (while instance running)
node capture_public_app.mjs     # 07 (if public URL), 08, 08b
node capture_screenshots.mjs    # 11–19; --mvp-only for 13
node capture_partA.mjs          # extras/partA_*
node capture_cleanup_proof.mjs  # 10 (after terminate)
```

## Cleanup performed

See [`docs/cleanup_log.md`](../docs/cleanup_log.md).
