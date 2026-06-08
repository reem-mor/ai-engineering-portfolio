# Live demo

## Baseline checks

```bash
python -m pytest
python scripts/verify_live_demo.py    # 29/29 with live .env and Bedrock Agent
python scripts/verify_spa_demo.py   # API-only parity for React SPA
```

> Offline (no AWS credentials), `verify_live_demo.py` degrades gracefully to **14/15** — Phase A
> live assertions are skipped (the one expected fail is "app configured for live Bedrock"), and
> Phase B proves the local fallback end-to-end (14/14). It no longer errors without a `.env`.

## Going live (Bedrock) - turnkey

**Final demo path:** `RAG_BACKEND=agent` (Bedrock Agent Runtime through `boto3 invoke_agent`).

The live alias `live` routes to agent **version 6** with guardrail v2, `piter-escalation`, and legacy `incidentiq-ops` disabled. Verify with:

```bash
RAG_BACKEND=agent python scripts/agent_smoke_test.py   # target 7/7
```

To exercise the real Bedrock Agent path and reach **29/29**, store AWS keys in the AWS CLI profile and set these project `.env` values:

```env
AWS_PROFILE=reemmor
PITER_AWS_REGION=us-east-1
PITER_USE_BEDROCK=true
RAG_BACKEND=agent
PITER_BEDROCK_KB_ID=...
PITER_BEDROCK_MODEL_ARN=arn:aws:bedrock:...:foundation-model/...   # or inference-profile ARN
PITER_BEDROCK_AGENT_ID=...
PITER_BEDROCK_AGENT_ALIAS_ID=...
```

Then:

```bash
aws sts get-caller-identity --profile reemmor
python scripts/verify_live_demo.py     # target 29/29 (live Bedrock + local fallback)
```

Notifications stay **mock** by default. A real escalation send additionally requires
`PITER_NOTIFICATION_MODE=live`, `PITER_ENABLE_LIVE_DISPATCH=true`, a confirmation token, an
allowlisted recipient, and an allowed severity (see `docs/notifications.md`). Never send in tests.

## Recording flow (SPA)

1. Open `http://localhost:8080/` → **Alert Storm Demo**
2. **Start alert storm** — UI shows *Simulated alert storm (399 alerts)* from `/api/alert-stream`
3. **Run PITER workflow** — `POST /api/triage` with P1 bet-service payload
4. Agent panel — follow-up via `POST /api/follow-up` (session memory)
5. Legacy console remains at `/console` until `PITER_CONSOLE_REDIRECT_SPA=true`

## Postgres scenario (verify script)

`verify_live_demo.py` uses a postgres CPU P2 scenario for Bedrock/local fallback proof.
The SPA storm demo uses the CSV P1 bet-service trigger — both share the same triage API contract.

## Docker

```bash
docker compose up -d
curl http://localhost:8080/api/health
```

## Before enabling SPA console redirect

1. `verify_spa_demo.py` passes all checks
2. Set `PITER_CONSOLE_REDIRECT_SPA=true` in `.env`
3. Re-run both verify scripts
