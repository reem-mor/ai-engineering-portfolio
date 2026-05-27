# Amdocs AI Course Portfolio

<p align="center">
  <strong>Hands-on AI-Augmented Software Engineering portfolio covering Python, RAG, FastAPI, React, Docker, AWS, testing, and production-minded project delivery.</strong>
</p>

<p align="center">
  <a href="#featured-project">Featured Project</a> |
  <a href="#repository-map">Repository Map</a> |
  <a href="#learning-path">Learning Path</a> |
  <a href="#homework-index">Homework</a> |
  <a href="#quick-start">Quick Start</a> |
  <a href="#quality-and-security">Quality</a>
</p>

<p align="center">
  <img alt="Python" src="https://img.shields.io/badge/Python-3.12+-blue">
  <img alt="FastAPI" src="https://img.shields.io/badge/FastAPI-Backend-009688">
  <img alt="React" src="https://img.shields.io/badge/React-Frontend-61DAFB">
  <img alt="RAG" src="https://img.shields.io/badge/RAG-FAISS%20%2B%20LLM-purple">
  <img alt="Docker" src="https://img.shields.io/badge/Docker-Ready-2496ED">
  <img alt="Status" src="https://img.shields.io/badge/Status-Active%20Portfolio-success">
</p>

---

## Overview

This repository documents my work during the **Amdocs AI Engineer / AI-Augmented Software Engineering course**. It includes lecture practice, homework assignments, Python fundamentals, NLP/RAG experiments, backend development, Docker/AWS exercises, and full-stack AI application projects.

The repository is organized as a learning and portfolio workspace. Each area is designed to show not only completed exercises, but also engineering decisions, documentation, testing, and practical delivery.

---

## Featured Project

### IncidentIQ - Full-Stack Incident Assistant RAG Application

[IncidentIQ](projects/incident-assistant-rag/) is the main portfolio project in this repository. It is a full-stack Retrieval-Augmented Generation application for **technical incident operations**.

It helps NOC, DevOps, Support, and Data Services teams query operational runbooks and incident documents while keeping answers grounded in the knowledge base.

| Area | Implementation |
|------|----------------|
| Domain | Technical incident operations, runbooks, escalation, alert triage |
| Backend | FastAPI, Pydantic, OpenAI API, FAISS, pytest |
| Frontend | React, TypeScript, Vite, operations-style UI |
| RAG | Document ingestion, chunking, embeddings, FAISS retrieval, grounded prompting |
| Guardrails | Similarity threshold, no-context refusal, visible sources, confidence fields |
| Delivery | Docker Compose, screenshots, evaluation flow, documentation |

**Project links**

- [IncidentIQ README](projects/incident-assistant-rag/README.md)
- [Architecture documentation](projects/incident-assistant-rag/docs/architecture.md)
- [RAG pipeline documentation](projects/incident-assistant-rag/docs/rag_pipeline.md)
- [Testing plan](projects/incident-assistant-rag/docs/testing_plan.md)
- [Reflection](projects/incident-assistant-rag/docs/reflection.md)
- [Demo script](projects/incident-assistant-rag/docs/demo_script.md)

---

## Repository Architecture

```mermaid
flowchart TB
  Repo[amdocs-ai-course]

  Repo --> Resources[resources]
  Repo --> Lectures[lectures]
  Repo --> Homework[homework]
  Repo --> Projects[projects]
  Repo --> Docs[CONTRIBUTING.md]

  Resources --> Slides[Course slides and handouts]

  Lectures --> L01[01 Jupyter and Python basics]
  Lectures --> L02[02 Python intro]
  Lectures --> L03[03 OOP and NumPy]
  Lectures --> L04[04 NLP and RAG]
  Lectures --> L05[05 Flask intro]
  Lectures --> L06[06 Flask advanced RAG]
  Lectures --> L07[07 Docker and AWS]

  Homework --> HW01[HW01 Notebook basics]
  Homework --> HW02[HW02 Python exercises]
  Homework --> HW03[HW03 Titanic CLI and tests]
  Homework --> HW04[HW04 RAG application]

  Projects --> IncidentIQ[IncidentIQ full-stack RAG]
  IncidentIQ --> Backend[FastAPI backend]
  IncidentIQ --> Frontend[React frontend]
  IncidentIQ --> Vector[FAISS vector index]
  IncidentIQ --> Docker[Docker Compose]
  IncidentIQ --> Tests[Pytest and evaluation]
```

---

## Repository Map

```text
amdocs-ai-course/
├── README.md
├── CONTRIBUTING.md
├── requirements.txt
│
├── resources/
│   ├── lecture01.pdf
│   ├── lecture02.pdf
│   ├── lecture03.pdf
│   ├── lecture04_flask_intro.pdf
│   ├── lecture05_flask_advanced.pdf
│   ├── lecture06_docker_aws.pdf
│   └── project_guidelines.pptx
│
├── lectures/
│   ├── 01_jupyter_python_basics/
│   ├── 02_python_intro/
│   ├── 03_oop_numpy/
│   ├── 04_nlp_rag/
│   ├── 05_flask_intro/
│   ├── 06_flask_advanced_rag/
│   └── 07_docker_aws/
│
├── homework/
│   ├── hw01/
│   ├── hw02/
│   ├── hw03/
│   └── hw04/
│
└── projects/
    ├── README.md
    ├── incident-assistant-rag/
    └── incidentiq/
```

---

## Learning Path

| Stage | Focus | Main Skills |
|-------|-------|-------------|
| 01 | Jupyter and Python basics | Markdown, notebooks, variables, control flow |
| 02 | Python foundations | Lists, dictionaries, functions, validation, clean code |
| 03 | OOP and NumPy | Classes, reusable logic, arrays, vector operations |
| 04 | NLP and RAG | Tokenization, embeddings, semantic search, FAISS, LLM APIs |
| 05 | Flask intro | Routes, templates, basic web applications |
| 06 | Advanced web and RAG | REST APIs, SQLite, RAG web app patterns |
| 07 | Docker and AWS | Containers, deployment basics, EC2, Nginx, cloud workflow |
| Project | Full-stack AI system | FastAPI, React, RAG, Docker, testing, documentation |

---

## Homework Index

| HW | Topic | Folder | Main Value |
|----|-------|--------|------------|
| 01 | Jupyter notebook basics | [homework/hw01](homework/hw01/) | Markdown, notebook formatting, Python basics |
| 02 | Python exercises | [homework/hw02](homework/hw02/) | Functions, data structures, NumPy, recursion |
| 03 | Titanic ticket system | [homework/hw03](homework/hw03/) | Input validation, CLI flow, testing mindset |
| 04 | RAG application | [homework/hw04](homework/hw04/) | Retrieval, generation, app structure, AI workflow |

---

## Project Index

| Project | Folder | Description |
|---------|--------|-------------|
| IncidentIQ - Incident Assistant RAG | [projects/incident-assistant-rag](projects/incident-assistant-rag/) | Full-stack RAG application for technical incident operations with React, FastAPI, FAISS, OpenAI, Docker, tests, and evaluation |
| IncidentIQ prototype | [projects/incidentiq](projects/incidentiq/) | Earlier incident assistant implementation and experimentation workspace |

---

## Main Project Architecture - IncidentIQ

```mermaid
flowchart LR
  Engineer[Engineer asks incident question]
  UI[React Operations UI]
  API[FastAPI Backend]
  Ingestion[Document Ingestion]
  FAISS[(FAISS Vector Index)]
  RAG[RAG Pipeline]
  Guardrails[Grounding Controls]
  LLM[OpenAI Model]
  Answer[Answer with Sources]

  Engineer --> UI
  UI --> API
  API --> Ingestion
  Ingestion --> FAISS
  API --> RAG
  RAG --> FAISS
  RAG --> Guardrails
  Guardrails -->|Relevant context| LLM
  Guardrails -->|No context| Answer
  LLM --> Answer
  Answer --> UI
```

---

## Quality and Security

This repository is written with portfolio-level engineering habits:

- Clear project structure and documentation.
- Separate lecture, homework, and project workspaces.
- Environment variables for API keys and secrets.
- `.env` files are excluded from git.
- Project-specific README files explain setup and usage.
- Tests are included where relevant, especially for Python validation and RAG flows.
- Docker is used for full-stack project delivery.
- The RAG project includes hallucination controls, no-context behavior, source transparency, and evaluation questions.

---

## Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/reem-mor/amdocs-ai-course.git
cd amdocs-ai-course
```

### 2. Create a Python virtual environment

```bash
python -m venv .venv
```

Windows:

```powershell
.\.venv\Scripts\Activate.ps1
```

macOS / Linux:

```bash
source .venv/bin/activate
```

### 3. Install root dependencies

```bash
pip install -r requirements.txt
```

### 4. Optional NLTK setup

Some NLP lectures require local NLTK resources:

```bash
python -c "import nltk; nltk.download('punkt'); nltk.download('punkt_tab'); nltk.download('stopwords'); nltk.download('wordnet'); nltk.download('omw-1.4'); nltk.download('averaged_perceptron_tagger_eng')"
```

### 5. Run the main RAG project

```bash
cd projects/incident-assistant-rag
```

Then follow the project-specific setup instructions in:

[projects/incident-assistant-rag/README.md](projects/incident-assistant-rag/README.md)

---

## Common Commands

### Run Python tests for HW03

```bash
cd homework/hw03
pytest -v
```

### Run NLP/RAG lecture demos

```bash
python lectures/04_nlp_rag/demos/nltk_basic.py
python lectures/04_nlp_rag/exercises/exercise_01_tokenization.py
```

### Run Flask intro demo

```bash
cd lectures/05_flask_intro
python app.py
```

### Run advanced Flask RAG demo

```bash
cd lectures/06_flask_advanced_rag
cp .env.example .env
python app.py
```

---

## Environment Variables

Create local `.env` files only where needed. Do not commit secrets.

Typical variables used across the AI/RAG exercises:

```env
GEMINI_API_KEY=your-google-ai-studio-key
HF_TOKEN=your-huggingface-token
OPENAI_API_KEY=your-openai-key
```

For the main IncidentIQ project, use the project-specific `.env.example` files in `projects/incident-assistant-rag/`.

---

## Submission Workflow

See [CONTRIBUTING.md](CONTRIBUTING.md) for the full submission process.

Recommended workflow:

```bash
git checkout -b docs/readme-refresh
git status
git add .
git commit -m "docs: improve course portfolio README"
git push
```

---

## What This Repository Demonstrates

- Python programming fundamentals.
- Clean validation and CLI application structure.
- OOP, NumPy, and practical data handling.
- NLP and RAG foundations.
- FAISS-based semantic search.
- Backend API development.
- Full-stack AI application delivery.
- Dockerized local deployment.
- Testing, evaluation, documentation, and presentation.
- Practical thinking for NOC, DevOps, and incident operations use cases.

---

## Future Improvements

- Add GitHub Actions for automated tests.
- Add a root-level project gallery with screenshots.
- Add consistent README templates across all homework folders.
- Add architecture diagrams for more lecture demos.
- Add cloud deployment notes for AWS labs and full-stack projects.
- Add a portfolio landing page for finished projects.

---

## License and Usage

This repository is used for course learning, homework submissions, and portfolio demonstration. Do not commit private keys, production credentials, or sensitive data.
