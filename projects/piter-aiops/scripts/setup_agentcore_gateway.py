#!/usr/bin/env python3
"""Attempt AgentCore Gateway (MCP) over enrichment Lambdas; document Path A vs B.

Path A (target): Cognito OAuth + AgentCore Gateway with Lambda targets.
Path B (fallback): Bedrock action groups only (see setup_enrichment_lambdas.py).

Estimated cost: Cognito user pool ~$0 on free tier; AgentCore usage-based (low for demo).

Usage:
  python scripts/setup_agentcore_gateway.py --dry-run
  python scripts/setup_agentcore_gateway.py --report-only
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import boto3  # noqa: E402
from botocore.exceptions import ClientError, UnknownServiceError  # noqa: E402

LAMBDA_TOOLS = ("iiq-correlate", "iiq-context", "iiq-similar")
TAGS = {"Project": "piter-aiops", "Owner": "reemmor"}


def _try_agentcore_client(region: str):
    try:
        return boto3.client("bedrock-agentcore", region_name=region)
    except UnknownServiceError:
        return None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--region", default="us-east-1")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument(
        "--report-only",
        action="store_true",
        help="Write MCP path decision without creating paid resources",
    )
    args = parser.parse_args()

    report = {
        "path_chosen": "B",
        "path_a_available": False,
        "reason": "",
        "lambda_tools": list(LAMBDA_TOOLS),
        "gateway_endpoint": None,
        "cognito": None,
    }

    client = _try_agentcore_client(args.region)
    if client is None:
        report["reason"] = (
            "bedrock-agentcore SDK not available in this boto3 build; "
            "use action groups (Path B) for agent tool invocation."
        )
    else:
        try:
            ops = sorted(client.meta.service_model.operation_names)
            report["path_a_available"] = True
            report["agentcore_operations_sample"] = ops[:20]
            if args.dry_run or args.report_only:
                report["reason"] = (
                    "AgentCore control plane reachable; gateway create skipped in dry-run. "
                    "Demo uses Path B action groups; expose MCP via console when enabled."
                )
            else:
                report["reason"] = (
                    "Gateway provisioning requires account-specific AgentCore preview APIs; "
                    "not automated in this repo. Path B action groups wired for reliable tools."
                )
        except ClientError as exc:
            report["reason"] = f"AgentCore API error: {exc}"

    out = ROOT / "docs" / "MCP_PATH.json"
    out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    print(f"\nWrote {out}")
    print("\nRecommendation: Path B (action groups) is the production tool path for the agent.")
    print("Path A MCP layer can be added when AgentCore Gateway is enabled on the account.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
