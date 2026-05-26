# Demo Script

## 1. Start the Application

Run:

```bash
docker compose build
docker compose up
```

Open:

```text
http://localhost:3000
```

## 2. Show Knowledge Base

Explain that the app includes sample incident documents in MD, TXT, CSV, PDF, and DOCX formats. Click `Index Sample Documents`.

## 3. Show RAG Chat

Ask:

```text
What should I check when users cannot log in after deployment?
```

Explain that the app retrieves relevant chunks from FAISS and answers only from the retrieved context.

## 4. Show Incident Analysis

Use:

```text
Description: Many users cannot log in after the latest production deployment.
Affected service: auth-service
Environment: production
```

Show severity, likely causes, checks, missing information, next action, escalation, and sources.

## 5. Show Swagger

Open:

```text
http://localhost:8000/docs
```

Show the API endpoints.

## 6. Explain Architecture

Mention:

- React frontend
- FastAPI backend
- OpenAI embeddings and generation
- FAISS vector search
- Supabase metadata and history
- Docker Compose
