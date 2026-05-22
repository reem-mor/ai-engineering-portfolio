FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Layer caching: copy requirements first, install before code
COPY requirements.txt .

# CPU-only PyTorch keeps the image much smaller than CUDA wheels
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu \
    && pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Pre-build the FAISS knowledge base inside the image
RUN OPENAI_API_KEY=build-time-placeholder-not-a-secret \
    python scripts/build_knowledge_base.py

# Expose application port
EXPOSE 8000

# Docker health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -fsS http://127.0.0.1:${PORT:-8000}/health || exit 1

# Never run as root in production
RUN adduser --disabled-password --gecos "" appuser
USER appuser

# Environment defaults
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8000

# Launch application
# Bind 0.0.0.0 inside the container so host port mapping (127.0.0.1:8000→8000) works.
# HEALTHCHECK above uses 127.0.0.1 (in-container loopback). Do not bind uvicorn to
# 127.0.0.0 only — that would reject traffic from the Docker bridge network.
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
