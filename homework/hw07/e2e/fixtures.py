"""Prompts and validation hints for hw07 E2E."""

from __future__ import annotations

import sys
from pathlib import Path

_HW07_ROOT = Path(__file__).resolve().parent.parent
if str(_HW07_ROOT) not in sys.path:
    sys.path.insert(0, str(_HW07_ROOT))

from prompts import load_system_prompt

KB_COLLECTION_NAME = "ai-job-postings"
KB_DESCRIPTION = (
    "Data science & AI job postings (Kaggle) — titles, companies, locations for RAG chat"
)
TOOL_ID = "hw07_live_job_search"
TOOL_NAME = "HW07 Live Job Search"
CHAT_MODEL = "llama3.2:3b"
OLLAMA_PULL_MODEL = "llama3.2:3b"
EMBED_MODEL = "nomic-embed-text"

PROMPT_KB_SKILLS = (
    "Using the #ai-job-postings knowledge base only: "
    "list three data science or machine learning job titles from the CSV with one company or location each."
)

PROMPT_LIVE_JOBS = (
    "Use the search_live_jobs tool: what DevOps or AI engineer jobs "
    "are open in Israel right now? List employer names and job titles."
)

PROMPT_HYBRID_SKILLS_THEN_LIVE = (
    "Based on the #ai-job-postings knowledge base, what skills should I learn for AI roles? "
    "Then use search_live_jobs to find current openings in Israel for those skills."
)

PROMPT_HYBRID_COMPARE = (
    "Compare the uploaded job market data in #ai-job-postings with live AI Engineer jobs in Israel "
    "using search_live_jobs."
)

PROMPT_HYBRID_KB_AND_TOOL = (
    "Use the Knowledge Base for historical dataset insights and search_live_jobs for current listings: "
    "summarize top skills from the CSV, then search live Machine Learning Engineer jobs in Israel."
)

KB_ANSWER_HINTS = [
    r"Machine Learning Engineer|Data Scientist|Data Engineer",
    r"company|employer|location",
    r"Senior|Principal|Engineer",
]

TOOL_OPERATION_HINTS = [
    r"search_live_jobs",
    r"HW07 Live Job Search",
    r"Searching live jobs",
]

TOOL_ANSWER_HINTS = [
    r"Mock Tech IL|Senior AI Engineer",
    r"employer|job_title|Apply:",
    r"Israel|Tel Aviv|Herzliya",
    r"DevOps|AI Engineer|Machine Learning",
]

SYSTEM_PROMPT = load_system_prompt()

OPEN_WEBUI_EMAIL = "admin@localhost.com"
OPEN_WEBUI_PASSWORD = "admin"
