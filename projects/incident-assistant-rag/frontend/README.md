# Incident Assistant — Frontend

React + TypeScript + Vite UI for IncidentIQ. **Full setup:** [`../docs/setup.md`](../docs/setup.md)

## Dev

```bash
npm install
npm run dev
```

Open http://localhost:5173. Index sample documents under **Knowledge Base** before using RAG Chat.

## Build

```bash
npm run build
```

Runs `tsc --noEmit` then `vite build`. Backend CORS allows `http://localhost:5173` and `http://127.0.0.1:5173`.

## Environment

Copy [`.env.example`](.env.example) to `.env` only if your API base URL is not `http://localhost:8000/api`.

**OpenAI keys and models stay in the backend** (see [`../backend/.env.example`](../backend/.env.example)) — the frontend never calls OpenAI directly.

## Docker

The production image uses `VITE_API_BASE_URL=/api` with nginx proxying to the backend (see root `docker-compose.yml`).
