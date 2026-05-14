# Homework 4 — RAG Application

## Overview

Build a Retrieval-Augmented Generation (RAG) application that ingests a document corpus, indexes it into a vector store, and answers natural-language queries using a language model backed by retrieved context.

## Deliverables

- `rag_app.py` — main application entry point (starter scaffold provided)
- `README.md` — this file, updated with your implementation notes

## Reference Implementation

Study `lectures/06_flask_advanced_rag/` for a complete production-quality RAG web app.
The `lectures/04_nlp_rag/demos/rag_example.py` CLI script is the simpler starting point.

## Getting Started

Key packages already available in the project `requirements.txt`:

- `faiss-cpu` — vector index
- `huggingface_hub` — HuggingFace cloud embeddings (`InferenceClient`)
- `google-genai` — Gemini LLM
- `nltk` — sentence tokenization for chunking

## Suggested Data Source

Use `lectures/04_nlp_rag/data/risk_analysis_report.txt` as your test corpus.
It is structured, domain-specific, and small enough to iterate quickly.

## Required Environment Variables

```bash
export GEMINI_API_KEY="your-google-ai-studio-key"
export HF_TOKEN="your-huggingface-token"
```
