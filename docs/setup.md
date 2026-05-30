# Setup Guide

## Prerequisites

- Python 3.12+
- Git
- Node.js 18+ (for React/Vite projects)
- Docker Desktop (optional, for container labs and capstone)
- AWS account (optional, for EC2/nginx homework lab)

## Clone and base environment

```powershell
git clone https://github.com/reem-mor/amdocs-ai-course.git
cd amdocs-ai-course
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

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
| `GEMINI_API_KEY` | Lecture 06 Flask RAG demo |
| `HF_TOKEN` | Hugging Face models in lecture demos |

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

Follow [`homework/hw05/nginx-docker-lab/README.md`](../homework/hw05/nginx-docker-lab/README.md) and the handout [`resources/handouts/ubuntu-ec2-docker-nginx-student-exercise.docx`](../resources/handouts/ubuntu-ec2-docker-nginx-student-exercise.docx).

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
| Docker build fails on hw04 | hw04 app code is still in progress — Dockerfile exists as a starter |
