# Amdocs AI Course

A hands-on Python & AI course covering Jupyter, OOP, NLP, RAG pipelines, Flask, and cloud deployment.

---

## Repository Structure

```
amdocs-ai-course/
├── README.md                        ← this file
├── CONTRIBUTING.md                  ← submission procedure and git workflow
├── requirements.txt                 ← full pinned dependency list
│
├── resources/                       ← canonical lecture slides (PDF)
│   ├── lecture01.pdf                ← Jupyter & Python Basics
│   ├── lecture02.pdf                ← Python Introduction
│   ├── lecture03.pdf                ← OOP & NumPy
│   ├── lecture04_flask_intro.pdf    ← Flask Introduction
│   ├── lecture05_flask_advanced.pdf ← Flask Advanced
│   ├── lecture06_docker_aws.pdf     ← Docker & AWS
│   └── project_guidelines.pptx     ← Final project brief
│
├── lectures/                        ← code, exercises, and study notes per lecture
│   ├── 01_jupyter_python_basics/
│   ├── 02_python_intro/
│   ├── 03_oop_numpy/
│   ├── 04_nlp_rag/                  ← NLP demos + full RAG CLI
│   │   ├── exercises/               ← tokenization & word vectors
│   │   ├── demos/                   ← NLTK, sentiment, GloVe, Gemini, FAISS
│   │   └── data/                    ← risk_analysis_report.txt (sample corpus)
│   ├── 05_flask_intro/              ← minimal Flask app with Jinja2 templates
│   ├── 06_flask_advanced_rag/       ← Flask REST API + SQLite + RAG web app
│   └── 07_docker_aws/
│
├── homework/
│   ├── hw01/                        ← Jupyter intro
│   ├── hw02/                        ← Python intro + advanced
│   ├── hw03/                        ← Titanic ticket CLI + pytest suite
│   │   └── data/titanic.csv
│   └── hw04/                        ← RAG application (starter scaffold provided)
│
└── projects/                        ← final project submissions
```

---

## Lecture Index

| # | Topic | Slides | Lecture Folder |
|---|-------|--------|----------------|
| 01 | Jupyter & Python Basics | [lecture01.pdf](resources/lecture01.pdf) | [01_jupyter_python_basics](lectures/01_jupyter_python_basics/) |
| 02 | Python Introduction | [lecture02.pdf](resources/lecture02.pdf) | [02_python_intro](lectures/02_python_intro/) |
| 03 | OOP & NumPy | [lecture03.pdf](resources/lecture03.pdf) | [03_oop_numpy](lectures/03_oop_numpy/) |
| 04 | NLP & RAG Pipeline | — | [04_nlp_rag](lectures/04_nlp_rag/) |
| 05 | Flask Introduction | [lecture04_flask_intro.pdf](resources/lecture04_flask_intro.pdf) | [05_flask_intro](lectures/05_flask_intro/) |
| 06 | Flask Advanced + RAG Web App | [lecture05_flask_advanced.pdf](resources/lecture05_flask_advanced.pdf) | [06_flask_advanced_rag](lectures/06_flask_advanced_rag/) |
| 07 | Docker & AWS | [lecture06_docker_aws.pdf](resources/lecture06_docker_aws.pdf) | [07_docker_aws](lectures/07_docker_aws/) |

Each lecture folder contains a **README.md** with:
- Topics covered
- Key concepts you must know (with code examples)
- Numbered exercises with expected output

---

## Homework Index

| HW | Topic | Folder |
|----|-------|--------|
| 01 | Jupyter notebook: Markdown, Python basics, matplotlib | [homework/hw01](homework/hw01/) |
| 02 | Python intro (lists, dicts, functions) + advanced (OOP, NumPy, recursion) | [homework/hw02](homework/hw02/) |
| 03 | Titanic ticket purchasing CLI + pytest suite | [homework/hw03](homework/hw03/) |
| 04 | RAG application — build your own from scratch | [homework/hw04](homework/hw04/) |

---

## Setup

### Clone and create a virtual environment

```bash
git clone <repo-url>
cd amdocs-ai-course

python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
```

### NLTK data (one-time download)

```bash
python -c "
import nltk
nltk.download('punkt')
nltk.download('punkt_tab')
nltk.download('stopwords')
nltk.download('wordnet')
nltk.download('omw-1.4')
nltk.download('averaged_perceptron_tagger_eng')
"
```

### API keys for NLP/RAG lectures

Create environment variables (or a `.env` file) before running the NLP demos or HW04:

```bash
export GEMINI_API_KEY="your-google-ai-studio-key"
export HF_TOKEN="your-huggingface-access-token"
```

- Gemini key: https://aistudio.google.com/
- HuggingFace token: https://huggingface.co/settings/tokens

### Run a lecture demo

```bash
# NLP demos
python lectures/04_nlp_rag/demos/nltk_basic.py
python lectures/04_nlp_rag/exercises/exercise_01_tokenization.py

# Flask intro
cd lectures/05_flask_intro && python app.py

# Flask advanced RAG web app
cd lectures/06_flask_advanced_rag
cp .env.example .env   # fill in your keys
python app.py
# Open http://127.0.0.1:5000/
```

### Run homework tests

```bash
cd homework/hw03
pytest test_titanic_ticket.py -v
```

---

## Submitting Homework

See [CONTRIBUTING.md](CONTRIBUTING.md) for the full submission procedure.

Quick summary:
1. Create a branch: `git checkout -b hw/NN-your-name`
2. Work inside `homework/hwNN/`
3. Push and open a Pull Request

---

## Final Project

See [projects/README.md](projects/README.md) and [resources/project_guidelines.pptx](resources/project_guidelines.pptx) for scope, deliverables, and grading criteria.
