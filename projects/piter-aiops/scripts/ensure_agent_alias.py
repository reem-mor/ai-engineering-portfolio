#!/usr/bin/env python3
"""Ensure agent has alias 'live' pointing at prepared version; sync instruction."""
from __future__ import annotations

import argparse
import os
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.bedrock_agent_client import AGENT_INSTRUCTION  # noqa: E402
from dotenv import load_dotenv  # noqa: E402

import boto3  # noqa: E402
from botocore.exceptions import ClientError  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent-id", required=True)
    parser.add_argument("--alias-name", default="live")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    load_dotenv(ROOT / ".env")
    region = __import__("os").environ.get("AWS_REGION", "us-east-1")
    client = boto3.client("bedrock-agent", region_name=region)

    agent = client.get_agent(agentId=args.agent_id)["agent"]
    if args.dry_run:
        print(f"Would sync instruction on {args.agent_id}")
        return 0

    client.update_agent(
        agentId=args.agent_id,
        agentName=agent["agentName"],
        agentResourceRoleArn=agent["agentResourceRoleArn"],
        foundationModel=os.environ.get("PITER_BEDROCK_AGENT_MODEL")
        or os.environ.get("PITER_BEDROCK_MODEL_ARN")
        or agent["foundationModel"],
        instruction=AGENT_INSTRUCTION,
    )
    print("Updated agent instruction from AGENT_INSTRUCTION")

    client.prepare_agent(agentId=args.agent_id)
    deadline = time.time() + 300
    while time.time() < deadline:
        status = client.get_agent(agentId=args.agent_id)["agent"]["agentStatus"]
        if status == "PREPARED":
            break
        if status == "FAILED":
            raise RuntimeError("prepare_agent failed")
        time.sleep(5)
    print("Agent PREPARED")

    aliases = client.list_agent_aliases(agentId=args.agent_id).get("agentAliasSummaries", [])
    existing = next((a for a in aliases if a.get("agentAliasName") == args.alias_name), None)
    if existing:
        print(f"Alias '{args.alias_name}' exists: {existing['agentAliasId']}")
        print(f"BEDROCK_AGENT_ALIAS_ID={existing['agentAliasId']}")
        return 0

    try:
        resp = client.create_agent_alias(
            agentId=args.agent_id,
            agentAliasName=args.alias_name,
            description="Production alias for PITER AiOps Flask app",
        )
        alias_id = resp["agentAlias"]["agentAliasId"]
        print(f"Created alias '{args.alias_name}': {alias_id}")
        print(f"BEDROCK_AGENT_ALIAS_ID={alias_id}")
    except ClientError as exc:
        print(f"create_agent_alias failed: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
