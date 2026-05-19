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
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Pre-build the FAISS knowledge base inside the image
# This means the index is baked in — no runtime build needed
# OPENAI_API_KEY is injected inline (single-RUN scope only) to satisfy
# Pydantic Settings validation. The embedder uses sentence-transformers,
# not OpenAI — so this placeholder never reaches a real API call.
# It is NOT persisted as an image ENV layer; the real key is supplied
# at runtime via --env-file.
RUN OPENAI_API_KEY=build-time-placeholder-not-a-secret \
    python scripts/build_knowledge_base.py

# Expose application port
EXPOSE 8000

# Docker health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Never run as root in production
RUN adduser --disabled-password --gecos "" appuser
USER appuser

# Environment defaults (secrets passed at runtime via --env-file)
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8000

# Launch application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
