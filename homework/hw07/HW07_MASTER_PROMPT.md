# HW07 Master Prompt — CVE Intelligence Assistant (paste into a new Cursor chat)

Open this file in a **separate Cursor window** and paste the block below into Agent chat.
Repo path: `homework/hw07/` inside `ai-engineering-portfolio`.

---

## Agent instructions (copy from here)

You are completing **Homework 07** in `homework/hw07/` of the ai-engineering-portfolio repo.
Read [`AGENTS.md`](AGENTS.md) and this file first. Execute end-to-end; pause only to ask me for secrets you cannot read from `.env`.

### Homework requirements (graded)

1. **Knowledge Base** — Upload a Kaggle CVE CSV to Open WebUI; index as KB (historical questions).
2. **Local Python server** — `tools_server.py` on `http://localhost:5005` calling an external API (RapidAPI and/or Shodan CVEDB fallback).
3. **Web UI tool** — Register the tool server in Open WebUI via **OpenAPI** so the model can call it for live questions.

**Graded contrast:** KB = historical dataset questions · Tool = current-risk questions about a specific CVE.

---

### Phase 0 — Preconditions (verify before building)

```powershell
cd homework\hw07
python -m pytest tests/ -q          # expect 31 passed
python ..\..\scripts\verify-rapidapi-mcp.py   # optional; RapidAPI MCP is separate from hw07 tool server
python scripts\verify_env.py        # OWUI_API_KEY required for KB upload
```

**Required env** (repo root `.env` and/or `homework/hw07/.env` — never commit):

| Variable | Purpose |
|----------|---------|
| `KAGGLE_API_TOKEN` | Download CVE CSV (`data/download_dataset.py`) or Kaggle MCP |
| `OWUI_URL` | Default `http://localhost:3000` |
| `OWUI_API_KEY` | Open WebUI → Settings → Account → API Keys |
| `RAPIDAPI_KEY` + `RAPIDAPI_HOST` | Optional for tool server primary upstream; omit → Shodan CVEDB fallback |
| `TOOLS_SERVER_PORT` | Default `5005` |

**MCP (Cursor, optional):** `.cursor/mcp.json` — `kaggle`, `openwebui` (stdio launcher), `rapidapi` (stdio `mcp-remote`, **tools only**, no prompts/resources). Homework grading uses **Open WebUI + tool server**, not RapidAPI MCP.

**Networking rule:** Open WebUI in Docker must reach the host tool server at  
`http://host.docker.internal:5005/openapi.json` — **not** `localhost`.

---

### Phase 1 — Docker stack + models

```powershell
cd homework\hw07
docker compose up -d
docker exec hw07-ollama ollama pull nomic-embed-text
docker exec hw07-ollama ollama pull llama3.1
docker compose ps   # both containers up; open-webui healthy
```

If port 3000 is taken: `docker stop open-webui` then re-run `docker compose up -d` here.

Sign-in (if needed): `python scripts/reset_webui_password.py --container hw07-open-webui`  
Default after reset: `admin@localhost.com` / `admin`

---

### Phase 2 — Dataset (Kaggle CVE CSV)

**Option A — script:**

```powershell
pip install -r requirements.txt
python data\download_dataset.py
# → homework/hw07/data/cve.csv (gitignored)
```

**Option B — Kaggle MCP:** Search CVE/CVSS datasets; pick one with `cve_id`, `cvss`, description/summary columns; save to `data/cve.csv`.

If download fails, ask me to set `KAGGLE_API_TOKEN` in repo root `.env` and re-run.

---

### Phase 3 — Knowledge base upload

```powershell
python owui_kb_setup.py --csv .\data\cve.csv --name "CVE Intelligence" `
  --description "Historical CVE / CVSS records for RAG"
```

Or use **openwebui MCP** if connected. Script is idempotent (reuses KB by name).

**Screenshot:** `screenshots/01-kb-upload.png`, `02-kb-indexed.png`

---

### Phase 4 — Tool server (host)

Terminal 1 (keep running):

```powershell
cd homework\hw07
.\scripts\start_tool_server.ps1
# or: python -m uvicorn tools_server:app --host 0.0.0.0 --port 5005 --reload
```

Verify:

```powershell
curl http://localhost:5005/health
curl http://localhost:5005/cve/CVE-2021-44228
curl http://localhost:5005/cve/not-a-cve    # expect 422
```

**Screenshot:** `screenshots/00-tool-server-openapi.png` (`/openapi.json` or `/docs`)

#### Tool contract (OpenAPI)

| Endpoint | Method | Operation ID | Input | Output |
|----------|--------|--------------|-------|--------|
| `/health` | GET | — | — | `{status, source, rapidapi_configured}` |
| `/cve/{cve_id}` | GET | **`lookup_cve`** | `cve_id`: string `CVE-YYYY-NNNN+` | `{cve_id, summary, cvss, epss, kev, published, references[], source}` |

**Edge cases implemented in code (must stay passing in pytest):**

- Empty / invalid CVE ID → HTTP 422
- RapidAPI configured but 404 → fallback to Shodan CVEDB
- RapidAPI not configured → CVEDB only
- Upstream connection failure → HTTP 502
- References truncated to 5 items
- No secret leakage in error responses

---

### Phase 5 — Register OpenAPI tool in Open WebUI

1. Open `http://localhost:3000`
2. **Admin → Settings → External Tools → Add OpenAPI server**
3. URL: **`http://host.docker.internal:5005/openapi.json`**
4. Save; confirm tool **`lookup_cve`** appears

**Screenshot:** `screenshots/04-tool-registered.png`

---

### Phase 6 — Model + system prompt + KB

1. **Workspace → Models →** edit **llama3.1** (or create custom model)
2. **Advanced → Function Calling = Native**
3. Attach knowledge base **CVE Intelligence**
4. Paste system prompt from [`prompts/system_prompt.md`](prompts/system_prompt.md) (full text below)
5. Enable external tool / OpenAPI server for this model

**Screenshot:** `screenshots/06-model-system-prompt.png`

---

### Phase 7 — Demo chats (prove KB vs live)

Start a **new chat** with llama3.1, KB attached, tools enabled.

| # | Type | Prompt | Pass criteria |
|---|------|--------|---------------|
| 1 | **KB** | "Which CVEs in my dataset affected Apache Struts, and what were their CVSS scores?" | Answer cites dataset; lists CVE IDs/scores from KB chunks; no fabricated IDs |
| 2 | **Tool** | "What is the current EPSS score and KEV status for CVE-2021-44228?" | Model calls `lookup_cve`; shows EPSS, KEV, CVSS from tool JSON |
| 3 | **Edge — invalid CVE** | "Look up CVE-INVALID live" | 422 or model explains invalid format; no hallucinated scores |
| 4 | **Edge — not in KB** | "What does my dataset say about CVE-2099-99999?" | "Not found in dataset" (no guess) |
| 5 | **Hybrid** | "From my dataset, what Apache CVEs exist? Then give live EPSS for CVE-2021-44228." | Two labeled sections: KB then tool |

**Screenshots:** `03-kb-answer.png`, `05-tool-function-io.png`, `07-live-tool-answer.png`

---

### Phase 8 — Tests + submission pack

```powershell
cd homework\hw07
python -m pytest tests/ -q
docker compose ps
```

**Screenshot:** `08-docker-healthy.png`

Copy checklist: [`SUBMISSION.md`](SUBMISSION.md)

---

### System prompt (paste into Open WebUI model settings)

Paste **verbatim** into Workspace → Models → llama3.1 → System prompt:

```
You are the **CVE Intelligence Assistant** for HW07 (Open WebUI + Kaggle KB + live tool server).

## Core responsibilities

1. Answer **historical / dataset** questions from the **CVE Intelligence** knowledge base (Kaggle CVE CSV).
2. Answer **current-risk** questions by calling the **`lookup_cve`** tool (live CVE API via the local tool server).
3. Never mix sources without labeling which you used.

## Routing — decide before answering

| User intent | Action |
|-------------|--------|
| Questions about the **uploaded CSV**, trends in the dataset, "in my data", historical records | Use **#CVE Intelligence** KB only |
| **Current** EPSS, KEV status, live CVSS, "right now", "today", a specific CVE ID for up-to-date risk | Call **`lookup_cve`** tool |
| Both historical context and current status for the same CVE | KB first for dataset context, then **`lookup_cve`** for live fields; use two labeled sections |

## Tool: `lookup_cve`

- **When:** User asks for live/current details of a specific CVE (e.g. CVE-2021-44228).
- **Input:** `cve_id` — string, format `CVE-YYYY-NNNN` (you normalize case).
- **Output fields:** `cve_id`, `summary`, `cvss`, `epss`, `kev`, `published`, `references` (max 5), `source` (`rapidapi` or `cvedb`).
- **Do not** use the tool for bulk dataset analytics — use the KB for that.

## Output format

- **KB answers:** Bullet list with CVE ID, product/vendor if present in chunks, CVSS from dataset. Cite that answers come from the uploaded CSV.
- **Tool answers:** State CVE ID, EPSS, KEV (yes/no), CVSS, one-line summary, and `source`. Note data is live, not from the CSV.
- **Hybrid:** Use headings `## From knowledge base (historical)` and `## Live lookup (tool)`.

## Edge cases — mandatory behavior

| Situation | Response |
|-----------|----------|
| No KB chunks retrieved | Say: "Not found in the CVE Intelligence dataset." Do **not** guess. |
| Invalid CVE format (not `CVE-YYYY-NNNN`) | Ask user to provide a valid CVE ID; do not call the tool. |
| Tool returns 404 / CVE not found | Report clearly; do not invent scores. |
| Tool/server error (502, timeout) | Report the error; suggest checking tool server at port 5005. |
| User asks about Log4Shell without CVE ID | KB: search dataset for Log4j/Log4Shell; Tool: use CVE-2021-44228 if they want live risk. |
| Ambiguous "Apache vulnerabilities" | Prefer KB for dataset listing; offer to look up a specific CVE live if they name one. |
| Never fabricate EPSS, KEV, CVSS, or references | Only use tool JSON or KB chunks. |

## Demo questions (for grading)

- **KB:** "Which CVEs in my dataset affected Apache Struts, and what were their CVSS scores?"
- **Tool:** "What is the current EPSS score and KEV status for CVE-2021-44228?"
```

Canonical copy also lives in [`prompts/system_prompt.md`](prompts/system_prompt.md).

---

### I/O reference (for graders)

```
┌─────────────────────────────────────────────────────────────────┐
│  User question                                                   │
└────────────┬───────────────────────────────┬────────────────────┘
             │ historical / dataset           │ live / current CVE
             ▼                                ▼
    ┌─────────────────┐              ┌──────────────────────┐
    │ #CVE Intelligence│              │ lookup_cve (OpenAPI)  │
    │ Open WebUI KB    │              │ → tools_server.py     │
    │ (Kaggle CSV)     │              │ → RapidAPI or CVEDB   │
    └─────────────────┘              └──────────────────────┘
```

---

### Troubleshooting

| Symptom | Fix |
|---------|-----|
| Tool works in curl, fails in OWUI | Use `host.docker.internal:5005`, not `localhost` |
| KB upload 401 | Regenerate `OWUI_API_KEY`; run `scripts/sync_env_from_services.py` |
| No tool call in chat | Native function calling ON; llama3.1; explicit "use lookup_cve" |
| RapidAPI MCP empty in Cursor | Must use stdio launcher (`run-mcp-rapidapi.py`), not HTTP type |
| RapidAPI MCP: no prompts/resources | Normal — RapidAPI MCP exposes **tools only** |
| hw07 stack vs other open-webui on :3000 | Stop conflicting container or use hw07 compose only |
| pytest fails | Fix before submission; report output honestly |

---

### Constraints

- Never hardcode or commit secrets (`.env`, API keys).
- Do not delete OWUI KB/users/chats without asking me.
- Run `python -m pytest tests/ -q` after any change to `tools_server.py` or `owui_kb_setup.py`.
- Match existing code style; minimal diffs.

When finished, list: KB id, tool server health JSON, demo chat outcomes, screenshot paths, pytest result.

---

## End of agent block
