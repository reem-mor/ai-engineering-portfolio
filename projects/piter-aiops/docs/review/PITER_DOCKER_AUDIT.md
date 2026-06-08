# PITER Docker Audit

## Files

| File | Assessment |
|------|------------|
| `Dockerfile` | Multi-stage build, gunicorn on 8080 |
| `docker-compose.yml` | **PASS** branding: `piter-aiops:dev`, container `piter-aiops` |
| `.dockerignore` | Present — verify excludes `.env`, tests, frontend node_modules |

## Compose configuration

- Port `8080:8080`
- Optional `.env` for Bedrock mode
- Mounts `~/.aws:ro` for credentials
- `USE_BEDROCK` from `PITER_USE_BEDROCK`

## This audit session

| Check | Result |
|-------|--------|
| `docker compose config` | Valid YAML rendered |
| `docker compose ps` | **FAILED** — Docker Desktop not running on host |
| `http://localhost:8080/health` | Not tested (no container) |

## Legacy names

- `infra/ec2_user_data.sh` references `incident-rag` container name — EC2 path legacy
- No `incidentiq` image name in current compose

## Recommended pre-demo commands

```bash
docker compose build
docker compose up -d
curl http://localhost:8080/health
py -3.12 scripts/verify_live_demo.py
```

## Cleanup candidates

Old local images named `incident-rag-bedrock` — propose prune after confirming unused (`docker images`).
