# PITER AiOps — Final Demo Runbook & Recording Script

**Prepared:** 2026-06-08  
**Approved baseline:** AWS readiness audit (read-only)  
**Stable demo path:** `RAG_BACKEND=retrieve_and_generate`  
**Do not before demo:** rename `iiq-*`, disable `incidentiq-ops`, deploy `piter-escalation`, send SNS/SES

---

## Part 1 — Pre-demo runbook (reliable path)

### 1.1 Confirm environment

Ensure project `.env` keeps the stable settings (do not change for the main recording):

```ini
PITER_USE_BEDROCK=true
RAG_BACKEND=retrieve_and_generate
PITER_BEDROCK_KB_ID=RBTJM6NIG9
AWS_PROFILE=reemmor
PITER_AWS_REGION=us-east-1
```

Agent IDs may remain set; they are unused while `RAG_BACKEND=retrieve_and_generate`.

### 1.2 Commands — reliable demo path

Run from repo root:

```powershell
cd C:\dev\amdocs-ai-course\projects\piter-aiops

# Preflight (optional but recommended)
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe scripts\verify_live_demo.py

# Start Docker (loads .env → live Bedrock + retrieve_and_generate)
docker compose up --build -d

# Health
Invoke-WebRequest -UseBasicParsing http://localhost:8080/health
# Expected: {"status":"ok"}

# Console
start http://localhost:8080/console
```

**Warm-up:** Run one triage before recording (first Bedrock call can be slower).

**Do not restart** the container between triage and follow-up — session memory is in-process.

### 1.3 Primary demo scenario (console)

| Step | Action |
|------|--------|
| 1 | Open **http://localhost:8080/console** |
| 2 | Click **Load demo alert** (or enter manually) |
| 3 | Click **Run triage** |
| 4 | Confirm badge **`mode: bedrock`** |
| 5 | Scroll citations, tools, owner, impact, similar incidents |
| 6 | Follow-up: **Who do I escalate this to?** |
| 7 | Confirm **memory_used** / owner-style answer without re-running full triage |

**Demo alert values** (matches `verify_live_demo.py`):

| Field | Value |
|-------|-------|
| Service | `postgres` |
| Environment | `NJ-DGE` |
| Severity | `P2` |
| Alert time | `2026-06-10T09:00:00Z` |
| Symptom | `PostgreSQL CPU above 90%` / `prod-db-1 CPU reached 95%` |

**Expected highlights:**

- Citations include **`runbook_db_cpu.md`** (or related postgres CPU runbook)
- **Recommended steps** (numbered, from runbook)
- **Suspect deploy** from correlate tool
- **Owner / escalation** (e.g. `dba-oncall`, platform-dba)
- **Business impact** with SLA/regulatory risk
- **Similar incidents** with MTTR

### 1.4 Optional — Alert Storm (extended demo)

If showing the full workflow UI:

```powershell
start http://localhost:8080/?section=storm
```

Flow: **Start Alert Storm → Run PITER Analysis → follow-up chat → (preview escalation, no send) → Mark resolved**

### 1.5 Fallback (if Bedrock hiccups during recording)

The app auto-falls back to **local TF-IDF** on Bedrock errors. Badge shows **`mode: local`**. Full card still renders.

Forced offline rehearsal (no AWS):

```powershell
$env:PITER_USE_BEDROCK="false"
docker compose up --build -d
```

Revert `.env` / env vars before live recording.

### 1.6 Optional — Agent orchestration proof (do not use as default)

**Purpose:** Show teacher-aligned `invoke_agent` path without changing the stable Docker demo.

**Recommended (venv, no Docker restart):**

```powershell
cd C:\dev\amdocs-ai-course\projects\piter-aiops
$env:AWS_PROFILE='reemmor'
$env:RAG_BACKEND='agent'
.\.venv\Scripts\python.exe scripts\agent_smoke_test.py
```

Expected: score printed (e.g. `7/7 passed`), results in `evaluation/agent_smoke_results.md`.

**Alternative (same client, single P1 prompt):**

```powershell
$env:AWS_PROFILE='reemmor'
$env:RAG_BACKEND='agent'
.\.venv\Scripts\python.exe -c "
from app.config import Config
from app.bedrock_agent_client import BedrockAgentClient
cfg = Config.from_env()
r = BedrockAgentClient(cfg).ask(
    'P1: bet-service 100%% error rate in GIB-UKGC. Return Priority, Investigation, Triage, Escalation, Resolution, Sources, Confidence.',
    session_id='demo-agent-proof')
print('grounded=', r.grounded, 'citations=', len(r.citations))
print(r.answer[:1500])
"
```

**If you must show agent in the UI:** temporarily set `RAG_BACKEND=agent` in `.env`, `docker compose up -d --force-recreate`, record segment, then **revert to `retrieve_and_generate`** and recreate container. Do not commit the change.

**Talking point:** Direct KB path = deterministic citations for demo; Agent path = managed orchestration over the same KB + action groups (verified in audit, ~27s for P1 scenario).

---

## Part 2 — What to show (UI map)

### 2.1 Citations

**Show:** Expand **Citations** / source list on the triage card.

**Say:** “Every remediation claim is tied to retrieved documents — here is the Postgres CPU runbook chunk from our S3-backed Knowledge Base.”

**Point at:** `document` / label (e.g. `runbook_db_cpu.md`), snippet text, **`grounded: true`**.

### 2.2 Tools / enrichment

**Show:** Deploy correlation, owner/escalation block, business impact, similar incidents.

**Say:** “RAG gives the runbook narrative; four enrichment tools add operational context — recent deploys, service owner and escalation path, dollar impact, and similar past incidents. These run deterministically alongside Bedrock.”

**Map for audience:**

| UI block | Tool / source |
|----------|----------------|
| Suspect deploys | correlate deployments |
| Owner / escalation | service context |
| Business impact | impact scoring |
| Similar incidents | similar-incidents lookup |

### 2.3 Memory follow-up

**Show:** Same session — type **Who do I escalate this to?** in follow-up.

**Say:** “Follow-up uses the same `session_id` — owner, deploy, and triage context are reused without a second full enrichment pass.”

**Confirm:** Response references **dba-oncall** / escalation chain; UI indicates memory use where applicable.

---

## Part 3 — Architecture talking points (60–90 seconds)

### 3.1 Agent + Knowledge Base association

**Implemented today:**

- Bedrock **Knowledge Base** `RBTJM6NIG9` is **ACTIVE**; S3 corpus under `projects/piter-aiops/data/sample_documents/`.
- The **Bedrock Agent** (`incidentiq-triage-agent` in console) is **PREPARED** and has KB `RBTJM6NIG9` **ENABLED** on agent version 3.
- **Demo runtime** uses **`retrieve_and_generate`** — Flask calls Bedrock KB API directly for stable, cited answers.

**Exact wording:**

> “The Knowledge Base is the evidence layer — runbooks and policies in S3, embedded with Titan, retrieved at question time. The Bedrock Agent is the orchestration layer — same KB, plus Lambda action groups for deploy correlation, ownership, and incident history. For this demo I use direct KB retrieval because it gives the most reliable citations; the Agent path is configured and verified on the same KB and tools.”

### 3.2 Why `iiq-*` names (legacy deployed names)

**Implemented today:**

- AWS Lambda/action groups use **`iiq-correlate`**, **`iiq-context`**, **`iiq-similar`** plus legacy **`incidentiq-ops`**.
- Local repo also has **`piter-*`** folders mirroring the same operations for Flask/MCP and future rename.

**Exact wording:**

> “Console names still say `iiq-*` from an earlier project iteration. Functionally they map to PITER tools: correlate recent deployments, resolve service context and escalation, find similar incidents, and legacy ops status for environment alerts. Renaming in AWS is a post-demo alignment step — behavior is what matters for triage.”

| AWS name | PITER tool |
|----------|------------|
| `iiq-correlate` | piter-recent-deployments |
| `iiq-context` | piter-service-context |
| `iiq-similar` | piter-similar-incidents |
| `incidentiq-ops` | legacy ops (status/alerts/incident create) |

### 3.3 `piter-escalation` — local / future

**Implemented today:**

- Escalation **preview and gates** in the app (confirmation token, allowlist, max sends).
- **`piter-escalation` Lambda** exists in repo; **not deployed** to AWS; **not** on the Agent.

**Exact wording:**

> “Escalation notification logic is implemented locally with safety gates — mock by default in the template, live SNS/SES only with explicit confirmation. The fourth action group, `piter-escalation`, is coded and tested but intentionally not deployed before this demo; that is the next AWS alignment step after approval.”

### 3.4 Guardrail — exists, not attached to Agent

**Implemented today:**

- **App guardrails** (`app/guardrails.py`) block destructive operator prompts before Bedrock.
- Account **Bedrock Guardrail** `incidentiq-demo-guardrail` exists (READY); **not attached** to the Agent; `PITER_GUARDRAIL_*` unset.

**Exact wording:**

> “We enforce safety in two layers. Application guardrails block dangerous remediation requests before they reach the model. A Bedrock Guardrail is also defined in the account for credential and destructive-action topics — attaching it to the Agent is the next infrastructure step, not required for today’s citation-first demo.”

---

## Part 4 — Implemented vs next step (cheat sheet)

| Capability | Status | Demo behavior |
|------------|--------|---------------|
| PITER workflow (Priority → Resolution) | **Implemented** | Shown in triage card + agent instruction |
| KB RAG with citations | **Implemented** | `retrieve_and_generate`, `mode: bedrock` |
| Four enrichment tools (deploy/owner/impact/similar) | **Implemented** | Visible on triage card |
| Session memory / follow-up | **Implemented** | Same-session owner question |
| Local fallback | **Implemented** | Auto on Bedrock failure; Phase B in verify script |
| Bedrock Agent + alias PREPARED | **Implemented** | Explain architecture; optional `agent` smoke |
| `invoke_agent` production path | **Verified, not default** | Optional script segment only |
| AWS names `iiq-*` / `incidentiq-*` | **Legacy labels** | Explain mapping; no rename before demo |
| `piter-escalation` on AWS | **Next step** | Local code + tests only |
| Bedrock Guardrail on Agent | **Next step** | App guardrails active today |
| SNS/SES live send | **Configured, gated** | **Do not send** during demo; preview only |
| EC2 public host | **Not used** | Docker `:8080` + live Bedrock |
| Rename to `piter-*` in AWS | **Next step** | Post-demo |

---

## Part 5 — Recording script (timed)

Adjust pace to your slot. **[ACTION]** = do on screen. **[SAY]** = narration.

### Segment A — Open (0:00–0:45)

**[ACTION]** Browser → `http://localhost:8080/console`. Quick show `/health` if needed.

**[SAY]** “This is **PITER AiOps** — Priority, Investigation, Triage, Escalation, Resolution — an SRE assistant for regulated betting platforms. It grounds answers in a Bedrock Knowledge Base and enriches incidents with deployment, ownership, impact, and history tools.”

### Segment B — Load alert & triage (0:45–2:30)

**[ACTION]** Load demo alert → **Run triage**. Wait for card. Point to **`mode: bedrock`**.

**[SAY]** “I’m triaging a P2 Postgres CPU alert in NJ-DGE. The badge shows **bedrock** — the answer is retrieved live from our Knowledge Base, not hallucinated. PITER classifies priority, investigation findings, triage steps, escalation, and resolution — all citation-backed.”

**[ACTION]** Expand **citations** → highlight `runbook_db_cpu.md`.

**[SAY]** “Here are the sources — the Postgres CPU runbook chunk Bedrock retrieved. If evidence were missing, the system would say ‘not in knowledge base’ rather than invent steps.”

### Segment C — Enrichment (2:30–3:45)

**[ACTION]** Scroll deploy correlation, owner, business impact, similar incidents.

**[SAY]** “Beyond RAG, four tools enrich the card: suspect deploy correlation, owner and escalation path, business impact estimate, and similar incidents with MTTR. In AWS these run as Lambda action groups behind the Bedrock Agent; in this demo path the same enrichment runs in the Flask layer alongside direct KB retrieval.”

### Segment D — Memory follow-up (3:45–4:30)

**[ACTION]** Follow-up box → **Who do I escalate this to?**

**[SAY]** “Same session — no re-triage. Follow-up pulls owner and escalation from session memory, so the operator gets a connected answer in seconds.”

### Segment E — Resilience (4:30–5:15)

**[SAY]** “If Bedrock were unavailable, the app falls back to a local runbook index — same card shape, same tools, same memory. Our verify script runs live AWS and simulated outage; both pass twenty-nine checks.”

### Segment F — Architecture (5:15–6:45) — optional but recommended for graders

**[SAY]** “Architecture in one minute: documents live in S3, sync into Knowledge Base **RBTJM6NIG9**. The Bedrock Agent shares that KB and calls **`iiq-*` Lambdas** — legacy names that map to PITER tools for deployments, context, and similar incidents. **`incidentiq-ops`** is a legacy ops group still enabled; we leave it for compatibility until post-demo cleanup.”

**[SAY]** “**Implemented:** KB RAG, enrichment, session memory, local fallback, agent prepared on the same KB. **Next step:** deploy **`piter-escalation`** to AWS, attach the Bedrock Guardrail to the Agent, and rename action groups to **`piter-*`** — after explicit approval, not for this recording.”

### Segment G — Agent proof (6:45–7:30) — optional clip

**[ACTION]** Terminal → run:

```powershell
$env:RAG_BACKEND='agent'
.\.venv\Scripts\python.exe scripts\agent_smoke_test.py
```

**[SAY]** “For submission alignment we also verified **`invoke_agent`** — the Agent orchestrates the same KB and tools. Demo default stays **`retrieve_and_generate`** for citation reliability; the Agent path is proven separately.”

### Segment H — Close (7:30–8:00)

**[SAY]** “PITER turns alerts into grounded, actionable triage with citations, enrichment, memory, and safe escalation gates — production-minded, with clear next steps for guardrails and AWS naming alignment. Questions welcome.”

---

## Part 6 — Pre-recording checklist

- [ ] `.env` has `RAG_BACKEND=retrieve_and_generate`
- [ ] `docker compose ps` → **healthy**
- [ ] `verify_live_demo.py` → **29/29** (optional)
- [ ] One warm-up triage completed
- [ ] Browser zoom readable (1280×720 or 1920×1080)
- [ ] Notifications: **do not** click live send; escalation preview only
- [ ] Close unrelated apps; `AWS_PROFILE` creds valid
- [ ] Do **not** restart container mid-take

---

## Part 7 — Troubleshooting (during recording)

| Symptom | Fix |
|---------|-----|
| `mode: local` unexpectedly | Check AWS creds in `~/.aws`; Bedrock throttling — acceptable, explain fallback |
| Empty citations | Confirm `PITER_USE_BEDROCK=true` and KB id; re-run warm-up |
| Follow-up generic | Same session? Did container restart? |
| Docker not up | `docker compose up -d` |
| Slow first response | Normal; pre-warm triage |

---

*No AWS mutations, commits, or pushes in this document. Stable demo path per approved readiness report (Decision B).*
