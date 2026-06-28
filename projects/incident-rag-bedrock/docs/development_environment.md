# Development Environment — Cursor vs External Tools

Cursor is the **primary dev environment** for this project, but not the **only** place you configure it. The assignment chain is:

`documents → Bedrock KB → Flask (boto3) → Docker → EC2 → public URL → cleanup`

## Configure from Cursor

| Task | Location | Command / action |
|------|----------|------------------|
| Edit Flask app, templates, CSS | `app/` | Editor |
| Environment variables | `.env` (from `.env.example`) | Copy and edit in Cursor |
| Unit tests | `tests/` | `pytest` |
| Upload corpus to S3 | `infra/upload_docs_to_s3.sh` | `BUCKET=... aws s3 sync ...` (or PowerShell equivalent) |
| Local container | `docker-compose.yml` | `docker compose up --build` |
| Push image | `Dockerfile` | `docker build` / `docker push` |
| EC2 file transfer | `docs/ec2_deployment.md` | `scp` / `ssh` from integrated terminal |

Recommended Cursor extensions (optional): configure a local `.vscode/extensions.json` (gitignored).

## Requires tools outside Cursor

| Task | Where |
|------|--------|
| Enable Bedrock model access | AWS Console → Bedrock → Model access |
| Create / sync Knowledge Base | AWS Console (or AWS CLI for advanced users) |
| Test KB before Flask | AWS Console → Test knowledge base |
| Create IAM role for EC2 | AWS Console → IAM (or CLI) |
| Launch EC2 instance | AWS Console → EC2 |
| Submission screenshots | Browser + AWS Console |
| Teardown | AWS Console per [`cleanup_checklist.md`](cleanup_checklist.md) |

## Prerequisites (install once on your machine)

- **Python 3.12+**
- **Docker Desktop** (Linux containers on Windows)
- **AWS CLI v2** with `aws configure` or `AWS_PROFILE`
- **SSH client** (Windows OpenSSH) for EC2 `scp` / `ssh`

Verify:

```powershell
python --version
docker --version
aws --version
aws sts get-caller-identity
```

## Recommended workflow

1. **Cursor** — clone repo, copy `.env.example` → `.env`, run `pytest`.
2. **AWS Console** — S3 bucket, model access, create KB, sync; copy `BEDROCK_KB_ID` and model ARN into `.env`.
3. **Cursor terminal** — upload docs, `docker compose up --build`, open `http://localhost:8080`.
4. **AWS Console** — IAM role, launch EC2 with instance profile.
5. **Cursor terminal** — `docker push`, `scp .env`, verify with `ssh ... docker ps`.
6. **Browser** — public URL and screenshots.
7. **AWS Console** — delete all resources per cleanup checklist.

## Bottom line

| Layer | Cursor-only? |
|-------|----------------|
| Python / Flask / tests / Dockerfile | Yes |
| `.env` and local run | Yes (integrated terminal) |
| Bedrock KB + EC2 + IAM | No — AWS Console required (CLI optional) |
| Docker runtime | No — Docker Desktop required |
| Submission proof | No — browser + Console screenshots |
