# Homework Submission Procedure

Source handout: `resources/handouts/homework_submission_procedure.docx` *(not yet in repo — add when available from course staff)*

The summary below covers the day-to-day workflow. For assignment requirements, see [`resources/handouts/`](resources/MANIFEST.md) and each homework folder README.

## Before You Start

- Pull the latest changes: `git pull`
- Activate your virtual environment: `.venv\Scripts\activate`
- Install any new dependencies: `pip install -r requirements.txt`

## Working on a Homework

1. Work inside the relevant folder: `homework/hw01/`, `homework/hw02/`, etc.
2. Read the `README.md` in that folder for the assignment questions.
3. Create your solution file(s) in the same folder — do **not** modify `README.md` unless instructed.

## Submitting

```bash
git add homework/hwXX/
git commit -m "hw0X: brief description of what you implemented"
git push
```

## Naming Conventions

| Artifact | Convention | Example |
|---|---|---|
| Homework folders | `hw0X/` | `hw04/` |
| Solution Python files | `snake_case.py` | `rag_app.py` |
| Solution notebooks | descriptive name | `titanic_ticket_purchasing_system.ipynb` |
| Data files | `snake_case` in `data/` subfolder | `hw03/data/titanic.csv` |

## General Rules

- Do not commit `.venv/`, `__pycache__/`, or `.env` files — these are covered by `.gitignore`.
- Do not commit large binary datasets — use `data/` folders and add oversized files to `.gitignore`.
- Commit messages should be concise and describe **what** you did, not that you "did homework".
