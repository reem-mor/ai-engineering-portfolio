# Lecture 07 — Docker & AWS Deployment

**Slides:** [`resources/lecture06_docker_aws.pdf`](../../resources/lecture06_docker_aws.pdf)

---

## Topics Covered

- Docker concepts: image, container, layer, registry
- Writing a `Dockerfile` for a Python/Flask app
- Core Docker commands: `build`, `run`, `ps`, `stop`, `exec`, `logs`
- `docker-compose` for multi-container setups
- Environment variables in containers: `-e` flag vs `.env` file
- AWS fundamentals: EC2, S3, Elastic Beanstalk (EB)
- Deploying a containerised Flask app to AWS EB
- Health check endpoints and their role in AWS/ECS
- IAM basics: least-privilege access for deployment

---

## Key Concepts You Must Know

### Docker Fundamentals

| Term | Meaning |
|------|---------|
| **Image** | Read-only blueprint (built from a `Dockerfile`) |
| **Container** | Running instance of an image |
| **Layer** | One instruction in the `Dockerfile` — cached for fast rebuilds |
| **Registry** | Storage for images — Docker Hub, AWS ECR, GitHub Packages |

```
Dockerfile  →  docker build  →  Image  →  docker run  →  Container
```

### Minimal Flask Dockerfile

```dockerfile
FROM python:3.12-slim

WORKDIR /app

# Copy dependencies first — layer cache reuse on code-only changes
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["python", "app.py"]
```

Key practices:
- Use slim/alpine base images to reduce attack surface and image size.
- Copy `requirements.txt` and install **before** copying application code — this caches the pip install layer.
- Never bake secrets into the image. Pass them as environment variables at runtime.

### Essential Docker Commands

```bash
# Build
docker build -t my-rag-app .

# Run (detached, port mapping, env var)
docker run -d -p 5000:5000 \
  -e GEMINI_API_KEY=your-key \
  -e HF_TOKEN=your-token \
  --name rag-app \
  my-rag-app

# Inspect
docker ps                         # list running containers
docker logs rag-app               # view stdout/stderr
docker exec -it rag-app bash      # open a shell inside the container

# Stop / remove
docker stop rag-app
docker rm rag-app
```

### docker-compose

Useful when your app needs multiple services (e.g. app + database + cache).

```yaml
# docker-compose.yml
services:
  web:
    build: .
    ports:
      - "5000:5000"
    environment:
      - GEMINI_API_KEY=${GEMINI_API_KEY}
      - HF_TOKEN=${HF_TOKEN}
    volumes:
      - ./data:/app/data       # persist uploaded documents
    restart: unless-stopped
```

```bash
docker compose up -d      # start in background
docker compose down       # stop and remove containers
docker compose logs -f    # tail logs
```

### AWS Core Services

| Service | Use in this course |
|---------|--------------------|
| **EC2** | Virtual machine — full control, manual deployment |
| **S3** | Object storage — store models, datasets, static files |
| **Elastic Beanstalk** | PaaS — deploy a ZIP or Docker container, AWS manages load balancer + auto-scaling |
| **ECR** | Private Docker registry — store your images for ECS/EB |
| **IAM** | Identity & Access Management — create deployment roles with least privilege |

### Deploying to Elastic Beanstalk (Docker platform)

```bash
# 1. Install EB CLI
pip install awsebcli

# 2. Initialise EB application
eb init -p docker my-rag-app

# 3. Create environment and deploy
eb create rag-prod --envvars GEMINI_API_KEY=...,HF_TOKEN=...

# 4. Subsequent deploys
eb deploy

# 5. Open in browser
eb open
```

### Health Check Endpoint

AWS EB / ECS expects a health check URL (default `GET /`) that returns `200 OK`.
Add a dedicated endpoint to avoid false alarms:

```python
@app.route("/health")
def health():
    return {"status": "ok", "engine_ready": engine.ready}, 200
```

### Environment Variables in Production

Never store secrets in source code or Docker images:
1. Use AWS Parameter Store or Secrets Manager for sensitive values.
2. For EB: set via `eb setenv` or the EB console.
3. For local Docker: use a `.env` file with `docker run --env-file .env`.

---

## Exercises

### Exercise 1 — Dockerise the RAG App
Write a `Dockerfile` for `lectures/06_flask_advanced_rag/`.
- Base image: `python:3.12-slim`
- Install from `requirements.txt`
- Expose port 5000
- Pass `GEMINI_API_KEY` and `HF_TOKEN` via `-e` at runtime (not baked in)

```bash
docker build -t rag-app .
docker run -p 5000:5000 -e GEMINI_API_KEY=... -e HF_TOKEN=... rag-app
```

### Exercise 2 — docker-compose with Volume
Add a `docker-compose.yml` that:
- Mounts `./data` from the host into `/app/data` inside the container
- Reads `.env` for secrets (`env_file: .env`)
- Restarts the container automatically on crash

### Exercise 3 — Health Check Route
Add `GET /health` to the RAG Flask app that returns:
```json
{"status": "ok", "engine_ready": true, "chunks": 42}
```
Return `503` if the engine is not yet ready.

### Exercise 4 — Multi-Stage Build
Rewrite the Dockerfile using a multi-stage build to reduce the final image size:
- Stage 1 (`builder`): install all dependencies including build tools
- Stage 2 (`runtime`): copy only the installed packages and app code

---

## Common Pitfalls

| Mistake | Fix |
|---------|-----|
| `COPY . .` before `pip install` | Reinstalls deps on every code change — put pip install first |
| Port not accessible | Check `EXPOSE` in Dockerfile AND `-p host:container` in `docker run` |
| Secrets baked into image | Use `--env-file` or `-e` at runtime; never `ENV SECRET=...` in Dockerfile |
| Container exits immediately | Check `docker logs <name>` — often an uncaught exception at startup |
| `PermissionError` on volume mount | The app user inside the container may lack write access — use `chmod` or run as root for development |
