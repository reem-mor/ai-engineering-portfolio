# Architecture

IncidentIQ uses a clean full-stack architecture. The frontend is a React TypeScript application. The backend is a FastAPI API. The vector search layer is FAISS. Supabase Postgres is optional and is used only for metadata and history.

## Components

## React Frontend

The frontend provides four main pages:

- Knowledge Base
- RAG Chat
- Incident Analysis
- Upload

It shows loading states, validation errors, retrieved sources, confidence, and used-context status.

## FastAPI Backend

The backend owns all secrets and all AI calls. It exposes endpoints for upload, indexing, chat, incident analysis, and health checks.

## FAISS Vector Store

FAISS stores document embeddings and performs semantic similarity search. It is local, fast, and required for this course project.

## Supabase Postgres

Supabase stores application metadata such as documents, chat sessions, chat messages, retrieval logs, incident analyses, and evaluation results. It does not replace FAISS.

## Why This Design

The design separates responsibilities clearly:

- FAISS handles vector retrieval.
- Supabase handles metadata and history.
- FastAPI handles business logic and AI calls.
- React handles user interaction.
