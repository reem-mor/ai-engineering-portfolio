# PITER Docker Live Check

**Date:** 2026-06-08

## Compose configuration

| Setting | Value |
|---------|--------|
| Image | `piter-aiops:dev` |
| Container | `piter-aiops` |
| Port | `8080:8080` |
| Healthcheck | `GET /health` — **healthy** |
| Build | Multi-stage Dockerfile, gunicorn workers |

## Commands run

```powershell
docker compose config
docker compose build
docker compose up -d
docker compose ps
Invoke-WebRequest http://localhost:8080/health
```

## Endpoints verified

| URL | Status |
|-----|--------|
| `http://localhost:8080/health` | 200 |
| `http://localhost:8080/` | SPA (PITER AiOps dashboard) |
| `http://localhost:8080/console` | Legacy triage console (bedrock mode in capture) |

## Screenshot

`screenshots/final/15_docker_running.png`

## Rollback

```powershell
docker compose down
docker compose up -d --build   # rebuild from current tree
```
