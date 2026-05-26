# Incident Assistant — frontend

## Build

```bash
npm install
npm run build
```

Uses **`tsc --noEmit`** then **`vite build`**. Backend must expose CORS for `http://localhost:5173` (already in FastAPI middleware).

Copy [`.env.example`](.env.example) to `.env` if your API base URL is not `http://localhost:8000/api`.

## Dev

```bash
npm run dev
```
