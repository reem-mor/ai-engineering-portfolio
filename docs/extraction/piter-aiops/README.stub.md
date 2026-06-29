# PITER AiOps

**Agentic incident-response platform** — AWS Bedrock Agent, RAG over runbooks, session memory,
alert-storm simulation, and safe escalation. Flask + React + Docker.

Built by [Re'em Mor](https://github.com/reem-mor) — AI Engineer × SRE.

## Quick start

```powershell
py -3.12 -m pip install -r requirements-dev.txt
cd frontend && npm ci && npm run build && cd ..
docker compose up --build -d
# http://localhost:8080/
py -3.12 -m pytest -q
```

Copy `.env.example` to `.env` for Bedrock/AWS settings. Never commit `.env`.

## Documentation

- Architecture and demo flow: see `docs/` in this repo
- Live deployment: `docs/ec2_deployment.md`

## License

MIT — see `LICENSE`.
