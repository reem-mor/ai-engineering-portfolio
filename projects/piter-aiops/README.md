# PITER AiOps

**This project now lives in its own repository.**

| | |
|---|---|
| **Repo** | [github.com/reem-mor/piter-aiops](https://github.com/reem-mor/piter-aiops) |
| **What** | AWS Bedrock-powered incident-response platform — agentic (Bedrock Agent + Action-Group tools), RAG over runbooks, session memory, alert-storm handling, safe escalation |
| **Stack** | Flask · React · Bedrock Agent · Lambda action groups · Docker · 300+ tests |

Former path in this archive: full `projects/piter-aiops/` tree (removed after extraction).

```bash
git clone https://github.com/reem-mor/piter-aiops.git
cd piter-aiops
python -m venv .venv && .\.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt && cp .env.example .env
pytest -q
```

Extraction runbook: [`docs/extraction/piter-aiops/`](../../docs/extraction/piter-aiops/).
