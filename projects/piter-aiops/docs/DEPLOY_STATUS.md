# Deploy status (prompt #3)

Captured **2026-06-03** after local verification and EC2 launch.

## Public demo

| Item | Value |
|------|--------|
| URL | http://54.167.30.47:8080/ |
| Instance | `i-016d77ef747791213` |
| Security group | `sg-0634549d8173ed78d` |
| Region | `us-east-1` |
| Tags | `Project=piter-aiops`, `Owner=reemmor` |
| Image | `329597159579.dkr.ecr.us-east-1.amazonaws.com/incident-rag-bedrock:demo` (digest `d9609f805532…`) |

Health: `GET /health` → `{"status":"ok"}`

## Screenshots

All twelve agent-era files are under [`screenshots/`](../screenshots/):

- `01_agent.png` … `06_ec2.png` — AWS CLI proof renders
- `07_app_home.png` … `10_mobile.png` — Playwright against **local** Docker (`127.0.0.1:8080`) with live Bedrock agent triage
- `11_docker_ps.png`, `12_tests.png` — terminal proof renders

To refresh app shots against the public URL:

```powershell
$env:APP_URL = "http://54.167.30.47:8080"
node scripts/capture_agent_submission.mjs
```

## Scripts added

- `scripts/capture_agent_submission.mjs` — 01–05, 07–10
- `scripts/capture_terminal_proof.mjs` — 11–12
- `scripts/capture_ec2_submission.mjs` — 06
- `scripts/launch_ec2_demo.ps1` — launch helper

## Teardown

Do **not** terminate until submission is graded. When ready, see [`TEARDOWN.md`](TEARDOWN.md) and [`cleanup_checklist.md`](cleanup_checklist.md).

```powershell
aws ec2 terminate-instances --instance-ids i-016d77ef747791213 --profile reemmor --region us-east-1
```
