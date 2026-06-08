#!/usr/bin/env python3
"""Start Bedrock KB ingestion job and wait until COMPLETE."""
from __future__ import annotations

import sys
import time
from pathlib import Path

import boto3
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.config import Config  # noqa: E402


def main() -> int:
    load_dotenv(ROOT / ".env")
    cfg = Config.from_env()
    client = boto3.client("bedrock-agent", region_name=cfg.AWS_REGION)
    resp = client.start_ingestion_job(
        knowledgeBaseId=cfg.BEDROCK_KB_ID,
        dataSourceId=cfg.BEDROCK_DATA_SOURCE_ID,
        description="PITER corpus sync (sample_documents)",
    )
    job = resp["ingestionJob"]
    job_id = job["ingestionJobId"]
    print(f"Started ingestion job {job_id} status={job.get('status')}")

    deadline = time.time() + 900
    while time.time() < deadline:
        cur = client.get_ingestion_job(
            knowledgeBaseId=cfg.BEDROCK_KB_ID,
            dataSourceId=cfg.BEDROCK_DATA_SOURCE_ID,
            ingestionJobId=job_id,
        )["ingestionJob"]
        status = cur["status"]
        stats = cur.get("statistics") or {}
        print(
            f"  status={status} scanned={stats.get('numberOfDocumentsScanned')} "
            f"new={stats.get('numberOfNewDocumentsIndexed')} "
            f"modified={stats.get('numberOfModifiedDocumentsIndexed')} "
            f"failed={stats.get('numberOfDocumentsFailed')}"
        )
        if status in {"COMPLETE", "FAILED", "STOPPED"}:
            if status != "COMPLETE":
                print("FAIL:", cur.get("failureReasons"))
                return 1
            print("Ingestion COMPLETE")
            return 0
        time.sleep(15)

    print("TIMEOUT waiting for ingestion")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
