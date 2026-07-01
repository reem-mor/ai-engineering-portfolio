# Setup Guide

## Prerequisites

- Python 3.12+
- Git
- Node.js 18+ (for React/Vite projects)
- Docker Desktop (optional, for container labs and capstone)
- AWS account (optional, for EC2/nginx homework lab)

## Clone and base environment

**Recommended (agents + humans):**

```powershell
git clone https://github.com/reem-mor/ai-engineering-portfolio.git
cd ai-engineering-portfolio
.\scripts\setup-dev.ps1
```

This creates `.venv`, installs dev tools + lecture-08 MCP deps, and copies `.env.example` → `.env`.

**Manual equivalent:**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
copy .env.example .env
```

For full lecture ML stack (torch, spacy, …): `pip install -r requirements.txt` — see [`REQUIREMENTS.md`](../REQUIREMENTS.md).

## Agent / MCP tooling

See **[`docs/AGENT-TOOLING.md`](AGENT-TOOLING.md)** — MCP server catalog, Cursor skills, rules, and CI matrix.

## NLTK data (lecture 04 NLP demos)

```powershell
python -c "import nltk; nltk.download('punkt'); nltk.download('punkt_tab'); nltk.download('stopwords'); nltk.download('wordnet'); nltk.download('omw-1.4'); nltk.download('averaged_perceptron_tagger_eng')"
```

## Environment variables

Copy the root template (placeholders only):

```powershell
copy .env.example .env
```

Never commit `.env`. The capstone project uses its own `backend/.env` — see that project's README.

Typical variables:

| Variable | Used in |
|----------|---------|
| `OPENAI_API_KEY` | RAG homework, capstone |
| `GEMINI_API_KEY` | Lecture 06 Flask RAG demo, lecture 08 tool-calling demo |
| `HF_TOKEN` | Hugging Face models in lecture demos |
| `KAGGLE_API_TOKEN` | Kaggle MCP — dataset download for hw07 ([Kaggle Settings](https://www.kaggle.com/settings)) |
| `RAPIDAPI_KEY` | hw07 Open WebUI tool server — live API lookups |

## Run by area

### Homework 03 (pytest)

```powershell
cd homework/hw03
pytest -v
```

### Lecture 05 — Flask intro

```powershell
cd lectures/05_flask_intro
python app.py
```

Open http://127.0.0.1:5000

### Lecture 06 — Flask + RAG

```powershell
cd lectures/06_flask_advanced_rag
copy .env.example .env
# Edit .env with your keys
python app.py
```

### Homework 05 — EC2 / Docker / Nginx

Follow [`homework/hw05/nginx-docker-lab/README.md`](../homework/hw05/nginx-docker-lab/README.md) and the handout [`resources/handouts/ubuntu-ec2-docker-nginx-student-exercise.docx`](../resources/MANIFEST.md).

### Lecture 08 — MCP

```powershell
cd lectures/08_mcp
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Copy the Cursor MCP template to the workspace (from repo root). Prefer the **root [`.mcp.json`](../.mcp.json)** — Cursor loads it automatically. For lecture-only minimal set:

```powershell
mkdir .cursor -ErrorAction SilentlyContinue
copy lectures\08_mcp\config\mcp.json.example .cursor\mcp.json
```

Or use the cross-platform launcher (after `setup-dev.ps1`):

```powershell
python scripts\run-mcp-course-tools.py
```

Restart Cursor and confirm **Settings → MCP** shows `course-tools`. See [`lectures/08_mcp/README.md`](../lectures/08_mcp/README.md) and [`docs/AGENT-TOOLING.md`](AGENT-TOOLING.md).

Optional Gemini demo (not MCP):

```powershell
copy .env.example .env
python demos\tool_calling_demo.py
```

### Homework 07 — Open WebUI + live tools

```powershell
cd homework\hw07
pip install -r requirements.txt
copy .env.example .env
# Set RAPIDAPI_KEY in .env; optional KAGGLE credentials for dataset download
python -m uvicorn tools_server:app --host 0.0.0.0 --port 5005
```

See [`homework/hw07/README.md`](../homework/hw07/README.md) for Open WebUI Docker setup and KB upload.

**MCP servers for hw07:** Root [`.mcp.json`](../.mcp.json) includes `kaggle` (HTTP) and `course-tools` (stdio). Set `KAGGLE_API_TOKEN` in your user environment before connecting.

### Lecture 11 — Local models (Qwen3.6 + llama.cpp)

```powershell
.\.venv\Scripts\pip.exe install -r lectures/11_local_models_webui/requirements.txt `
  --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cpu
.\lectures\11_local_models_webui\scripts\download_qwen36.ps1
.\lectures\11_local_models_webui\scripts\start_llama_server.ps1
```

Set `HF_TOKEN` in `.env`. Skill: [`.cursor/skills/local-models/SKILL.md`](../.cursor/skills/local-models/SKILL.md). Full guide: [`lectures/11_local_models_webui/README.md`](../lectures/11_local_models_webui/README.md).

### Capstone — IncidentIQ

```powershell
cd projects/incident-assistant-rag
```

Follow [`projects/incident-assistant-rag/README.md`](../projects/incident-assistant-rag/README.md).

## Troubleshooting

| Issue | Fix |
|-------|-----|
| `pytest` blocked on Windows | Use `python -m pytest` |
| Missing NLTK corpora | Run the NLTK download command above |
| API errors in RAG demos | Check `.env` keys and model names |
| MCP server not connecting in Cursor | Copy `mcp.json.example` to `.cursor/mcp.json`; use venv Python path on Windows |
| Docker build fails on hw04 | hw04 is scaffold-only — full RAG lives in [`projects/incident-assistant-rag/`](../projects/incident-assistant-rag/) |
| VS Code shows many extra folders | Local caches + old copies — run `.\scripts\clean-workspace.ps1`; copy [`.vscode/settings.json.example`](../.vscode/settings.json.example) to hide clutter |
| `projects/piter-aiops/` reappeared | Do not develop PITER here — clone [github.com/reem-mor/piter-aiops](https://github.com/reem-mor/piter-aiops) separately |

## Workspace hygiene

After cloning or switching branches, remove local-only artifacts:

```powershell
.\scripts\clean-workspace.ps1
```

See [`docs/STRUCTURE.md`](STRUCTURE.md) for committed vs gitignored folders.
