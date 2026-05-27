# Incident Assistant — frontend

## Build

```bash
npm install
npm run build
```

Uses **`tsc --noEmit`** then **`vite build`**. Backend CORS allows `http://localhost:5173` and `http://127.0.0.1:5173` (see FastAPI middleware). Prefer opening the dev UI at **http://localhost:5173**.

Copy [`.env.example`](.env.example) to `.env` if your API base URL is not `http://localhost:8000/api`.

## Dev

```bash
npm run dev
```
