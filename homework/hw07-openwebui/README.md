# Netflix KB + Local Tool Server Homework

## Overview
This project demonstrates two assistant capabilities:

1. **Knowledge Base (KB)** using a Kaggle CSV uploaded into Open WebUI.
2. **Local Python Tool Server** that calls an external API through RapidAPI.

The assistant can:
- answer dataset questions using the uploaded KB
- answer live country questions using the local Python server

---

## Dataset
**Dataset:** Netflix Movies and TV Shows  
**Source:** Kaggle  
**Link:** https://www.kaggle.com/datasets/shivamb/netflix-shows

This dataset includes fields such as:
- `show_id`
- `type`
- `title`
- `director`
- `cast`
- `country`
- `date_added`
- `release_year`
- `rating`
- `duration`
- `listed_in`
- `description`

---

## External API
**API used:** Country State City - Search REST API  
**Source:** RapidAPI  
**Plan:** Free Basic tier

This API is relevant because the Netflix dataset contains a `country` field, so the assistant can combine dataset questions with live country information.

Example:
- KB question: "List 5 Netflix titles from France"
- Tool question: "What currency is used in France?"

The RapidAPI `/allcountries` payload includes fields such as `name`, `isoCode`, `currency`, `phonecode`, `latitude`, `longitude`, `flag`, and `timezones`. It does not include capital or region.

---

## Project Structure

```text
hw07-openwebui/
├── README.md
├── requirements.txt
├── .env.example
├── tools_server.py
├── test_tools_server.py
├── system_prompt.txt
├── openwebui_function_tool.py
├── screenshots_checklist.md
└── data/
    ├── download_dataset.py
    └── netflix_titles.csv
```

---

## Setup

### 1. Install dependencies
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

### 2. Download dataset (optional if CSV already present)
Requires Kaggle CLI credentials (`kaggle.json` or `KAGGLE_USERNAME` / `KAGGLE_KEY`):

```powershell
python data/download_dataset.py
```

### 3. Create environment file
Copy `.env.example` and create your own `.env` file in this folder:

```powershell
Copy-Item .env.example .env
```

Then add your RapidAPI key:
```env
RAPIDAPI_KEY=your_real_rapidapi_key_here
```

The server loads only `homework/hw07-openwebui/.env` (not the repo root `.env`).

### 4. Run the local server
```powershell
python tools_server.py
```

The server runs on:
```text
http://localhost:5005
```

### 5. Run tests
```powershell
python -m pytest -v
```

---

## Recommended Local Model Setup

For this homework, keep the local model stack simple:

- **Chat model:** `llama3.2:3b` in Ollama, or `llama3.1:8b` if your machine runs it comfortably.
- **Knowledge Base embeddings:** `nomic-embed-text`.
- **Advanced optional model:** Qwen3.6 via a separate `llama-server` is useful for experiments, but it is not required for this KB + local tool workflow.

In Open WebUI, configure Ollama as the model provider, set `nomic-embed-text` for document embeddings, then attach the `Netflix Shows KB` to the chat/model.

---

## Open WebUI KB Setup

1. Open Open WebUI.
2. Go to **Workspace** -> **Knowledge**.
3. Create a new Knowledge Base called `Netflix Shows KB`.
4. Upload `data/netflix_titles.csv`.
5. Wait until indexing is complete.
6. Use this KB in your chat/model.

---

## Open WebUI Tool Setup

1. Go to **Workspace** -> **Tools** or **Functions**.
2. Create a new tool/function.
3. Copy the code from `openwebui_function_tool.py`.
4. Save and enable the tool.
5. Make sure your local Flask server is running on `http://localhost:5005`.

The copied tool uses `http://host.docker.internal:5005`, which is the usual address when Open WebUI runs in Docker and the Flask server runs on the Windows host. If Open WebUI and the tool server run in the same Docker Compose network, change the tool base URL to `http://tools-server:5005`. If Open WebUI runs directly on the host, use `http://localhost:5005`.

---

## System Prompt

Use the content from `system_prompt.txt` in your model or chat system prompt.

Purpose:
- use KB for dataset questions
- use tool for live country questions
- combine both when needed

---

## Local Server Endpoints

### `GET /health`
Checks if the local server is running.

### `GET /country/<country_name>`
Returns country information from RapidAPI.

---

## Sample Questions and Expected Behavior

### KB questions
These should be answered from the uploaded CSV:
- `#netflix-shows-kb List 5 Netflix titles from India.`
- Which titles were released in 2020?
- What ratings appear most often in the dataset?
- Show movies from the United States.

### Tool questions
These should use the local Python server:
- What currency is used in Japan?
- What is the ISO code for France?
- What phone code is used in Brazil?
- Give me country details for Canada.

### Combined questions
These can use both KB and tool:
- `#netflix-shows-kb Show 3 Netflix titles from Japan and tell me Japan's currency.`
- List Netflix titles from France and give me France's currency.

---

## Post-Upgrade Verification

The project was upgraded and retested against Open WebUI `v0.10.2`.

Verified runtime:

- Open WebUI: `ghcr.io/open-webui/open-webui:latest`, healthy on `http://localhost:8080`
- Tool server: healthy on `http://localhost:5005`
- Ollama: running directly on Windows host for better local inference speed
- Chat model available: `llama3.2:3b`
- Embedding model available: `nomic-embed-text:latest`
- Workspace Knowledge: `Netflix Shows KB`
- Workspace Tool: `Netflix Country Info`
- Workspace Prompt: `Netflix HW07 System Prompt`

Automated checks:

```text
python -m pytest -v
15 passed, 1 warning

python -m ruff check homework/hw07-openwebui
All checks passed
```

Post-upgrade evidence files:

- `submission/evidence-after-upgrade.json` - Open WebUI health, models, tool, prompt API evidence.
- `submission/evidence-after-upgrade-db.json` - database-level proof for KB, document, knowledge, tool, and prompt after migration.
- `submission/final-evidence-host-ollama.json` - final proof that Open WebUI is connected to host Ollama and can complete chat with `llama3.2:3b`.
- `submission/QA_AFTER_UPGRADE.md` - final input/output questions and edge-case results.
- `submission/edge-case-results-after-upgrade.json` - raw edge-case endpoint outputs.

Post-upgrade screenshots:

- `submission/04-openwebui-health.png`
- `submission/05-openwebui-knowledge.png`
- `submission/06-openwebui-tools.png`
- `submission/07-openwebui-prompts.png`
- `submission/11-openwebui-models.png`
- `submission/12-edge-atlantis.png`
- `submission/13-edge-partial-fran.png`
- `submission/14-edge-united-states.png`
- `submission/15-edge-bad-route.png`
- `submission/16-edge-cote-divoire-after-upgrade.png`

Important note: the Open WebUI `Models` workspace tab shows custom model presets, not the raw Ollama runtime model list. Runtime model availability is proven by `ollama list`, `submission/evidence-after-upgrade.json`, and `submission/final-evidence-host-ollama.json`.

Open WebUI is configured to reach host Ollama through `http://host.docker.internal:11434`. For a polished manual demo, run:

1. `#netflix-shows-kb List 5 Netflix titles from India.`
2. `What currency is used in France?`
3. `#netflix-shows-kb Show 3 Netflix titles from Japan and tell me Japan's currency.`

Five edge cases verified:

1. Unknown country: `GET /country/Atlantis` -> `404`
2. Accented input: `GET /country/Côte d'Ivoire` -> `200`, currency `XOF`
3. Partial lowercase input: `GET /country/fran` -> `200`, matches France
4. Encoded space: `GET /country/United%20States` -> `200`, currency `USD`
5. Bad route: `GET /country/` -> `404`

---

## Submission

Submit:
- all project files
- screenshots listed in `screenshots_checklist.md`
- explanation of KB questions vs tool questions
- post-upgrade evidence files in `submission/`
