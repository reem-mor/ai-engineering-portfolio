"""Prompts and validation hints for hw07 E2E."""

from __future__ import annotations

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

SYSTEM_PROMPT = """You are an AI career assistant for homework 07.

Rules:
1. For questions about job titles, companies, or locations in the uploaded Kaggle job-postings CSV, use the #ai-job-postings knowledge base only. Cite specific titles or employers from retrieved chunks.
2. For current/live hiring (open roles, employers hiring now, today's listings), call the search_live_jobs tool with clear role keywords and location (default Israel).
3. Do not invent employers or job titles. If the KB has no match, say so. If the tool returns no listings, say so.
4. Keep answers concise and structured (bullets or numbered lists)."""

OPEN_WEBUI_EMAIL = "admin@localhost.com"
OPEN_WEBUI_PASSWORD = "admin"
