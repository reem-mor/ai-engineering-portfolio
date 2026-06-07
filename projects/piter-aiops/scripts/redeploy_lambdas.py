"""Redeploy the EXISTING PITER AiOps action-group Lambdas (code only).

Packages each action_groups/iiq-* folder (handler + enrichment tools + data
files) and calls update_function_code on the already-existing function. It does
NOT create functions, roles, action groups, or any new infrastructure; if a
function is missing it is reported and skipped.

Run:  python scripts/redeploy_lambdas.py
"""
from __future__ import annotations

import io
import os
import sys
import zipfile
from pathlib import Path

import boto3
from botocore.exceptions import ClientError

ROOT = Path(__file__).resolve().parents[1]
REGION = os.environ.get("AWS_REGION", "us-east-1")

FUNCTIONS = ("iiq-correlate", "iiq-context", "iiq-similar")

_INCLUDE_SUFFIXES = {".py", ".csv", ".json"}
_EXCLUDE_DIRS = {"__pycache__", "events"}


def package(folder: str) -> bytes:
    ag_dir = ROOT / "action_groups" / folder
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for path in sorted(ag_dir.rglob("*")):
            if not path.is_file():
                continue
            if any(part in _EXCLUDE_DIRS for part in path.relative_to(ag_dir).parts):
                continue
            if path.suffix not in _INCLUDE_SUFFIXES:
                continue
            if path.name == "openapi_schema.yaml":
                continue
            arc = str(path.relative_to(ag_dir)).replace("\\", "/")
            zf.write(path, arcname=arc)
    return buf.getvalue()


def main() -> int:
    client = boto3.Session(region_name=REGION).client("lambda")
    failures = 0
    for fn in FUNCTIONS:
        try:
            client.get_function(FunctionName=fn)
        except ClientError as exc:
            if exc.response["Error"]["Code"] == "ResourceNotFoundException":
                print(f"[SKIP] {fn}: function does not exist (no new infra created)")
                failures += 1
                continue
            raise
        payload = package(fn)
        client.update_function_code(FunctionName=fn, ZipFile=payload)
        client.get_waiter("function_updated").wait(FunctionName=fn)
        cfg = client.get_function_configuration(FunctionName=fn)
        print(f"[OK]   {fn}: code updated ({len(payload):,} bytes), "
              f"state={cfg['State']} lastModified={cfg['LastModified']}")
    print("-" * 50)
    print(f"redeploy complete: {len(FUNCTIONS) - failures}/{len(FUNCTIONS)} functions updated")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
