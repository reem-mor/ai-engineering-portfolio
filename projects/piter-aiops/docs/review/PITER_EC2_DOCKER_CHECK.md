# PITER AWS Phase 10 — EC2 and Docker Verification

**Audit date:** 2026-06-08

## EC2 (AWS read-only)

| Check | Result |
|-------|--------|
| Instances tagged `Project=piter-aiops` | **None** |
| Running instances (account) | **0** |
| EC2 required for demo | **No** — local Docker is sufficient |

**Conclusion:** Demo host is **local Docker** on `:8080`, not EC2. `infra/ec2_user_data_demo.sh` exists for optional cloud deploy but no instance is running.

## Docker — local

### docker compose config

- Service: `web` → image `piter-aiops:dev`, port `8080:8080`
- AWS creds: bind-mount `~/.aws` read-only
- `USE_BEDROCK` / `PITER_USE_BEDROCK`: true
- `RAG_BACKEND`: `retrieve_and_generate`
- Health: container **`piter-aiops` Up (healthy)**

### docker compose ps

```
NAME          IMAGE             STATUS
piter-aiops   piter-aiops:dev   Up (healthy)   0.0.0.0:8080->8080/tcp
```

### docker images

| Image | Size | Notes |
|-------|------|-------|
| `piter-aiops:dev` | 456MB | **Current** |
| `incidentiq-midproject:dev` | 459MB | **Legacy** — candidate for removal after approval |

### Health check

```powershell
Invoke-WebRequest http://localhost:8080/health
# {"status":"ok"}
```

## Cost / risk

| Resource | Risk |
|----------|------|
| EC2 | **$0** — none running |
| Docker local | Dev machine CPU/RAM only |
| Bedrock invoke | Per-token + KB retrieval (monitor during demo) |

## Cleanup proposal (approval required)

```powershell
# Do NOT run without approval
docker rmi incidentiq-midproject:dev
docker image prune -f
```

## Commands run

```powershell
aws ec2 describe-instances --filters "Name=tag:Project,Values=piter-aiops"
docker compose config
docker compose ps
docker images
Invoke-WebRequest -UseBasicParsing http://localhost:8080/health
```
