"""Update an existing Bedrock KB RAG flow, publish a new version, and repoint the alias."""

from __future__ import annotations

import json
import logging
import os
import sys
from pathlib import Path

import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger(__name__)

LESSON_ROOT = Path(__file__).resolve().parent.parent
DEFINITION_PATH = Path(__file__).resolve().parent / "flow_kb_definition.json"
FLOW_NAME = "reem-orders-kb-flow"


def _load_config() -> dict[str, str]:
    load_dotenv(LESSON_ROOT / ".env")
    flow_id = os.getenv("BEDROCK_KB_FLOW_ID", "")
    alias_id = os.getenv("BEDROCK_KB_FLOW_ALIAS_ID", "")
    region = os.getenv("AWS_REGION", "us-east-1")
    profile = os.getenv("AWS_PROFILE")
    role_arn = os.getenv("BEDROCK_KB_FLOWS_EXECUTION_ROLE_ARN", "")
    model_id = os.getenv("BEDROCK_MODEL_ID", "amazon.nova-lite-v1:0")
    kb_id = os.getenv("BEDROCK_KB_ID", "KCYCNC0OSD")

    if not flow_id or not alias_id:
        logger.error(
            "Set BEDROCK_KB_FLOW_ID and BEDROCK_KB_FLOW_ALIAS_ID in .env "
            "(run create_kb_flow.py first)"
        )
        sys.exit(1)

    if not role_arn or "123456789012" in role_arn:
        logger.error(
            "Set BEDROCK_KB_FLOWS_EXECUTION_ROLE_ARN in lectures/09_flows_bedrock_n8n/.env"
        )
        sys.exit(1)

    return {
        "flow_id": flow_id,
        "alias_id": alias_id,
        "region": region,
        "profile": profile or "",
        "role_arn": role_arn,
        "model_id": model_id,
        "kb_id": kb_id,
    }


def _bedrock_agent_client(region: str, profile: str | None) -> object:
    session_kwargs: dict[str, str] = {"region_name": region}
    if profile:
        session_kwargs["profile_name"] = profile
    session = boto3.Session(**session_kwargs)
    return session.client("bedrock-agent")


def _apply_flow_config(definition: dict, *, kb_id: str, model_id: str) -> dict:
    """Inject KB ID and model ID into KnowledgeBase and Prompt nodes."""
    for node in definition.get("nodes", []):
        node_type = node.get("type")
        if node_type == "KnowledgeBase":
            kb_config = node["configuration"]["knowledgeBase"]
            kb_config["knowledgeBaseId"] = kb_id
            kb_config["modelId"] = model_id
        elif node_type == "Prompt":
            inline = node["configuration"]["prompt"]["sourceConfiguration"]["inline"]
            inline["modelId"] = model_id
    return definition


def main() -> None:
    config = _load_config()
    client = _bedrock_agent_client(config["region"], config["profile"] or None)

    with DEFINITION_PATH.open(encoding="utf-8") as handle:
        raw = json.load(handle)

    definition = {
        "nodes": raw["nodes"],
        "connections": raw["connections"],
    }
    definition = _apply_flow_config(
        definition,
        kb_id=config["kb_id"],
        model_id=config["model_id"],
    )

    logger.info("Updating flow id=%s in %s", config["flow_id"], config["region"])
    try:
        client.update_flow(
            flowIdentifier=config["flow_id"],
            name=FLOW_NAME,
            description=raw.get("description", "Orders KB RAG flow with classifier router"),
            executionRoleArn=config["role_arn"],
            definition=definition,
        )
    except ClientError as exc:
        logger.error("update_flow failed: %s", exc)
        sys.exit(1)

    logger.info("Preparing flow (applies working draft)")
    client.prepare_flow(flowIdentifier=config["flow_id"])

    version_response = client.create_flow_version(flowIdentifier=config["flow_id"])
    flow_version = version_response["version"]
    logger.info("Flow version created: %s", flow_version)

    client.update_flow_alias(
        flowIdentifier=config["flow_id"],
        aliasIdentifier=config["alias_id"],
        name="latest",
        description="Points to the latest prepared version",
        routingConfiguration=[{"flowVersion": flow_version}],
    )
    logger.info(
        "Alias %s repointed to version %s",
        config["alias_id"],
        flow_version,
    )

    print("\n--- Flow updated ---")
    print(f"BEDROCK_KB_FLOW_ID={config['flow_id']}")
    print(f"BEDROCK_KB_FLOW_ALIAS_ID={config['alias_id']}")
    print(f"Active version={flow_version}")
    print("\nNext: python bedrock_flows/invoke_kb_flow.py")


if __name__ == "__main__":
    main()
