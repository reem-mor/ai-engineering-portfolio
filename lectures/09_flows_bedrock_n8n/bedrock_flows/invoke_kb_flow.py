"""Invoke the orders KB RAG Bedrock Flow alias and print the streamed output."""

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

DEFAULT_QUERY = "Which orders have status Processing?"


def _load_config() -> dict[str, str]:
    load_dotenv(LESSON_ROOT / ".env")
    flow_id = os.getenv("BEDROCK_KB_FLOW_ID", "")
    alias_id = os.getenv("BEDROCK_KB_FLOW_ALIAS_ID", "")
    region = os.getenv("AWS_REGION", "us-east-1")
    profile = os.getenv("AWS_PROFILE")

    if not flow_id or not alias_id:
        logger.error(
            "Set BEDROCK_KB_FLOW_ID and BEDROCK_KB_FLOW_ALIAS_ID in .env "
            "(run create_kb_flow.py first or copy from the Bedrock console)"
        )
        sys.exit(1)

    return {
        "flow_id": flow_id,
        "alias_id": alias_id,
        "region": region,
        "profile": profile or "",
    }


def _runtime_client(region: str, profile: str | None) -> object:
    session_kwargs: dict[str, str] = {"region_name": region}
    if profile:
        session_kwargs["profile_name"] = profile
    session = boto3.Session(**session_kwargs)
    return session.client("bedrock-agent-runtime")


def _collect_stream(response: dict) -> dict:
    """Merge all events from the invoke_flow response stream."""
    result: dict = {}
    for event in response.get("responseStream", []):
        result.update(event)
    return result


def invoke(
    *,
    text: str,
    flow_id: str,
    alias_id: str,
    region: str,
    profile: str | None,
) -> str:
    client = _runtime_client(region, profile)
    logger.info("Invoking flow_id=%s alias_id=%s", flow_id, alias_id)

    try:
        response = client.invoke_flow(
            flowIdentifier=flow_id,
            flowAliasIdentifier=alias_id,
            inputs=[
                {
                    "content": {"document": {"text": text}},
                    "nodeName": "FlowInput",
                    "nodeOutputName": "document",
                }
            ],
        )
    except ClientError as exc:
        logger.error("invoke_flow failed: %s", exc)
        raise

    result = _collect_stream(response)
    completion = result.get("flowCompletionEvent", {})
    reason = completion.get("completionReason", "UNKNOWN")

    if reason != "SUCCESS":
        logger.error("Flow completed with reason=%s", reason)
        if "flowFailEvent" in result:
            logger.error("Failure detail: %s", json.dumps(result["flowFailEvent"]))
        sys.exit(1)

    output = result["flowOutputEvent"]["content"]["document"]
    return output if isinstance(output, str) else json.dumps(output)


def main() -> None:
    config = _load_config()
    query = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else DEFAULT_QUERY

    answer = invoke(
        text=query,
        flow_id=config["flow_id"],
        alias_id=config["alias_id"],
        region=config["region"],
        profile=config["profile"] or None,
    )

    print("\n--- Question ---")
    print(query)
    print("\n--- Answer ---")
    print(answer)


if __name__ == "__main__":
    main()
