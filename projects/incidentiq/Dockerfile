FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONPATH=/app \
    PORT=8000

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy dependency metadata first for Docker layer caching.
COPY requirements.txt .

# CPU-only PyTorch keeps the image much smaller than CUDA wheels.
RUN python -m pip install --upgrade pip \
    && python -m pip install torch==2.11.0 --index-url https://download.pytorch.org/whl/cpu \
    && python -m pip install -r requirements.txt

COPY . .

# Build the FAISS index at image build time without embedding a real API key.
RUN OPENAI_API_KEY=build-time-placeholder-not-a-secret \
    python scripts/build_knowledge_base.py

RUN adduser --disabled-password --gecos "" appuser \
    && chown -R appuser:appuser /app
USER appuser

HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -fsS http://127.0.0.1:${PORT:-8000}/health || exit 1

EXPOSE 8000

# Bind 0.0.0.0 inside the container so host port mapping and Render routing work.
CMD ["sh", "-c", "python -m uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
