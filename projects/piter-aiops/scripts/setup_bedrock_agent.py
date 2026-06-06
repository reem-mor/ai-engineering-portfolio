#!/usr/bin/env python3
"""Provision a Bedrock Agent linked to the PITER AiOps Knowledge Base.

Creates agent, associates KB, prepares, and creates a 'live' alias.
Requires AWS credentials with bedrock-agent control-plane permissions.

Usage (from project root):
  python scripts/setup_bedrock_agent.py
  python scripts/setup_bedrock_agent.py --dry-run
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.bedrock_agent_client import AGENT_INSTRUCTION  # noqa: E402
from app.config import Config  # noqa: E402

import boto3  # noqa: E402


def _wait_prepared(agent_client, agent_id: str, *, timeout_s: int = 300) -> None:
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        resp = agent_client.get_agent(agentId=agent_id)
        status = resp["agent"]["agentStatus"]
        if status == "PREPARED":
            return
        if status == "FAILED":
            raise RuntimeError(f"Agent preparation failed: {resp['agent']}")
        time.sleep(5)
    raise TimeoutError(f"Agent {agent_id} not PREPARED within {timeout_s}s")


def main() -> int:
    parser = argparse.ArgumentParser(description="Create Bedrock Agent for PITER AiOps")
    parser.add_argument("--agent-name", default="PITER AiOps-noc-agent")
    parser.add_argument("--alias-name", default="live")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    cfg = Config.from_env()
    if args.dry_run:
        print("Dry run — would create agent with:")
        print(f"  region={cfg.AWS_REGION}")
        print(f"  kb_id={cfg.BEDROCK_KB_ID}")
        print(f"  model={cfg.BEDROCK_MODEL_ARN}")
        print(f"  num_results={cfg.BEDROCK_NUM_RESULTS}")
        return 0

    agent_ctrl = boto3.client("bedrock-agent", region_name=cfg.AWS_REGION)

    create_resp = agent_ctrl.create_agent(
        agentName=args.agent_name,
        foundationModel=cfg.BEDROCK_MODEL_ARN,
        instruction=AGENT_INSTRUCTION,
        description="PITER AiOps NOC triage agent backed by incident-ops KB",
        idleSessionTTLInSeconds=600,
    )
    agent_id = create_resp["agent"]["agentId"]
    print(f"Created agent: {agent_id}")

    agent_ctrl.associate_agent_knowledge_base(
        agentId=agent_id,
        agentVersion="DRAFT",
        knowledgeBaseId=cfg.BEDROCK_KB_ID,
        description="Incident runbooks and postmortems",
        knowledgeBaseState="ENABLED",
    )
    print(f"Associated KB: {cfg.BEDROCK_KB_ID}")

    agent_ctrl.prepare_agent(agentId=agent_id)
    print("Prepare started — waiting for PREPARED status...")
    _wait_prepared(agent_ctrl, agent_id)

    alias_resp = agent_ctrl.create_agent_alias(
        agentId=agent_id,
        agentAliasName=args.alias_name,
        description="Production alias for PITER AiOps Flask app",
    )
    alias_id = alias_resp["agentAlias"]["agentAliasId"]
    print(f"Created alias '{args.alias_name}': {alias_id}")
    print()
    print("Add to .env:")
    print(f"BEDROCK_AGENT_ID={agent_id}")
    print(f"BEDROCK_AGENT_ALIAS_ID={alias_id}")
    print("RAG_BACKEND=agent")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
