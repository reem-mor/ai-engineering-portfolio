# syntax=docker/dockerfile:1
# Multi-stage build: builder installs deps + bakes FAISS index; runtime is slim + non-root.

# ---- builder: compile deps, download embedding model, build knowledge base ----
FROM python:3.11-slim AS builder

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH" \
    HF_HOME=/app/.cache/huggingface \
    SENTENCE_TRANSFORMERS_HOME=/app/.cache/sentence-transformers \
    PIP_NO_CACHE_DIR=1

# CPU-only PyTorch first — avoids ~3GB of CUDA wheels from sentence-transformers
COPY requirements-prod.txt .
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu \
    && pip install --no-cache-dir -r requirements-prod.txt

COPY . .

# Placeholder satisfies pydantic-settings at build time; real key comes from .env at runtime
RUN OPENAI_API_KEY=build-time-placeholder-not-a-secret \
    python scripts/build_knowledge_base.py

# ---- runtime: no build tools, non-root user, baked index + model cache ----
FROM python:3.11-slim AS runtime

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && adduser --disabled-password --gecos "" appuser

WORKDIR /app

ENV PATH="/opt/venv/bin:$PATH" \
    HF_HOME=/app/.cache/huggingface \
    SENTENCE_TRANSFORMERS_HOME=/app/.cache/sentence-transformers \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8000

COPY --from=builder /opt/venv /opt/venv
COPY --from=builder /app /app

RUN chown -R appuser:appuser /app

USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=90s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
