#!/usr/bin/env python3
"""Deploy iiq-correlate, iiq-context, iiq-similar Lambdas and wire to Bedrock Agent."""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
import zipfile
from io import BytesIO
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv  # noqa: E402

import boto3  # noqa: E402
from botocore.exceptions import ClientError  # noqa: E402

ENRICHMENT_GROUPS = (
    {
        "folder": "iiq-correlate",
        "function_name": "iiq-correlate",
        "action_group_name": "iiq-correlate",
        "openapi_key": "agent/iiq-correlate/openapi_schema.yaml",
        "description": "Correlate deployments with dependency hops",
    },
    {
        "folder": "iiq-context",
        "function_name": "iiq-context",
        "action_group_name": "iiq-context",
        "openapi_key": "agent/iiq-context/openapi_schema.yaml",
        "description": "Owner lookup and business impact scoring",
    },
    {
        "folder": "iiq-similar",
        "function_name": "iiq-similar",
        "action_group_name": "iiq-similar",
        "openapi_key": "agent/iiq-similar/openapi_schema.yaml",
        "description": "Find similar historical incidents",
    },
)

TAGS = [
    {"Key": "Project", "Value": "piter-aiops"},
    {"Key": "Owner", "Value": "reemmor"},
]


def _package_lambda(folder: str) -> bytes:
    ag_dir = ROOT / "action_groups" / folder
    buf = BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for path in ag_dir.rglob("*"):
            if path.is_file() and path.suffix not in {".yaml", ".json"} or path.name.endswith(
                (".py", ".csv", ".json")
            ):
                if path.suffix == ".yaml" and "openapi" in path.name:
                    continue
                if path.parent.name == "events":
                    continue
                arc = str(path.relative_to(ag_dir)).replace("\\", "/")
                zf.write(path, arcname=arc)
    return buf.getvalue()


def _deploy_lambda(lambda_client, *, name: str, role_arn: str, folder: str, dry_run: bool) -> str:
    if dry_run:
        return f"arn:aws:lambda:us-east-1:000000000000:function:{name}"
    payload = _package_lambda(folder)
    try:
        lambda_client.get_function(FunctionName=name)
        lambda_client.update_function_code(FunctionName=name, ZipFile=payload)
        print(f"  Updated Lambda: {name}")
    except ClientError as exc:
        if exc.response["Error"]["Code"] != "ResourceNotFoundException":
            raise
        lambda_client.create_function(
            FunctionName=name,
            Runtime="python3.12",
            Role=role_arn,
            Handler="lambda_function.lambda_handler",
            Code={"ZipFile": payload},
            Timeout=15,
            MemorySize=256,
            Architectures=["arm64"],
            Description=f"PITER AiOps enrichment — {folder}",
            Tags={t["Key"]: t["Value"] for t in TAGS},
        )
        print(f"  Created Lambda: {name}")
    lambda_client.get_waiter("function_active").wait(FunctionName=name)
    return lambda_client.get_function(FunctionName=name)["Configuration"]["FunctionArn"]


def _upload_openapi(s3_client, bucket: str, key: str, folder: str, dry_run: bool) -> None:
    src = ROOT / "action_groups" / folder / "openapi_schema.yaml"
    if dry_run:
        print(f"  s3://{bucket}/{key}")
        return
    s3_client.upload_file(str(src), bucket, key, ExtraArgs={"ContentType": "application/x-yaml"})


def _find_action_group(agent_client, agent_id: str, name: str) -> dict | None:
    token = None
    while True:
        kwargs: dict = {"agentId": agent_id, "agentVersion": "DRAFT"}
        if token:
            kwargs["nextToken"] = token
        resp = agent_client.list_agent_action_groups(**kwargs)
        for group in resp.get("actionGroupSummaries", []):
            if group.get("actionGroupName") == name:
                return group
        token = resp.get("nextToken")
        if not token:
            return None


def _upsert_action_group(
    agent_client,
    *,
    agent_id: str,
    name: str,
    lambda_arn: str,
    bucket: str,
    openapi_key: str,
    description: str,
    dry_run: bool,
) -> None:
    if dry_run:
        print(f"  Action group {name} -> {lambda_arn}")
        return
    existing = _find_action_group(agent_client, agent_id, name)
    api_schema = {"s3": {"s3BucketName": bucket, "s3ObjectKey": openapi_key}}
    executor = {"lambda": lambda_arn}
    if existing:
        agent_client.update_agent_action_group(
            agentId=agent_id,
            agentVersion="DRAFT",
            actionGroupId=existing["actionGroupId"],
            actionGroupName=name,
            actionGroupExecutor=executor,
            apiSchema=api_schema,
            description=description,
            actionGroupState="ENABLED",
        )
        print(f"  Updated action group: {name}")
    else:
        agent_client.create_agent_action_group(
            agentId=agent_id,
            agentVersion="DRAFT",
            actionGroupName=name,
            actionGroupExecutor=executor,
            apiSchema=api_schema,
            description=description,
            actionGroupState="ENABLED",
        )
        print(f"  Created action group: {name}")


def _lambda_permission(lambda_client, *, fn: str, agent_id: str, region: str, account: str) -> None:
    sid = f"bedrock-agent-{fn}"
    source_arn = f"arn:aws:bedrock:{region}:{account}:agent/{agent_id}"
    try:
        lambda_client.add_permission(
            FunctionName=fn,
            StatementId=sid,
            Action="lambda:InvokeFunction",
            Principal="bedrock.amazonaws.com",
            SourceArn=source_arn,
        )
    except ClientError as exc:
        if exc.response["Error"]["Code"] != "ResourceConflictException":
            raise


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent-id", required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    load_dotenv(ROOT / ".env")
    region = os.environ.get("AWS_REGION", "us-east-1")
    bucket = os.environ.get("S3_BUCKET", "").strip()
    if not bucket:
        print("S3_BUCKET required", file=sys.stderr)
        return 1
    lambda_role = os.environ.get("LAMBDA_EXECUTION_ROLE_NAME", "PITER AiOps-lambda-role")
    session = boto3.Session(region_name=region)
    sts = session.client("sts")
    account = sts.get_caller_identity()["Account"]
    iam = session.client("iam")
    lambda_client = session.client("lambda")
    s3_client = session.client("s3")
    agent_client = session.client("bedrock-agent")

    try:
        role_arn = iam.get_role(RoleName=lambda_role)["Role"]["Arn"]
    except ClientError:
        print(f"IAM role {lambda_role} missing — run setup_action_group.py first", file=sys.stderr)
        return 1

    print(f"Agent {args.agent_id}  Account {account}")
    for spec in ENRICHMENT_GROUPS:
        print(f"\n=== {spec['function_name']} ===")
        arn = _deploy_lambda(
            lambda_client,
            name=spec["function_name"],
            role_arn=role_arn,
            folder=spec["folder"],
            dry_run=args.dry_run,
        )
        _upload_openapi(s3_client, bucket, spec["openapi_key"], spec["folder"], args.dry_run)
        if not args.dry_run:
            _lambda_permission(
                lambda_client,
                fn=spec["function_name"],
                agent_id=args.agent_id,
                region=region,
                account=account,
            )
        _upsert_action_group(
            agent_client,
            agent_id=args.agent_id,
            name=spec["action_group_name"],
            lambda_arn=arn,
            bucket=bucket,
            openapi_key=spec["openapi_key"],
            description=spec["description"],
            dry_run=args.dry_run,
        )

    if not args.dry_run:
        agent_client.prepare_agent(agentId=args.agent_id)
        print("\nPrepare started — waiting...")
        deadline = time.time() + 300
        while time.time() < deadline:
            status = agent_client.get_agent(agentId=args.agent_id)["agent"]["agentStatus"]
            if status == "PREPARED":
                break
            if status == "FAILED":
                raise RuntimeError("Agent preparation failed")
            time.sleep(5)
        print("Agent PREPARED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
