"""Create, prepare, version, and alias a Bedrock KB RAG flow from flow_kb_definition.json."""

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
    region = os.getenv("AWS_REGION", "us-east-1")
    profile = os.getenv("AWS_PROFILE")
    role_arn = os.getenv("BEDROCK_KB_FLOWS_EXECUTION_ROLE_ARN", "")
    model_id = os.getenv("BEDROCK_MODEL_ID", "amazon.nova-lite-v1:0")
    kb_id = os.getenv("BEDROCK_KB_ID", "KCYCNC0OSD")

    if not role_arn or "123456789012" in role_arn:
        logger.error(
            "Set BEDROCK_KB_FLOWS_EXECUTION_ROLE_ARN in lectures/09_flows_bedrock_n8n/.env"
        )
        sys.exit(1)

    return {
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

    logger.info("Creating flow '%s' in %s", FLOW_NAME, config["region"])
    try:
        create_response = client.create_flow(
            name=FLOW_NAME,
            description=raw.get("description", "Orders KB RAG flow"),
            executionRoleArn=config["role_arn"],
            definition=definition,
        )
    except ClientError as exc:
        logger.error("create_flow failed: %s", exc)
        sys.exit(1)

    flow_id = create_response["id"]
    logger.info("Flow created: id=%s arn=%s", flow_id, create_response.get("arn"))

    logger.info("Preparing flow (applies working draft)")
    client.prepare_flow(flowIdentifier=flow_id)

    version_response = client.create_flow_version(flowIdentifier=flow_id)
    flow_version = version_response["version"]
    logger.info("Flow version created: %s", flow_version)

    alias_response = client.create_flow_alias(
        flowIdentifier=flow_id,
        name="latest",
        description="Points to the latest prepared version",
        routingConfiguration=[{"flowVersion": flow_version}],
    )
    alias_id = alias_response["id"]
    logger.info("Flow alias created: id=%s name=latest", alias_id)

    print("\n--- Save these values to .env ---")
    print(f"BEDROCK_KB_FLOW_ID={flow_id}")
    print(f"BEDROCK_KB_FLOW_ALIAS_ID={alias_id}")
    print("\nNext: python bedrock_flows/invoke_kb_flow.py")


if __name__ == "__main__":
    main()
