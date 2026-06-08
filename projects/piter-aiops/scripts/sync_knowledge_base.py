#!/usr/bin/env python3
"""Sync knowledge_base/ to S3 and start a Bedrock Knowledge Base ingestion job."""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import boto3  # noqa: E402

from app.config import Config  # noqa: E402

KB_ROOT = ROOT / "knowledge_base"


def sync_markdown_to_s3(cfg: Config) -> int:
    """Upload all knowledge_base/**/*.md under cfg.S3_PREFIX."""
    if not cfg.S3_BUCKET:
        print("S3_BUCKET is required to sync knowledge base documents")
        return 1
    prefix = cfg.S3_PREFIX.rstrip("/") + "/"
    if not KB_ROOT.is_dir():
        print(f"Missing knowledge base directory: {KB_ROOT}")
        return 1

    s3 = boto3.client("s3", region_name=cfg.AWS_REGION)
    uploaded = 0
    for path in sorted(KB_ROOT.rglob("*.md")):
        rel = path.relative_to(KB_ROOT).as_posix()
        key = f"{prefix}{rel}"
        s3.upload_file(str(path), cfg.S3_BUCKET, key)
        uploaded += 1
    print(f"Uploaded {uploaded} markdown files to s3://{cfg.S3_BUCKET}/{prefix}")
    return 0


def start_ingestion(cfg: Config, *, wait: bool) -> int:
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
    job_id = job["ingestionJobId"]
    status = job["status"]
    print(f"Started ingestion job {job_id} with status {status}")

    if not wait:
        return 0

    while status in {"STARTING", "IN_PROGRESS"}:
        time.sleep(5)
        detail = client.get_ingestion_job(
            knowledgeBaseId=cfg.BEDROCK_KB_ID,
            dataSourceId=cfg.BEDROCK_DATA_SOURCE_ID,
            ingestionJobId=job_id,
        )["ingestionJob"]
        status = detail["status"]
        print(f"Ingestion status: {status}")

    stats = client.get_ingestion_job(
        knowledgeBaseId=cfg.BEDROCK_KB_ID,
        dataSourceId=cfg.BEDROCK_DATA_SOURCE_ID,
        ingestionJobId=job_id,
    )["ingestionJob"].get("statistics", {})
    print(f"Ingestion statistics: {stats}")
    return 0 if status == "COMPLETE" else 1


def main() -> int:
    parser = argparse.ArgumentParser(description="Sync PITER knowledge_base to S3 and ingest")
    parser.add_argument(
        "--skip-upload",
        action="store_true",
        help="Only start ingestion (assume S3 already has current corpus)",
    )
    parser.add_argument(
        "--skip-ingest",
        action="store_true",
        help="Only upload markdown to S3",
    )
    parser.add_argument(
        "--wait",
        action="store_true",
        help="Poll until ingestion completes",
    )
    args = parser.parse_args()

    cfg = Config.from_env()
    if not args.skip_upload:
        code = sync_markdown_to_s3(cfg)
        if code != 0:
            return code
    if args.skip_ingest:
        return 0
    return start_ingestion(cfg, wait=args.wait)


if __name__ == "__main__":
    raise SystemExit(main())
