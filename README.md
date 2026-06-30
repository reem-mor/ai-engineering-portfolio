<div align="center">

# AI Engineering Portfolio

### Learning archive & capstone projects — Amdocs / Lab17 AI-Augmented Software Engineering

**AI Engineer × SRE** — production-minded systems · grounded RAG · agentic ops · deterministic safety floors

[![CI](https://github.com/reem-mor/ai-engineering-portfolio/actions/workflows/ci.yml/badge.svg)](https://github.com/reem-mor/ai-engineering-portfolio/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python&logoColor=white)](#skills--competencies)
[![Tests](https://img.shields.io/badge/In--repo_tests-201%2B%20pytest-brightgreen)](#production-engineering-habits)
[![Ecosystem](https://img.shields.io/badge/Ecosystem-650%2B%20tests%20total-blueviolet)](#featured-work)
[![Stack](https://img.shields.io/badge/Stack-FastAPI%20%C2%B7%20Flask%20%C2%B7%20React-009688)](#skills--competencies)
[![AI](https://img.shields.io/badge/AI-RAG%20%C2%B7%20Bedrock%20%C2%B7%20Agents-purple)](#skills--competencies)

<p>
  <img src="https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white" alt="FastAPI">
  <img src="https://img.shields.io/badge/Flask-000000?logo=flask&logoColor=white" alt="Flask">
  <img src="https://img.shields.io/badge/AWS%20Bedrock-232F3E?logo=amazonaws&logoColor=white" alt="AWS Bedrock">
  <img src="https://img.shields.io/badge/Docker-2496ED?logo=docker&logoColor=white" alt="Docker">
  <img src="https://img.shields.io/badge/Kubernetes-326CE5?logo=kubernetes&logoColor=white" alt="Kubernetes">
  <img src="https://img.shields.io/badge/Terraform-7B42BC?logo=terraform&logoColor=white" alt="Terraform">
  <img src="https://img.shields.io/badge/React-61DAFB?logo=react&logoColor=black" alt="React">
  <img src="https://img.shields.io/badge/n8n-EA4B71?logo=n8n&logoColor=white" alt="n8n">
  <img src="https://img.shields.io/badge/MCP-Model_Context_Protocol-6E40C9" alt="MCP">
</p>

[Employer review](#-60-second-employer-review) · [Featured work](#featured-work) · [Skills](#skills--competencies) · [Architecture](#architecture) · [Learning journey](#learning-journey) · [Curriculum](#curriculum) · [MCP & agents](#mcp--agent-tooling) · [Evidence gallery](#evidence-gallery) · [Quick start](#quick-start)

**[Re'em Mor](https://github.com/reem-mor)** · B.Sc. CS (GPA 91) · Production SRE/NOC @ regulated multi-jurisdiction gaming · [Profile README](https://github.com/reem-mor/reem-mor)

> Former repo name: `amdocs-ai-course` (GitHub redirects automatically)

</div>

---

## Who this is for

| Audience | Start here | Time |
|----------|------------|------|
| **Hiring manager / recruiter** | [60-second review](#-60-second-employer-review) → [**PITER AiOps**](https://github.com/reem-mor/piter-aiops) | ~2 min |
| **Technical interviewer** | [Featured work](#featured-work) → [`incident-assistant-rag/`](projects/incident-assistant-rag/) → [Evidence gallery](#evidence-gallery) | ~10 min |
| **Engineering lead (AI/SRE)** | [Skills matrix](#skills--competencies) · [RAG evolution](#rag-evolution--two-tracks) · [Production habits](#production-engineering-habits) | ~15 min |
| **Self-learner** | [Quick start](#quick-start) · [`docs/SYLLABUS.md`](docs/SYLLABUS.md) | — |

---

## ⏱ 60-second employer review

**The headline:** I build AI systems that survive production — not demos that only work on the happy path.

By day I run **regulated, multi-jurisdiction infrastructure** (500+ nodes, Kubernetes, Terraform, on-call incident response). This archive shows how I applied that ops mindset to AI engineering: **grounded RAG, tool-using agents, MCP integrations, and guardrails that override LLM output when safety matters.**

**Review in this order:**

1. **[PITER AiOps](https://github.com/reem-mor/piter-aiops)** — flagship Bedrock Agent + RAG incident platform · **325+ tests**
2. **[IncidentIQ capstone](projects/incident-assistant-rag/)** — full-stack grounded RAG in this repo · **90 tests · eval 5/5**
3. **[course-assistant-bot](https://github.com/reem-mor/course-assistant-bot)** — production Telegram bot · **224 tests · mypy strict**
4. **[HINDSIGHT](https://github.com/reem-mor/hindsight)** — document intelligence pipeline · n8n + Gemini + FastAPI
5. **This repo** — honest progression from Python → RAG → agents/MCP with CI evidence

---

## What I learned & practiced

Four stages, each with **runnable artifacts** — not slide-only coursework.

| Stage | Topics mastered | Key deliverables | Outcome |
|-------|-----------------|------------------|---------|
| **1 — Foundations** | Python 3.12, OOP, NumPy, pytest | hw01–03, lectures 01–03 | Typed, tested Python baseline |
| **2 — RAG & Web** | Embeddings, FAISS, chunking, Flask/FastAPI | hw04 scaffold → [**IncidentIQ**](projects/incident-assistant-rag/) | Grounded answers + source citation + **no-context refusal** |
| **3 — Ops & Agents** | Docker, EC2, MCP, n8n, Bedrock, LangGraph, Open WebUI | hw05–07, lectures 07–11 | Containerized labs, agent workflows, tool servers |
| **4 — Capstone & Flagships** | Bedrock KB → Agent, extraction to standalone repos | [PITER](https://github.com/reem-mor/piter-aiops), [bot](https://github.com/reem-mor/course-assistant-bot), [HINDSIGHT](https://github.com/reem-mor/hindsight) | Production-minded systems with CI, Docker, guardrails |

**Engineering principles repeated across every project:**

- Deterministic safety floors — scoring, thresholds, and eligibility in code, not LLM prose
- No-context refusal — fixed response when retrieval misses; no wasted LLM calls
- Structured errors, health endpoints, secrets via env vars only
- pytest + ruff in CI; externals mocked in tests

---

## Featured work

Production-minded AI systems — each with **screenshot evidence**, stack, and test counts. Pin order: [flagships README](flagships/README.md).

---

### 🛰️ [PITER AiOps](https://github.com/reem-mor/piter-aiops) — flagship · **325+ tests**

<a href="https://github.com/reem-mor/piter-aiops"><img src="docs/screenshots/featured/piter-investigation-triage.png" alt="PITER AiOps — investigation detail with triage and RAG citations" width="100%"/></a>

| | |
|---|---|
| **What it does** | Agentic incident-response for NOC/SRE: Bedrock Agent + RAG over runbooks, 4 Lambda action groups, session memory, **safe escalation previews** (humans decide). |
| **Stack** | AWS Bedrock · RAG · Lambda · Flask · React · Docker |
| **Highlights** | Alert storm → P1 triage → RAG citations → correlation chain → escalation preview |

<p align="center">
  <a href="https://github.com/reem-mor/piter-aiops"><img src="docs/screenshots/featured/piter-rag-citations.png" alt="PITER — RAG citations" width="49%"/></a>
  <a href="https://github.com/reem-mor/piter-aiops#see-it-working"><img src="docs/screenshots/featured/piter-see-it-working.png" alt="PITER — demo gallery" width="49%"/></a>
</p>

---

### 🧠 [IncidentIQ](projects/incident-assistant-rag/) — in-repo capstone · **90 tests · eval 5/5**

<a href="projects/incident-assistant-rag/"><img src="docs/screenshots/featured/incidentiq-rag-chat.png" alt="IncidentIQ — grounded RAG chat with source citations and confidence badges" width="100%"/></a>

| | |
|---|---|
| **What it does** | Full-stack incident assistant: upload runbooks → FAISS index → grounded chat with **source citations**, confidence scores, and **fixed refusal** when retrieval misses. |
| **Stack** | FastAPI · OpenAI · FAISS · React · Docker |
| **Highlights** | Deterministic no-context refusal · RAG eval harness · Swagger API · incident analysis panel |

<p align="center">
  <a href="projects/incident-assistant-rag/"><img src="projects/incident-assistant-rag/screenshots/07_frontend_rag_chat_irrelevant.png" alt="IncidentIQ — no-context refusal" width="32%"/></a>
  <a href="projects/incident-assistant-rag/"><img src="projects/incident-assistant-rag/screenshots/08_frontend_incident_analysis.png" alt="IncidentIQ — incident analysis" width="32%"/></a>
  <a href="projects/incident-assistant-rag/"><img src="projects/incident-assistant-rag/screenshots/12_backend_evaluation_5_of_5.png" alt="IncidentIQ — RAG evaluation 5/5" width="32%"/></a>
</p>

---

### 🔎 [HINDSIGHT](https://github.com/reem-mor/hindsight) — document intelligence pipeline

<a href="https://github.com/reem-mor/hindsight"><img src="docs/screenshots/featured/hindsight-workflow.png" alt="HINDSIGHT — n8n cloud workflow canvas" width="100%"/></a>

| | |
|---|---|
| **What it does** | Ingests ops documents → Gemini extraction → **deterministic enrichment** → semantic search over incident history. Region-aware routing for SEV1/confidential alerts. |
| **Stack** | n8n · FastAPI · Gemini · Supabase / pgvector |
| **Highlights** | Cloud + local Docker · daily digest workflow · form intake → pipeline → email/Sheets |

<p align="center">
  <a href="https://github.com/reem-mor/hindsight"><img src="docs/screenshots/featured/hindsight-dashboard.png" alt="HINDSIGHT — pipeline dashboard" width="49%"/></a>
  <a href="https://github.com/reem-mor/hindsight"><img src="https://raw.githubusercontent.com/reem-mor/hindsight/main/docs/architecture.png" alt="HINDSIGHT — architecture" width="49%"/></a>
</p>

---

### 🤖 [course-assistant-bot](https://github.com/reem-mor/course-assistant-bot) — production Telegram bot · **224 tests**

<a href="https://github.com/reem-mor/course-assistant-bot"><img src="docs/screenshots/featured/course-bot-architecture.png" alt="course-assistant-bot — LangGraph router architecture" width="100%"/></a>

| | |
|---|---|
| **What it does** | Bilingual (HE/EN) Telegram course-ops: schedule, recordings, homework submission, RAG recommendations, admin FSM flows. **LLM classifies; code enforces rules.** |
| **Stack** | Python · uv · SQLAlchemy/Alembic · LangGraph · Docker · mypy strict |
| **Highlights** | Async PTB v21 · all externals mocked in CI · Alembic migrations · multi-LLM routing |

---

### ⚡ [Incident RAG (Bedrock)](projects/incident-rag-bedrock/) — AWS KB iteration · **111 tests**

<a href="projects/incident-rag-bedrock/"><img src="docs/screenshots/featured/bedrock-grounded-answer.png" alt="Bedrock KB — grounded answer with citations" width="100%"/></a>

| | |
|---|---|
| **What it does** | Same incident domain as IncidentIQ, using **managed Bedrock Knowledge Base** — stepping stone to PITER Agent. |
| **Stack** | Flask · Bedrock KB · React · EC2 |
| **Highlights** | RetrieveAndGenerate · refusal on low confidence · EC2 deployment evidence |

<p align="center">
  <a href="projects/incident-rag-bedrock/"><img src="projects/incident-rag-bedrock/screenshots/01_bedrock_kb_overview.png" alt="Bedrock KB overview" width="32%"/></a>
  <a href="projects/incident-rag-bedrock/"><img src="projects/incident-rag-bedrock/screenshots/09_app_refusal_or_low_confidence.png" alt="Bedrock refusal" width="32%"/></a>
  <a href="projects/incident-rag-bedrock/"><img src="projects/incident-rag-bedrock/screenshots/11_pytest_passed.png" alt="Bedrock pytest 111" width="32%"/></a>
</p>

**RAG progression (honest arc):**

```text
Track A (OpenAI + local FAISS):  L04 → L06 → hw04 → incident-assistant-rag (capstone)
Track B (AWS Bedrock):           L09 → incident-rag-bedrock → piter-aiops (flagship Agent)
```

Hero image sources: [`docs/screenshots/featured/`](docs/screenshots/featured/) · Regenerate: `node scripts/capture-featured-previews.mjs`

---

## Skills & competencies

| Domain | Skills | Evidence in this repo |
|--------|--------|----------------------|
| **RAG & retrieval** | Embeddings, FAISS, chunking, similarity thresholds, evaluation harness, source attribution | [IncidentIQ](projects/incident-assistant-rag/) · [Bedrock iteration](projects/incident-rag-bedrock/) |
| **LLM applications** | Grounded generation, refusal paths, prompt + tool design, multi-LLM routing | Capstone · [hw06 n8n agent](homework/hw06/n8n-customer-support-agent/) · [bot](https://github.com/reem-mor/course-assistant-bot) |
| **Agents & orchestration** | AWS Bedrock Agent, LangChain/LangGraph, n8n workflows, MCP tool servers | [PITER](https://github.com/reem-mor/piter-aiops) · L08–11 · [hw07 tools](homework/hw07/open-webui-tools/) |
| **Backend** | FastAPI, Flask, async Python, pydantic v2, REST APIs, OpenAPI | Capstone · lectures 05–06 · hw07 FastAPI server |
| **Frontend** | React, TypeScript, Vite, ops consoles | Capstone · [PITER frontend](https://github.com/reem-mor/piter-aiops) |
| **SRE & DevOps** | Docker Compose, EC2 labs, Nginx, health checks, CI/CD, secrets hygiene | [hw05](homework/hw05/nginx-docker-lab/) · [CI](.github/workflows/ci.yml) · `.env.example` |
| **Quality** | pytest (mocked externals), ruff, structured logging, idempotent scripts | **201+** in-repo tests · 4 CI matrices |
| **Agent dev tooling** | MCP server wiring, Cursor skills/rules, cross-tool AGENTS.md | [`.mcp.json`](.mcp.json) · [`docs/AGENT-TOOLING.md`](docs/AGENT-TOOLING.md) |

<details>
<summary><b>Technology stack</b> — full list</summary>

| Area | Technologies |
|------|--------------|
| Languages | Python 3.12 |
| Web | FastAPI, Flask, React, TypeScript, Vite |
| AI | OpenAI, FAISS, AWS Bedrock KB/Agent, LangChain, LangGraph, Ollama |
| Data | SQLite, Postgres, pgvector, Google Sheets (HINDSIGHT) |
| Ops | Docker, EC2, n8n, MCP, Kubernetes & Terraform (production day-job context) |
| Quality | ruff, pytest, GitHub Actions |

</details>

---

## Architecture

Colour-coded ecosystem — **curriculum → in-repo capstones → external flagships**:

<details open>
<summary><b>Portfolio ecosystem map</b> — interactive mermaid</summary>

```mermaid
flowchart TB
  subgraph archive["This repo — ai-engineering-portfolio"]
    L["lectures/ 01–11"]
    H["homework/ hw01–hw07"]
    CAP["incident-assistant-rag<br/>FastAPI · OpenAI · FAISS"]
    ITER["incident-rag-bedrock<br/>Bedrock KB iteration"]
  end
  subgraph external["flagships/ → standalone repos"]
    PITER["piter-aiops<br/>Bedrock Agent + tools"]
    HIND["hindsight<br/>n8n + Gemini pipeline"]
    BOT["course-assistant-bot<br/>Telegram HE/EN"]
  end
  L --> H --> CAP
  ITER -.->|evolved into| PITER
  H --> BOT
  CAP -.->|parallel track| PITER
  classDef archive fill:#11233a,stroke:#3b82f6,color:#cfe0ff
  classDef cap fill:#1e1430,stroke:#a855f7,color:#e6d6ff
  classDef ext fill:#2a2010,stroke:#f59e0b,color:#ffe6bf
  class L,H archive
  class CAP,ITER cap
  class PITER,HIND,BOT ext
```

</details>

| Layer | Location | Role |
|-------|----------|------|
| **Curriculum** | `lectures/`, `homework/`, `exercises/` | Authored notes + runnable demos |
| **Capstone** | `projects/incident-assistant-rag/` | Featured RAG app — 90 tests, evaluation harness |
| **Iteration** | `projects/incident-rag-bedrock/` | Bedrock KB stepping-stone → PITER |
| **Flagships** | `flagships/` | Pointers to external production repos |
| **Meta** | `docs/`, `AGENTS.md`, `.mcp.json` | Setup, syllabus, agent/MCP tooling |

Deep dive: [`docs/architecture/repository-architecture.md`](docs/architecture/repository-architecture.md)

### RAG evolution — two tracks

<details open>
<summary><b>Compare retrieval architectures</b> — mermaid</summary>

```mermaid
flowchart LR
  subgraph trackA [Track A — Local FAISS]
    A1[Upload PDF] --> A2[Chunk + embed]
    A2 --> A3[FAISS index]
    A3 --> A4[Similarity search]
    A4 --> A5{Above threshold?}
    A5 -->|yes| A6[OpenAI chat + sources]
    A5 -->|no| A7[Fixed refusal]
  end
  subgraph trackB [Track B — AWS Bedrock]
    B1[S3 corpus] --> B2[Bedrock KB sync]
    B2 --> B3[RetrieveAndGenerate]
    B3 --> B4{Confidence OK?}
    B4 -->|yes| B5[Grounded answer]
    B4 -->|no| B6[Refusal]
    B2 --> B7[Bedrock Agent + Lambda tools]
    B7 --> B8[PITER AiOps]
  end
  trackA --> CAP[incident-assistant-rag]
  trackB --> BED[incident-rag-bedrock]
  BED --> B8
```

</details>

<details>
<summary><b>Capstone request flow</b> — upload → index → grounded chat</summary>

```mermaid
sequenceDiagram
  autonumber
  participant U as Operator
  participant UI as React UI
  participant API as FastAPI
  participant IDX as FAISS index
  participant LLM as OpenAI

  U->>UI: Upload runbook PDF
  UI->>API: POST /documents
  API->>IDX: Chunk + embed + store
  U->>UI: Ask incident question
  UI->>API: POST /chat
  API->>IDX: Similarity search
  alt hits above threshold
    API->>LLM: Prompt + retrieved chunks
    LLM-->>API: Grounded answer
    API-->>UI: Answer + sources + scores
  else no context
    API-->>UI: Fixed refusal — no LLM call
  end
```

</details>

---

## Learning journey

<details open>
<summary><b>Four-stage colored flow</b> — lectures + homework → capstone → flagships</summary>

```mermaid
flowchart TB
  subgraph stage1 [Stage 1 Foundations]
    L01[L01 Jupyter Python]
    L02[L02 Python intro]
    L03[L03 OOP NumPy]
    HW01[hw01 Jupyter]
    HW02[hw02 Python scripts]
    HW03[hw03 Titanic CLI]
    L01 --> L02 --> L03
    L01 --> HW01
    L02 --> HW02
    L03 --> HW03
  end

  subgraph stage2 [Stage 2 RAG and Web]
    L04[L04 NLP FAISS RAG]
    L05[L05 Flask]
    L06[L06 Flask SQLite RAG]
    HW04[hw04 RAG app]
    L04 --> L05 --> L06
    L04 --> HW04
    L06 --> HW04
  end

  subgraph stage3 [Stage 3 Ops and Agents]
    L07[L07 Docker AWS]
    L08[L08 MCP]
    L09[L09 Bedrock n8n]
    L10[L10 LangChain LangGraph]
    L11[L11 Open WebUI]
    HW05[hw05 EC2 Nginx]
    HW06[hw06 n8n agent]
    HW07[hw07 Open WebUI tools]
    L07 --> HW05
    L09 --> HW06
    L08 --> L11
    L11 --> HW07
    L10 --> HW07
  end

  subgraph stage4 [Stage 4 Capstone and Flagships]
    CAP[incident-assistant-rag]
    BED[incident-rag-bedrock]
    PITER[piter-aiops external]
    HW04 -.-> CAP
    L06 -.-> CAP
    BED -.-> PITER
  end

  stage1 --> stage2 --> stage3 --> stage4

  classDef foundations fill:#11233a,stroke:#3b82f6,color:#cfe0ff
  classDef rag fill:#1a2e1a,stroke:#22c55e,color:#dcfce7
  classDef ops fill:#2a2010,stroke:#f59e0b,color:#ffe6bf
  classDef cap fill:#1e1430,stroke:#a855f7,color:#e6d6ff
  class L01,L02,L03,HW01,HW02,HW03 foundations
  class L04,L05,L06,HW04 rag
  class L07,L08,L09,L10,L11,HW05,HW06,HW07 ops
  class CAP,BED,PITER cap
```

Source: [`docs/diagrams/learning-path.mermaid`](docs/diagrams/learning-path.mermaid)

</details>

---

## Curriculum

Full map: [`docs/SYLLABUS.md`](docs/SYLLABUS.md) · [`lectures/README.md`](lectures/README.md) · [`homework/README.md`](homework/README.md)

<details>
<summary><b>Lectures 01–11</b> — topics & skills</summary>

| # | Topic | Path | Skills gained |
|---|-------|------|---------------|
| 01 | Jupyter & Python basics | `lectures/01_jupyter_python_basics/` | Python, notebooks |
| 02 | Python foundations | `lectures/02_python_intro/` | Functions, I/O, data structures |
| 03 | OOP & NumPy | `lectures/03_oop_numpy/` | Classes, arrays |
| 04 | NLP, embeddings, FAISS, RAG | `lectures/04_nlp_rag/` | Embeddings, vector search, RAG |
| 05 | Flask web development | `lectures/05_flask_intro/` | Flask, Docker |
| 06 | Flask + SQLite + RAG | `lectures/06_flask_advanced_rag/` | REST API, FAISS chat UI |
| 07 | Docker & AWS EC2 | `lectures/07_docker_aws/` | Containers, EC2, architecture diagrams |
| 08 | Model Context Protocol | `lectures/08_mcp/` | MCP stdio servers, tool-calling |
| 09 | Bedrock Flows & n8n | `lectures/09_flows_bedrock_n8n/` | Bedrock, workflow automation |
| 10 | LangChain & LangGraph | `lectures/10_langchain_langgraph/` | Agent memory, routing, graphs |
| 11 | Local models & Open WebUI | `lectures/11_local_models_webui/` | Ollama, local KB → hw07 |

</details>

<details>
<summary><b>Homework hw01–hw07</b> — assignments & evidence</summary>

| HW | Topic | Status | Evidence |
|----|-------|--------|----------|
| hw01 | Jupyter intro | Complete | Notebook |
| hw02 | Python foundations | Complete | Scripts + exercises |
| hw03 | OOP / Titanic CLI | Complete | pytest |
| hw04 | RAG web app | Scaffold — full impl in capstone | Docker scaffold |
| hw05 | EC2 / Docker / Nginx | Complete | [Screenshots](homework/hw05/nginx-docker-lab/screenshots/) |
| hw06 | n8n customer-support agent | Complete | [Workflow + guardrails](homework/hw06/n8n-customer-support-agent/) |
| hw07 | Open WebUI + MCP tools | Complete | [Screenshots](homework/hw07/screenshots/) · Playwright e2e |

</details>

---

## MCP & agent tooling

This repo is configured for **AI-assisted development** — MCP servers, Cursor skills, and cross-tool agent guidance (`AGENTS.md`).

<details open>
<summary><b>MCP ecosystem</b> — how agents connect to course tooling</summary>

```mermaid
flowchart LR
  subgraph ide [Agent IDEs]
    Cursor[Cursor]
    Claude[Claude Code]
  end
  subgraph mcp [MCP layer — .mcp.json]
    CT[course-tools]
    PW[playwright]
    KG[kaggle]
    AWK[aws-knowledge]
    AWA[aws-api]
    BKB[bedrock-kb]
    N8N[n8n-workflows]
    LOV[lovable]
  end
  subgraph use [Used for]
    L08[Lecture 08 demo]
    E2E[hw07 UI capture]
    DS[hw07 datasets]
    DOC[AWS docs Q&A]
    BR[Bedrock KB labs]
    HW6[hw06 workflows]
  end
  Cursor --> mcp
  Claude --> mcp
  CT --> L08
  PW --> E2E
  KG --> DS
  AWK --> DOC
  BKB --> BR
  N8N --> HW6
```

</details>

| Server | Use in this repo |
|--------|------------------|
| `course-tools` | Lecture 08 stdio MCP demo |
| `playwright` | E2E / UI capture (hw07) |
| `kaggle` | hw07 Netflix dataset |
| `aws-knowledge` | AWS documentation Q&A |
| `aws-api` | AWS API operations |
| `bedrock-kb` | Bedrock Knowledge Base retrieval |
| `n8n-workflows` | hw06 / lecture 09 automation |
| `lovable` | Optional UI experiments |

Bootstrap: [`docs/AGENT-TOOLING.md`](docs/AGENT-TOOLING.md) · [`scripts/setup-dev.ps1`](scripts/setup-dev.ps1) · [`.mcp.json`](.mcp.json)

---

## Evidence gallery

Detailed captures beyond the [featured heroes](#featured-work) above — homework labs, API surface, and test output.

### IncidentIQ — full walkthrough

| API (Swagger) | KB index | Grounded chat | Refusal (no context) |
|:---:|:---:|:---:|:---:|
| [![01](projects/incident-assistant-rag/screenshots/01_swagger_all_api_endpoints.png)](projects/incident-assistant-rag/screenshots/01_swagger_all_api_endpoints.png) | [![04](projects/incident-assistant-rag/screenshots/04_frontend_knowledge_base_index_success.png)](projects/incident-assistant-rag/screenshots/04_frontend_knowledge_base_index_success.png) | [![06](projects/incident-assistant-rag/screenshots/06_frontend_rag_chat_grounded.png)](projects/incident-assistant-rag/screenshots/06_frontend_rag_chat_grounded.png) | [![07](projects/incident-assistant-rag/screenshots/07_frontend_rag_chat_irrelevant.png)](projects/incident-assistant-rag/screenshots/07_frontend_rag_chat_irrelevant.png) |

| Tests (90) | Evaluation 5/5 |
|:---:|:---:|
| [![11](projects/incident-assistant-rag/screenshots/11_backend_tests_90_passed_pytest.png)](projects/incident-assistant-rag/screenshots/11_backend_tests_90_passed_pytest.png) | [![12](projects/incident-assistant-rag/screenshots/12_backend_evaluation_5_of_5.png)](projects/incident-assistant-rag/screenshots/12_backend_evaluation_5_of_5.png) |

Architecture: [`projects/incident-assistant-rag/docs/architecture.png`](projects/incident-assistant-rag/docs/architecture.png)

### Bedrock learning iteration

| KB overview | Grounded answer | Refusal / low confidence | pytest (111) |
|:---:|:---:|:---:|:---:|
| [![kb](projects/incident-rag-bedrock/screenshots/01_bedrock_kb_overview.png)](projects/incident-rag-bedrock/screenshots/01_bedrock_kb_overview.png) | [![answer](projects/incident-rag-bedrock/screenshots/08_app_question_and_answer.png)](projects/incident-rag-bedrock/screenshots/08_app_question_and_answer.png) | [![refusal](projects/incident-rag-bedrock/screenshots/09_app_refusal_or_low_confidence.png)](projects/incident-rag-bedrock/screenshots/09_app_refusal_or_low_confidence.png) | [![tests](projects/incident-rag-bedrock/screenshots/11_pytest_passed.png)](projects/incident-rag-bedrock/screenshots/11_pytest_passed.png) |

### Ops & agent homework

| hw05 EC2 + Docker + Nginx | hw06 n8n agent | hw07 Open WebUI KB | hw07 tool server |
|:---:|:---:|:---:|:---:|
| [![ec2](homework/hw05/nginx-docker-lab/screenshots/01-ec2-instance-and-security-group.png)](homework/hw05/nginx-docker-lab/screenshots/01-ec2-instance-and-security-group.png) | [![n8n](homework/hw06/n8n-customer-support-agent/screenshots/01_full_workflow.png)](homework/hw06/n8n-customer-support-agent/screenshots/01_full_workflow.png) | [![kb](homework/hw07/screenshots/03-kb-indexed.png)](homework/hw07/screenshots/03-kb-indexed.png) | [![tools](homework/hw07/screenshots/00-tool-server-openapi.png)](homework/hw07/screenshots/00-tool-server-openapi.png) |

### External flagships — more in each repo

[**PITER**](https://github.com/reem-mor/piter-aiops#see-it-working) · [**HINDSIGHT**](https://github.com/reem-mor/hindsight#-see-it-working) · [**course-assistant-bot**](https://github.com/reem-mor/course-assistant-bot#documentation)

Index: [`docs/screenshots/README.md`](docs/screenshots/README.md) · Hero captures: [`docs/screenshots/featured/`](docs/screenshots/featured/)

---

## Production engineering habits

Ops-minded patterns backed by repo evidence — not demo-only AI:

| Signal | Where |
|--------|-------|
| CI gate — ruff + **4 pytest matrices** | [`.github/workflows/ci.yml`](.github/workflows/ci.yml) |
| Health / deep checks | Capstone `/health` endpoints |
| No-context refusal (deterministic) | Capstone + Bedrock iteration |
| RAG evaluation harness | Capstone eval **5/5** |
| Docker Compose reproducibility | Capstone, hw07 |
| Secrets hygiene | [`.env.example`](.env.example), MCP `${env:VAR}` |
| Incident-domain corpus | Shared runbook samples across projects |
| EC2 / container ops lab | [`homework/hw05/nginx-docker-lab/`](homework/hw05/nginx-docker-lab/) |
| Guardrails in n8n agent | Input guardrails + agent prompt — [hw06](homework/hw06/n8n-customer-support-agent/) |

---

## Repository structure

```text
docs/  lectures/  homework/  exercises/  projects/  flagships/  resources/  scripts/
```

| Folder | Role |
|--------|------|
| `lectures/` | Lessons 01–11 — demos colocated with notes |
| `homework/` | Assignments hw01–07 — evidence colocated |
| `projects/` | In-repo capstone + Bedrock iteration |
| `flagships/` | Pointers → external production repos |
| `docs/` | Syllabus, setup, architecture, agent tooling |

Full map: [`docs/STRUCTURE.md`](docs/STRUCTURE.md) · Clean local clutter: `.\scripts\clean-workspace.ps1`

---

## Quick start

```bash
git clone https://github.com/reem-mor/ai-engineering-portfolio.git
cd ai-engineering-portfolio
python -m venv .venv && source .venv/bin/activate   # Windows: .\.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
```

**Capstone (Docker):**

```bash
cd projects/incident-assistant-rag && docker compose up --build
# → http://localhost:8080
```

**CI parity:**

```bash
cd projects/incident-assistant-rag/backend && pip install -r requirements.txt && pytest -q
cd projects/incident-rag-bedrock && pip install -r requirements.txt && pytest -q
cd lectures/10_langchain_langgraph && pip install -r requirements.txt && pytest -q
cd homework/hw07/open-webui-tools && pip install -r requirements.txt && pytest -q
ruff check .
```

Human setup: [`docs/setup.md`](docs/setup.md) · Agent bootstrap: [`scripts/setup-dev.ps1`](scripts/setup-dev.ps1)

---

## Documentation

| Doc | Contents |
|-----|----------|
| [`docs/README.md`](docs/README.md) | Documentation hub |
| [`docs/SYLLABUS.md`](docs/SYLLABUS.md) | Full curriculum map |
| [`docs/STRUCTURE.md`](docs/STRUCTURE.md) | Repository layout |
| [`flagships/README.md`](flagships/README.md) | External repo pointers + pin order |
| [`docs/AGENT-TOOLING.md`](docs/AGENT-TOOLING.md) | MCP, skills, CI matrix |
| [`docs/setup.md`](docs/setup.md) | Clone, venv, per-project deps |
| [`docs/portfolio/GITHUB_PROFILE_PLAYBOOK.md`](docs/portfolio/GITHUB_PROFILE_PLAYBOOK.md) | Profile README + GitHub pins |
| [`AGENTS.md`](AGENTS.md) | Cross-tool agent guidance |

---

## License

MIT for original code — [`LICENSE`](LICENSE). Course slides/handouts: [`resources/MANIFEST.md`](resources/MANIFEST.md) only (instructor IP — not redistributed).
