# amdocs-ai-course — AI Engineering Coursework & Learning Archive

<p align="center">
  <strong>Re'em Mor — AI Engineer × SRE.</strong><br>
  Production SRE/NOC background in regulated environments, now building AI systems
  that hold up in production.
</p>

<p align="center">
  <a href="#featured-work">Featured work</a> ·
  <a href="#what-this-repo-is">What this is</a> ·
  <a href="#repository-map">Repository map</a> ·
  <a href="#projects-in-this-repo">Projects</a> ·
  <a href="#course-milestones">Milestones</a> ·
  <a href="#quick-start">Quick start</a>
</p>

<p align="center">
  <a href="../../actions/workflows/ci.yml"><img alt="CI" src="https://img.shields.io/badge/CI-ruff%20%2B%20pytest-success"></a>
  <img alt="Python" src="https://img.shields.io/badge/Python-3.12-blue">
  <img alt="Stack" src="https://img.shields.io/badge/Stack-FastAPI%20%C2%B7%20Flask%20%C2%B7%20React-009688">
  <img alt="AI" src="https://img.shields.io/badge/AI-RAG%20%C2%B7%20AWS%20Bedrock%20%C2%B7%20FAISS-purple">
  <img alt="License" src="https://img.shields.io/badge/License-MIT-green">
</p>

---

## What this repo is

This repository is my **learning archive** for the Amdocs / Lab17 **AI-Augmented Software
Engineering** course: lecture write-ups, homework, labs, and the course projects that grew
out of them — from Python fundamentals to full-stack RAG applications, Docker, and AWS.

It is a *teaching and portfolio archive*, kept lean and honest. **My flagship projects live
in their own repositories** — see Featured work below. Use this repo to see the progression
and the engineering habits behind the flagships.

**About me:** B.Sc. Computer Science (The Open University of Israel, GPA 91, finishing now);
production SRE/NOC experience in regulated, multi-jurisdiction online-gaming environments
(alert triage, incident response, production DB ops). Bilingual EN/HE.
GitHub: [github.com/reem-mor](https://github.com/reem-mor).

---

## Featured work

The serious, standalone projects — built as production-minded systems, each in its own repo:

| Project | What it is | Repo |
|---------|------------|------|
| **PITER AiOps** | AWS Bedrock-powered incident-response platform — agentic (Bedrock Agent + Action-Group tools), RAG over runbooks, session memory, alert-storm handling and safe escalation. Flask/React, Docker. | [reem-mor/piter-aiops](https://github.com/reem-mor/piter-aiops) <sup>*(extraction in progress; currently also at [`projects/piter-aiops/`](projects/piter-aiops/))*</sup> |
| **HINDSIGHT** | Intelligent incident-log / document analyst with semantic search — turns operational history into searchable, grounded answers. | [reem-mor/hindsight](https://github.com/reem-mor/hindsight) |

**Core stack:** Python · FastAPI / Flask · AWS Bedrock · RAG (FAISS / pgvector) · Docker ·
n8n automation · React.

---

## Projects in this repo

These are the course projects. The agentic flagship (PITER AiOps) is the most advanced and
is being extracted to its own repo; the other two show the RAG progression.

| Project | Folder | Stack | Status |
|---------|--------|-------|--------|
| **IncidentIQ** — Incident Assistant RAG | [`projects/incident-assistant-rag`](projects/incident-assistant-rag/) | FastAPI · OpenAI · local FAISS · React · Docker | **Featured capstone.** Full-stack RAG for incident ops: grounded answers, no-context refusal, source transparency, tests + evaluation. |
| **PITER AiOps** | [`projects/piter-aiops`](projects/piter-aiops/) | Flask · AWS Bedrock **Agent** · React · Docker | **Flagship.** Agent + tools + memory + escalation. Moving to [its own repo](https://github.com/reem-mor/piter-aiops). |
| **Incident RAG (Bedrock)** | [`projects/incident-rag-bedrock`](projects/incident-rag-bedrock/) | Flask · AWS Bedrock KB · React | **Learning iteration** — the Bedrock-managed-RAG stepping-stone that PITER grew from. |

There is also **[`oz_veruach_bot/`](oz_veruach_bot/)** — a standalone bilingual (HE/EN)
Telegram assistant for the course cohort (async, SQLAlchemy + Alembic, multi-LLM, Docker,
strict typing + 200+ tests). It's a separate product living here for now.

---

## Repository map

```text
amdocs-ai-course/
├── README.md                 # you are here
├── AGENTS.md                 # canonical cross-tool agent guidance
├── CLAUDE.md                 # sources @AGENTS.md
├── LICENSE                   # MIT (own code) + IP carve-out for course material
├── CONTRIBUTING.md           # homework/submission workflow
├── requirements.txt          # root deps (UTF-8)
├── .mcp.json                 # project MCP servers (only what's used)
│
├── .github/workflows/ci.yml  # ruff + pytest
├── pyproject.toml            # root ruff config
│
├── docs/                     # course docs, architecture, audit, security
├── resources/MANIFEST.md     # course slides/handouts live in Drive (third-party IP)
├── lectures/                 # 01–09 lesson write-ups + demos
├── homework/                 # hw01–hw06
├── exercises/                # standalone labs
│
├── oz_veruach_bot/           # standalone Telegram bot (own product)
└── projects/
    ├── incident-assistant-rag/   # featured capstone (FastAPI + OpenAI + FAISS)
    ├── piter-aiops/              # flagship (Bedrock agent) — extracting to own repo
    └── incident-rag-bedrock/     # Bedrock-KB learning iteration
```

---

## Course milestones

| Lesson | Focus | Portfolio value |
|--------|-------|-----------------|
| 01 | Jupyter & Python basics | Clear technical communication and Python fundamentals |
| 02 | Python foundations | Functions, data structures, validation, control flow |
| 03 | OOP & NumPy | Classes, arrays, numerical foundations |
| 04 | NLP & RAG foundations | Tokenization, embeddings, semantic search, FAISS, LLM APIs |
| 05 | Flask web development | Routes, forms, Jinja2, static files |
| 06 | SQLite & RAG web app | CRUD, session memory, FAISS, async UI |
| 07 | Docker & AWS EC2 | Images, containers, Dockerfile, EC2, SSH, Nginx, Security Groups |
| 08 | Model Context Protocol (MCP) | Stdio MCP server, FastMCP tools, MCP Inspector |
| 09 | Bedrock Flows & n8n | Managed agent flows + n8n automation workflows |
| Project | Full-stack AI system | End-to-end delivery: FastAPI/React, FAISS/Bedrock, Docker, tests, docs |

---

## Skills demonstrated

| Category | Skills |
|----------|--------|
| AI Engineering | RAG, embeddings, FAISS, AWS Bedrock (KB + Agent), prompt grounding, no-context refusal, source attribution, agentic tools |
| Backend | Python, FastAPI, Flask, REST APIs, Pydantic, error handling |
| Frontend | React, TypeScript, Vite, operational UIs |
| Data | SQLite, pgvector, CRUD, conversation memory, metadata |
| DevOps / SRE | Docker, Docker Compose, Nginx, AWS EC2, SSH, Security Groups, incident-ops thinking |
| Quality | pytest, evaluation harnesses, CI (ruff + pytest), documentation |
| Security | `.env` separation, `.gitignore`/`.dockerignore`, env-interpolated secrets, no key exposure |

---

## Quick start

```bash
git clone https://github.com/reem-mor/amdocs-ai-course.git
cd amdocs-ai-course
python -m venv .venv && source .venv/bin/activate   # Windows: .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Each project and most lectures are self-contained — `cd` into one and follow its README.
Copy `.env.example` to `.env` where a project needs keys (never commit `.env`).

**Run the featured capstone:**

```bash
cd projects/incident-assistant-rag
docker compose up --build
```

**Run the offline test suites (what CI runs):**

```bash
cd projects/incident-assistant-rag/backend && pip install -r requirements.txt && pytest -q
cd projects/incident-rag-bedrock && pip install -r requirements.txt && pytest -q
```

---

## Quality & security

- Per-project READMEs with setup and usage.
- Secrets via environment variables; `.env` gitignored, only `.env.example` committed.
- MCP/credential config uses env interpolation and AWS named profiles — no hardcoded keys.
- Docker + `.dockerignore` for clean builds.
- CI (ruff + pytest) on the kept Python areas.
- Grounded RAG behavior with source transparency and no-context refusal in the projects.

A full employer-readiness audit lives in [`docs/AUDIT_2026.md`](docs/AUDIT_2026.md);
security/history remediation notes in
[`docs/SECURITY_REMEDIATION.md`](docs/SECURITY_REMEDIATION.md).

---

## License

Original code is licensed under the [MIT License](LICENSE). Course slides, PPTX, and DOCX
handouts are Amdocs/Lab17 educational materials and are **not redistributed here** — see
[`resources/MANIFEST.md`](resources/MANIFEST.md). Do not commit secrets or credentials.
