"""
Pinecone index setup + batched upsert for PITER RAG.
Matches your Bedrock KB config: Titan Text Embeddings V2 (1024-dim, cosine), us-east-1.

Install:  pip install pinecone boto3
Env:      export PINECONE_API_KEY=...   (never hardcode)
          AWS creds via your 'reemmor' profile (boto3 picks it up)
"""

import os
import json
import time
import hashlib
from typing import Iterable

import boto3
from pinecone import Pinecone, ServerlessSpec

# ---------------------------------------------------------------------------
# Config — tweak names/namespaces here only
# ---------------------------------------------------------------------------
INDEX_NAME = "piter-kb-prod"
DIMENSION = 1024                 # Titan Text Embeddings V2
METRIC = "cosine"               # normalized text embeddings
CLOUD = "aws"
REGION = "us-east-1"            # colocate with your Bedrock stack
EMBED_MODEL_ID = "amazon.titan-embed-text-v2:0"
AWS_PROFILE = "reemmor"
AWS_REGION = "us-east-1"
BATCH_SIZE = 100               # Pinecone-recommended upsert batch size

# Metadata fields you'll actually filter on. Keep this lean.
# (Pinecone serverless indexes all metadata by default; declaring intent here
#  keeps your ingestion disciplined.)
FILTERABLE_FIELDS = ["source", "doc_id", "service_owner", "timestamp"]


# ---------------------------------------------------------------------------
# Clients
# ---------------------------------------------------------------------------
pc = Pinecone(api_key=os.environ["PINECONE_API_KEY"])
session = boto3.Session(profile_name=AWS_PROFILE, region_name=AWS_REGION)
bedrock = session.client("bedrock-runtime")


# ---------------------------------------------------------------------------
# Index creation (idempotent)
# ---------------------------------------------------------------------------
def ensure_index() -> None:
    existing = [i["name"] for i in pc.list_indexes()]
    if INDEX_NAME in existing:
        print(f"[skip] index '{INDEX_NAME}' already exists")
        return

    print(f"[create] {INDEX_NAME}  dim={DIMENSION}  metric={METRIC}  {CLOUD}/{REGION}")
    pc.create_index(
        name=INDEX_NAME,
        dimension=DIMENSION,
        metric=METRIC,
        spec=ServerlessSpec(cloud=CLOUD, region=REGION),
    )
    # wait until ready
    while not pc.describe_index(INDEX_NAME).status["ready"]:
        time.sleep(1)
    print("[ready] index is up")


# ---------------------------------------------------------------------------
# Embedding via Titan V2 (same model as your Bedrock KB → consistent vectors)
# ---------------------------------------------------------------------------
def embed(text: str) -> list[float]:
    resp = bedrock.invoke_model(
        modelId=EMBED_MODEL_ID,
        body=json.dumps({"inputText": text, "dimensions": DIMENSION, "normalize": True}),
    )
    return json.loads(resp["body"].read())["embedding"]


# ---------------------------------------------------------------------------
# Deterministic IDs → re-ingestion is idempotent (same chunk = same ID)
# ---------------------------------------------------------------------------
def chunk_id(source: str, text: str) -> str:
    return hashlib.sha256(f"{source}::{text}".encode()).hexdigest()[:32]


def batched(iterable: Iterable, n: int):
    batch = []
    for item in iterable:
        batch.append(item)
        if len(batch) == n:
            yield batch
            batch = []
    if batch:
        yield batch


# ---------------------------------------------------------------------------
# Upsert
# ---------------------------------------------------------------------------
def upsert_chunks(chunks: list[dict], namespace: str = "default") -> None:
    """
    chunks: [{ "text": str, "source": str, "metadata": {...optional...} }, ...]
    Stores chunk text in metadata so retrieval returns usable context.
    """
    index = pc.Index(INDEX_NAME)
    total = 0

    for batch in batched(chunks, BATCH_SIZE):
        vectors = []
        for c in batch:
            meta = {k: v for k, v in c.get("metadata", {}).items()}
            meta["source"] = c["source"]
            meta["text"] = c["text"]          # keep text for context return
            vectors.append({
                "id": chunk_id(c["source"], c["text"]),
                "values": embed(c["text"]),
                "metadata": meta,
            })
        index.upsert(vectors=vectors, namespace=namespace)
        total += len(vectors)
        print(f"[upsert] +{len(vectors)}  (total {total})  ns={namespace}")

    print(f"[done] {total} vectors upserted into '{namespace}'")


# ---------------------------------------------------------------------------
# Example query
# ---------------------------------------------------------------------------
def query(text: str, namespace: str = "default", top_k: int = 5, flt: dict | None = None):
    index = pc.Index(INDEX_NAME)
    res = index.query(
        vector=embed(text),
        top_k=top_k,
        namespace=namespace,
        include_metadata=True,
        filter=flt,           # e.g. {"source": {"$eq": "runbooks"}}
    )
    for m in res["matches"]:
        print(f"{m['score']:.3f}  {m['metadata'].get('source')}  {m['metadata'].get('text','')[:80]}")
    return res


if __name__ == "__main__":
    ensure_index()

    # --- demo ingestion (replace with your real chunks) ---
    sample = [
        {"text": "wallet-service v4.12.3 introduced replication lag on primary DB.",
         "source": "past_incidents",
         "metadata": {"doc_id": "INC-2041", "service_owner": "payments", "timestamp": "2026-05-30"}},
        {"text": "Escalation policy: replication lag > 5min pages the on-call DBA.",
         "source": "escalation_policies",
         "metadata": {"doc_id": "ESC-07", "service_owner": "platform"}},
    ]
    upsert_chunks(sample, namespace="incidents")
    print("\n--- query ---")
    query("database replication lag after deploy", namespace="incidents")