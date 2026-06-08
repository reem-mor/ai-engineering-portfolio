#!/usr/bin/env python3
"""Start a Bedrock Knowledge Base ingestion job for the configured data source."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import boto3  # noqa: E402

from app.config import Config  # noqa: E402


def main() -> int:
    cfg = Config.from_env()
    if not cfg.BEDROCK_DATA_SOURCE_ID:
        print("BEDROCK_DATA_SOURCE_ID is required to start ingestion")
        return 1
    client = boto3.client("bedrock-agent", region_name=cfg.AWS_REGION)
    response = client.start_ingestion_job(
        knowledgeBaseId=cfg.BEDROCK_KB_ID,
        dataSourceId=cfg.BEDROCK_DATA_SOURCE_ID,
        description="PITER AiOps knowledge_base sync",
    )
    job = response["ingestionJob"]
    print(f"Started ingestion job {job['ingestionJobId']} with status {job['status']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
