# PITER AiOps — Live Demo Checklist & Readiness Report

> Last verified: **2026-06-08** · Region `us-east-1`
> Surface: local Docker container on `:8080`, **live Bedrock Agent** RAG via `.env`.

---

## 1. What you open

| Item | Value |
|------|-------|
| **Demo URL** | **http://localhost:8080/** |
| Health check | `http://localhost:8080/api/health` |
| Backing intelligence | Bedrock Agent + KB `RBTJM6NIG9` through `boto3 invoke_agent` |
| App-layer tools | 4 PITER tools: deployments, service context, similar incidents, escalation |

The React dashboard at `/` is the primary live-demo surface. The legacy `/console`
route remains available as a backup. Both surfaces expose whether the answer came
from Bedrock or local fallback.

---

## 2. Exact alert input

Click **“Load demo alert”** (fills the exact values below), then **“Run triage.”**

| Field | Value |
|-------|-------|
| Service | `postgres` |
| Environment | `NJ-DGE` |
| Severity | `P2` |
| Alert time (ISO-8601) | `2026-06-10T09:00:00Z` |
| Symptom / description | `Postgres CPU is 95% on prod-db-1` |

---

## 3. Expected triage output (live = `mode: bedrock`)

A single triage card containing:

- **Cited answer** — grounded summary + numbered recommended steps + escalation +
  “why this answer,” pinned to the Postgres CPU runbook.
- **Citations** — `runbook_db_cpu.md` and `postmortem_2024_07.md` (live KB) /
  `RB-007-postgres-cpu-high.md` (local fallback).
- **Recommended steps** — 8 steps (connect to bastion → identify long-running
  queries → cancel → reindex → failover to Patroni replica → escalate).
- **Likely cause / suspect deploy** — `DEP-2026-0610-01 — postgres 14.2.1-pg`.
- **Owner & escalation** — team `platform-dba`, on-call `dba-oncall`,
  `#inc-platform-db`, chain `platform-dba → dba-oncall → vp-engineering`.
- **Business impact** — `~$30,000 / 15 min`, est. total `$120,000`,
  SLA risk `high`, regulatory `high`.
- **Similar incidents** — `INC-2026-NJ-001` (38m MTTR), `INC-2026-NJ-002` (29m MTTR).

Verified screenshots: [`screenshots/final/`](../screenshots/final/).

---

## 4. Exact follow-up question + expected answer

In the **Follow-up** box (same card, same session) type:

> **who do I escalate to?**

Expected answer (served **from session memory**, marked “from memory · owner”):

> Escalate to **dba-oncall** (team platform-dba, Slack #inc-platform-db).
> Escalation chain: platform-dba → dba-oncall → vp-engineering. Secondary: vp-engineering.

Alternative follow-ups that also hit memory: `what deploy caused this?`,
`business impact?`.

---

## 5. Commands to run before class

```powershell
cd C:\dev\amdocs-ai-course\projects\piter-aiops

# 1. Build + start the container (loads .env → USE_BEDROCK=true, live Bedrock)
docker compose up -d

# 2. Confirm it's healthy and serving the console
curl.exe -s -o NUL -w "%{http_code}`n" http://localhost:8080/api/health   # 200

# 3. (Optional) re-run the guarantees
.\.venv\Scripts\python.exe -m pytest -q                                 # 279 passed
.\.venv\Scripts\python.exe scripts\verify_live_demo.py                  # 29/29 PASS

# 4. Open the demo
start http://localhost:8080/
```

Do **not** restart the container between “Run triage” and the follow-up — session
memory is in-process (single gunicorn worker by design).

---

## 6. Fallback plan (if AWS is unavailable)

The demo cannot fail because of AWS:

- The app auto-falls back to **local TF-IDF RAG** on any Bedrock error
  (bad creds, throttling, model access). The card still renders fully grounded
  with citations from the local runbooks; the 4 tools, owner, impact, similar
  incidents, and follow-up memory are identical.
- To force the never-fail offline rehearsal mode, set `USE_BEDROCK=false`:

  ```powershell
  $env:USE_BEDROCK="false"; docker compose up --build -d
  ```

  The badge will read `mode: local`. Everything else looks the same to the class.
- This was verified end-to-end: `verify_live_demo.py` Phase B simulates an
  AWS outage (bad KB id) and still passes all checks.

---

## 7. Honest readiness report

### Passed (verified `2026-06-08`)
- App opens, demo alert loads, submit works (`/` primary; `/console` backup).
- ✅ Live Bedrock cited RAG answer (`mode: bedrock`, KB `RBTJM6NIG9`, 7/7 KB smoke).
- ✅ All 4 MCP tools enrich the card (correlate, context/owner, similar, impact).
- ✅ Owner/escalation, business impact, similar incidents all render.
- ✅ Follow-up works in-session and is served **from memory**.
- ✅ Mobile/projector layout (390px) renders the full card.
- ✅ No browser console errors; no stack traces surfaced (JSON error bodies only).
- ✅ AWS-down auto-fallback to local mode keeps the full demo (29/29 e2e checks).
- `pytest` 279 passed.

### Needs your AWS login (only if you want the *public* AWS angle)
- ⚠️ **EC2 public host is gone.** The previously documented instance
  (`i-016d77ef747791213`, `54.167.30.47`) no longer exists. There is **no running
  EC2** under the project tag. The demo therefore runs on **local Docker**, which
  still calls **live Bedrock** — so it is genuinely “live on AWS intelligence,”
  just not a public EC2 URL. Re-launching EC2 is **not** required and was **not**
  done (no new paid infra without your approval).

### Manual config / notes
- `.env` is local-only and git-ignored; it points at the existing KB/Agent IDs and
  the enabled Claude Haiku 4.5 inference profile. Real fix applied: removed `topP`
  from the Bedrock inference config (Haiku rejects `temperature`+`topP` together).
- `RAG_BACKEND=agent` is the primary final demo mode. Direct `retrieve_and_generate`
  and local TF-IDF fallback remain available if the Agent alias or KB is unavailable.
- Firecrawl is optional and env-only; absent key is skipped cleanly.

### Safe for the live class demo
- ✅ **Yes.** Primary path = local Docker + live Bedrock. Guaranteed backup =
  `USE_BEDROCK=false` local mode. Either way the class sees a full cited triage
  card with tools, owner, impact, similar incidents, and memory-backed follow-up.

---

## 8. What to say during the presentation

1. “This is PITER AiOps — Priority, Investigation, Triage, Escalation, Resolution.”
2. “Priority Center: mixed P1–P4 alerts; I’ll pick Postgres at 95% CPU on `prod-db-1`,
   P2.” *(select alert → Run PITER workflow)*
3. “Investigation: enrichment shows deploy correlation and similar incidents.”
4. “Triage plan: grounded runbook steps with citations.”
5. “Escalation Hub: owner and on-call path for P1–P3.”
6. “Resolution Tracker: mark resolved; Agent Analytics KPIs update.”
7. *(Legacy talking point)* “I’ll load a real production-style alert…” *(if needed for backup script)*
3. “Notice the badge says **bedrock** — the cited answer is retrieved live from our
   AWS Bedrock Knowledge Base of runbooks, not made up. Here are the citations.”
4. “Beyond RAG, four tools enriched the incident through MCP-style tool-calling:
   it correlated a suspect deploy, found the owning team and on-call escalation,
   quantified business impact (~$30k / 15 min), and pulled similar past incidents
   with their MTTR.”
5. “Now a follow-up in the same session — *who do I escalate to?* — answered
   **from memory**, so it stays connected to this incident.”
6. “And it’s resilient: if Bedrock were unavailable, it auto-falls back to a local
   retriever and still produces the full card — the demo never fails.”

---

## 9. Known risks before presenting

- **Don’t restart the app** between triage and follow-up (in-process session memory).
- **Bedrock model access / throttling** — if it hiccups, the badge flips to `local`
  and the demo continues; optionally pre-set `USE_BEDROCK=false` for zero risk.
- **No public EC2 URL** — demo on `localhost:8080`; mention AWS Bedrock is the live
  brain behind it.
- **First request latency** — the very first Bedrock call can take a few seconds;
  run one triage during setup to warm it.
- **Firecrawl** — optional; missing key is skipped, no impact on the demo.
