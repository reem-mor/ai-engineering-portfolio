# HW07 Submission — CVE Intelligence Assistant

Open WebUI + Kaggle CVE knowledge base + live `lookup_cve` tool server.

## What was built

| Component | Description |
|-----------|-------------|
| **Knowledge Base** | **CVE Intelligence Dataset** — NVD/Kaggle CVE CSV (`data/cve.csv`) indexed for historical RAG |
| **Tool server** | FastAPI at `http://localhost:5005` — OpenAPI tool `lookup_cve` with Pydantic I/O schema |
| **Live upstream** | Shodan CVEDB fallback (free). Optional RapidAPI CVE host via `RAPIDAPI_CVE_HOST` |
| **Custom model** | `cve-intelligence-assistant` on `llama3.1:latest` with KB + native function calling |
| **System prompt** | [`prompts/system_prompt.md`](prompts/system_prompt.md) — routes KB vs live tool |

## How to run (reproduce)

```powershell
cd homework\hw07
docker compose up -d
docker exec hw07-ollama ollama pull nomic-embed-text
docker exec hw07-ollama ollama pull llama3.1

# Env: copy .env.example → .env (OWUI_EMAIL, OWUI_PASSWORD, optional RAPIDAPI_*)
python data\download_dataset.py          # needs KAGGLE_API_TOKEN in repo root .env
python scripts\sync_env_from_services.py # optional OWUI_API_KEY refresh
python scripts\bootstrap_owui.py         # KB + tool registration + model

python scripts\verify_tool_server.py
python -m pytest -q
python scripts\run_demo_chats.py
python scripts\capture_screenshots.py
```

## Docker services

| Service | Container | Port |
|---------|-----------|------|
| Open WebUI | `hw07-open-webui` | 3000 |
| Ollama | `hw07-ollama` | 11434 |
| Tool server | `hw07-tool-server` | 5005 |

## Model & embedding

- **Chat model:** `llama3.1:latest` (custom preset: `cve-intelligence-assistant`)
- **Embedding:** `nomic-embed-text` via Ollama (`RAG_EMBEDDING_ENGINE=ollama`)

## Knowledge base

- **Name:** CVE Intelligence Dataset
- **File:** `data/cve.csv` (Kaggle/NVD CVE records with CVSS, Apache/Log4j keywords)
- **Upload:** `python owui_kb_setup.py` or `python scripts/bootstrap_owui.py` (JWT or API key)

## RapidAPI / live tool

| Setting | Value |
|---------|-------|
| Tool OpenAPI (Docker OWUI) | `http://tool-server:5005/openapi.json` |
| Tool OpenAPI (host) | `http://localhost:5005/openapi.json` |
| Operation ID | `lookup_cve` |
| Input | `cve_id` path param — `CVE-YYYY-NNNN` |
| Output | JSON: `cve_id`, `summary`, `cvss`, `epss`, `kev`, `published`, `references[]`, `source` |
| RapidAPI | `RAPIDAPI_KEY` + `RAPIDAPI_CVE_HOST` for CVE APIs. `RAPIDAPI_HOST=jsearch.*` is **not** used by the CVE tool (JSearch is a separate MCP product) |
| Fallback | Shodan CVEDB when no CVE-compatible RapidAPI host — `mode=fallback` in `/health` |

Verify: `python scripts\verify_tool_server.py`

## Tests

```powershell
python -m pytest -q
# Expected: 32 passed
```

## Screenshots

| # | File | What to show |
|---|------|----------------|
| 00 | `00-tool-server-openapi.png` | FastAPI `/docs` or `/openapi.json` |
| 01 | `01-kb-upload.png` | Knowledge base with `cve.csv` attached |
| 02 | `02-kb-indexed.png` | File indexed / processing complete |
| 03 | `03-kb-answer.png` | Chat: Apache Struts CVEs from dataset |
| 04 | `04-tool-registered.png` | Admin → External Tools: OpenAPI server |
| 05 | `05-tool-function-io.png` | Tool call `lookup_cve` in chat |
| 06 | `06-model-system-prompt.png` | Model settings: prompt + KB + function calling |
| 07 | `07-live-tool-answer.png` | Chat: live EPSS/KEV for CVE-2021-44228 |
| 08 | `08-docker-healthy.png` | `docker compose ps` — hw07 stack |

## Demo questions (5)

| # | Type | Question | Expected behavior |
|---|------|----------|-------------------|
| 1 | **KB** | Which CVEs in my dataset affected Apache Struts, and what were their CVSS scores? | Lists CVE IDs + CVSS from uploaded CSV; cites dataset |
| 2 | **Tool** | What is the current EPSS score and KEV status for CVE-2021-44228? | Calls `lookup_cve`; shows live EPSS, KEV, CVSS |
| 3 | **Edge** | Look up CVE-INVALID live | Explains invalid CVE format; no fabricated scores |
| 4 | **Edge** | What does my dataset say about CVE-2099-99999? | Should refuse / not found in dataset |
| 5 | **Hybrid** | From my dataset, what Apache CVEs exist? Then give live EPSS for CVE-2021-44228. | KB section + live tool section |

Run automated demos: `python scripts\run_demo_chats.py`

## Final verification checklist

```
HW07 Final Verification:
- Docker containers: PASS
- Open WebUI login/admin: PASS
- Ollama connection: PASS
- Chat model available: PASS
- Embedding model available: PASS
- Knowledge Base created: PASS
- KB file uploaded/indexed: PASS
- RapidAPI/CVE tool registered: PASS
- Demo KB question works: PASS
- Demo live search question works: PASS
- pytest: PASS (32 passed)
- screenshots generated: see screenshots/
- submission docs updated: PASS
```
