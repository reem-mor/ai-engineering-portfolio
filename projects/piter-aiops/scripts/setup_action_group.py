#!/usr/bin/env python3
"""Deploy IncidentIQ Lambda action group and wire it to an existing Bedrock Agent.

Idempotent: creates IAM roles, Lambda, S3 OpenAPI upload, action group, prepares agent.

Usage (from project root):
  python scripts/setup_action_group.py --dry-run
  python scripts/setup_action_group.py
  python scripts/setup_action_group.py --agent-id HH4YGSLZUE
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
import zipfile
from dataclasses import dataclass
from io import BytesIO
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.bedrock_agent_client import AGENT_INSTRUCTION  # noqa: E402
from app.config import ConfigError  # noqa: E402
from dotenv import load_dotenv  # noqa: E402

import boto3  # noqa: E402
from botocore.exceptions import ClientError  # noqa: E402

INFRA = ROOT / "infra"
ACTION_GROUP_DIR = ROOT / "action_groups" / "incidentiq-ops"
LAMBDA_SOURCE = ACTION_GROUP_DIR / "lambda_function.py"
OPENAPI_SOURCE = ACTION_GROUP_DIR / "openapi_schema.yaml"


@dataclass(frozen=True)
class DeployConfig:
    AWS_REGION: str
    S3_BUCKET: str
    BEDROCK_KB_ID: str
    BEDROCK_MODEL_ARN: str


def _load_deploy_config() -> DeployConfig:
    load_dotenv(ROOT / ".env")
    region = os.environ.get("AWS_REGION", "us-east-1").strip()
    bucket = os.environ.get("S3_BUCKET", "").strip()
    if not bucket:
        raise ConfigError("S3_BUCKET required in .env for OpenAPI schema upload")
    return DeployConfig(
        AWS_REGION=region,
        S3_BUCKET=bucket,
        BEDROCK_KB_ID=os.environ.get("BEDROCK_KB_ID", "").strip(),
        BEDROCK_MODEL_ARN=os.environ.get("BEDROCK_MODEL_ARN", "").strip(),
    )


def _load_policy_template(name: str, **replacements: str) -> dict:
    raw = (INFRA / name).read_text(encoding="utf-8")
    for key, value in replacements.items():
        raw = raw.replace(key, value)
    return json.loads(raw)


def _account_id(sts_client) -> str:
    return sts_client.get_caller_identity()["Account"]


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


def _ensure_role(
    iam,
    *,
    role_name: str,
    trust_policy: dict,
    inline_policy_name: str,
    inline_policy: dict,
    account: str,
    dry_run: bool,
) -> str:
    role_arn = f"arn:aws:iam::{account}:role/{role_name}"
    if dry_run:
        print(f"  IAM role: {role_name} -> {role_arn}")
        return role_arn

    try:
        iam.get_role(RoleName=role_name)
        print(f"  IAM role exists: {role_name}")
    except ClientError as exc:
        if exc.response["Error"]["Code"] != "NoSuchEntity":
            raise
        iam.create_role(
            RoleName=role_name,
            AssumeRolePolicyDocument=json.dumps(trust_policy),
            Description="IncidentIQ Bedrock action group / agent resource role",
            Tags=[{"Key": "Project", "Value": "IncidentIQ"}],
        )
        print(f"  Created IAM role: {role_name}")

    iam.put_role_policy(
        RoleName=role_name,
        PolicyName=inline_policy_name,
        PolicyDocument=json.dumps(inline_policy),
    )
    print(f"  Updated inline policy: {inline_policy_name}")
    return role_arn


def _ensure_lambda_role(iam, *, role_name: str, region: str, account: str, dry_run: bool) -> str:
    trust = _load_policy_template("lambda_trust_policy.json")
    policy = _load_policy_template(
        "lambda_execution_policy.json",
        REGION=region,
        ACCOUNT_ID=account,
    )
    return _ensure_role(
        iam,
        role_name=role_name,
        trust_policy=trust,
        inline_policy_name="incidentiq-lambda-execution",
        inline_policy=policy,
        account=account,
        dry_run=dry_run,
    )


def _is_placeholder(value: str) -> bool:
    v = (value or "").strip()
    return not v or "XXXX" in v or "YYYY" in v or "<account-id>" in v


def _normalize_model_arn(model_arn: str, account: str) -> str:
    return model_arn.replace("<account-id>", account)


def _model_invoke_resources(model: str, region: str, account: str) -> list[str]:
    """IAM resource ARNs for Bedrock model invoke on the agent resource role."""
    resources: list[str] = []
    normalized = _normalize_model_arn(model, account)
    if normalized.startswith("arn:"):
        resources.append(normalized)
        if ":inference-profile/" in normalized:
            profile_id = normalized.rsplit("/", 1)[-1]
            # us.anthropic.claude-haiku-4-5-20251001-v1:0 -> anthropic.claude-haiku-4-5-20251001-v1:0
            foundation_id = profile_id.split(".", 1)[-1] if "." in profile_id else profile_id
            for reg in {region, "us-east-1", "us-east-2", "us-west-2"}:
                resources.append(f"arn:aws:bedrock:{reg}::foundation-model/{foundation_id}")
    else:
        for reg in {region, "us-east-1", "us-east-2", "us-west-2"}:
            resources.append(f"arn:aws:bedrock:{reg}::foundation-model/{model}")
    return list(dict.fromkeys(resources))


ENRICHMENT_LAMBDAS = ("iiq-correlate", "iiq-context", "iiq-similar")


def _lambda_invoke_resources(region: str, account: str, *function_names: str) -> list[str]:
    names = list(dict.fromkeys(function_names))
    return [f"arn:aws:lambda:{region}:{account}:function:{name}" for name in names]


def _build_agent_resource_policy(
    *,
    region: str,
    account: str,
    kb_id: str,
    lambda_functions: tuple[str, ...],
    s3_bucket: str,
    model: str,
) -> dict:
    return {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "BedrockKnowledgeBaseRetrieve",
                "Effect": "Allow",
                "Action": ["bedrock:Retrieve", "bedrock:RetrieveAndGenerate"],
                "Resource": f"arn:aws:bedrock:{region}:{account}:knowledge-base/{kb_id}",
            },
            {
                "Sid": "InvokeActionGroupLambda",
                "Effect": "Allow",
                "Action": "lambda:InvokeFunction",
                "Resource": _lambda_invoke_resources(region, account, *lambda_functions),
            },
            {
                "Sid": "ReadActionGroupOpenApiSchema",
                "Effect": "Allow",
                "Action": ["s3:GetObject", "s3:ListBucket"],
                "Resource": [
                    f"arn:aws:s3:::{s3_bucket}",
                    f"arn:aws:s3:::{s3_bucket}/agent/*",
                ],
            },
            {
                "Sid": "BedrockUseInferenceProfile",
                "Effect": "Allow",
                "Action": [
                    "bedrock:GetInferenceProfile",
                    "bedrock:ListInferenceProfiles",
                    "bedrock:UseInferenceProfile",
                ],
                "Resource": f"arn:aws:bedrock:{region}:{account}:inference-profile/*",
            },
            {
                "Sid": "BedrockInvokeFoundationModel",
                "Effect": "Allow",
                "Action": [
                    "bedrock:GetInferenceProfile",
                    "bedrock:InvokeModel",
                    "bedrock:InvokeModelWithResponseStream",
                ],
                "Resource": _model_invoke_resources(model, region, account),
            },
        ],
    }


def _resolve_kb_id(cfg: DeployConfig, agent_client, agent_id: str) -> str:
    if not _is_placeholder(cfg.BEDROCK_KB_ID):
        return cfg.BEDROCK_KB_ID
    resp = agent_client.list_agent_knowledge_bases(agentId=agent_id, agentVersion="DRAFT")
    summaries = resp.get("agentKnowledgeBaseSummaries") or []
    if summaries:
        kb_id = summaries[0]["knowledgeBaseId"]
        print(f"  Resolved KB ID from agent: {kb_id}")
        return kb_id
    raise RuntimeError("BEDROCK_KB_ID placeholder and agent has no linked knowledge base")


def _resolve_foundation_model(cfg: DeployConfig, agent_client, agent_id: str, account: str) -> str:
    if not _is_placeholder(cfg.BEDROCK_MODEL_ARN):
        return _normalize_model_arn(cfg.BEDROCK_MODEL_ARN, account)
    model = agent_client.get_agent(agentId=agent_id)["agent"]["foundationModel"]
    print(f"  Resolved foundation model from agent: {model}")
    return model


def _ensure_agent_role(
    iam,
    *,
    role_name: str,
    region: str,
    account: str,
    kb_id: str,
    lambda_functions: tuple[str, ...],
    s3_bucket: str,
    model: str,
    dry_run: bool,
) -> str:
    trust = _load_policy_template(
        "agent_trust_policy.json",
        REGION=region,
        ACCOUNT_ID=account,
    )
    policy = _build_agent_resource_policy(
        region=region,
        account=account,
        kb_id=kb_id,
        lambda_functions=lambda_functions,
        s3_bucket=s3_bucket,
        model=model,
    )
    return _ensure_role(
        iam,
        role_name=role_name,
        trust_policy=trust,
        inline_policy_name="incidentiq-agent-resource",
        inline_policy=policy,
        account=account,
        dry_run=dry_run,
    )


def _package_lambda() -> bytes:
    buf = BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.write(LAMBDA_SOURCE, arcname="lambda_function.py")
    return buf.getvalue()


def _deploy_lambda(
    lambda_client,
    *,
    function_name: str,
    role_arn: str,
    region: str,
    dry_run: bool,
    skip_lambda: bool,
) -> str:
    fn_arn = f"arn:aws:lambda:{region}:{role_arn.split(':')[4]}:function:{function_name}"
    if skip_lambda:
        print(f"  Skipping Lambda deploy (--skip-lambda); using {fn_arn}")
        return fn_arn

    if dry_run:
        print(f"  Lambda: {function_name} -> {fn_arn}")
        return fn_arn

    payload = _package_lambda()
    try:
        lambda_client.get_function(FunctionName=function_name)
        lambda_client.update_function_code(FunctionName=function_name, ZipFile=payload)
        print(f"  Updated Lambda code: {function_name}")
    except ClientError as exc:
        if exc.response["Error"]["Code"] != "ResourceNotFoundException":
            raise
        lambda_client.create_function(
            FunctionName=function_name,
            Runtime="python3.12",
            Role=role_arn,
            Handler="lambda_function.lambda_handler",
            Code={"ZipFile": payload},
            Timeout=15,
            MemorySize=256,
            Architectures=["arm64"],
            Description="IncidentIQ Bedrock action group (ops tools)",
            Tags={"Project": "IncidentIQ"},
        )
        print(f"  Created Lambda: {function_name}")

    waiter = lambda_client.get_waiter("function_active")
    waiter.wait(FunctionName=function_name)
    resp = lambda_client.get_function(FunctionName=function_name)
    return resp["Configuration"]["FunctionArn"]


def _upload_openapi(s3_client, *, bucket: str, key: str, dry_run: bool) -> None:
    if dry_run:
        print(f"  S3 upload: s3://{bucket}/{key}")
        return
    s3_client.upload_file(str(OPENAPI_SOURCE), bucket, key, ExtraArgs={"ContentType": "application/x-yaml"})
    print(f"  Uploaded OpenAPI: s3://{bucket}/{key}")


def _ensure_lambda_permission(
    lambda_client,
    *,
    function_name: str,
    agent_id: str,
    region: str,
    account: str,
    dry_run: bool,
) -> None:
    statement_id = "bedrock-agent-invoke"
    source_arn = f"arn:aws:bedrock:{region}:{account}:agent/{agent_id}"
    if dry_run:
        print(f"  Lambda permission: bedrock.amazonaws.com -> {function_name} (source {source_arn})")
        return
    try:
        lambda_client.add_permission(
            FunctionName=function_name,
            StatementId=statement_id,
            Action="lambda:InvokeFunction",
            Principal="bedrock.amazonaws.com",
            SourceArn=source_arn,
        )
        print(f"  Added Lambda permission for agent {agent_id}")
    except ClientError as exc:
        if exc.response["Error"]["Code"] == "ResourceConflictException":
            print(f"  Lambda permission already exists: {statement_id}")
        else:
            raise


def _find_action_group(agent_client, agent_id: str, name: str) -> dict | None:
    token: str | None = None
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
    action_group_name: str,
    lambda_arn: str,
    s3_bucket: str,
    s3_key: str,
    dry_run: bool,
) -> None:
    if dry_run:
        print(
            f"  Action group: {action_group_name} -> Lambda {lambda_arn}, "
            f"schema s3://{s3_bucket}/{s3_key}"
        )
        return

    existing = _find_action_group(agent_client, agent_id, action_group_name)
    api_schema = {"s3": {"s3BucketName": s3_bucket, "s3ObjectKey": s3_key}}
    executor = {"lambda": lambda_arn}
    description = "NOC ops: environment status, alerts, incident creation"

    if existing:
        agent_client.update_agent_action_group(
            agentId=agent_id,
            agentVersion="DRAFT",
            actionGroupId=existing["actionGroupId"],
            actionGroupName=action_group_name,
            actionGroupExecutor=executor,
            apiSchema=api_schema,
            description=description,
            actionGroupState="ENABLED",
        )
        print(f"  Updated action group: {action_group_name}")
    else:
        agent_client.create_agent_action_group(
            agentId=agent_id,
            agentVersion="DRAFT",
            actionGroupName=action_group_name,
            actionGroupExecutor=executor,
            apiSchema=api_schema,
            description=description,
            actionGroupState="ENABLED",
        )
        print(f"  Created action group: {action_group_name}")


def _sync_agent(
    agent_client,
    *,
    agent_id: str,
    agent_role_arn: str,
    foundation_model: str,
    dry_run: bool,
) -> None:
    if dry_run:
        print(f"  update_agent: resource role -> {agent_role_arn}")
        print(f"  update_agent: foundation model -> {foundation_model}")
        print("  update_agent: instruction synced from AGENT_INSTRUCTION")
        return

    agent = agent_client.get_agent(agentId=agent_id)["agent"]
    current_role = agent.get("agentResourceRoleArn", "")
    if current_role != agent_role_arn:
        print(f"  Migrating agent resource role: {current_role or '(none)'} -> {agent_role_arn}")

    update_kwargs = {
        "agentId": agent_id,
        "agentName": agent["agentName"],
        "agentResourceRoleArn": agent_role_arn,
        "foundationModel": foundation_model,
        "instruction": AGENT_INSTRUCTION,
    }
    for attempt in range(3):
        try:
            agent_client.update_agent(**update_kwargs)
            break
        except ClientError as exc:
            if exc.response.get("Error", {}).get("Code") != "AccessDeniedException":
                raise
            if attempt >= 2 or ":inference-profile/" not in foundation_model:
                raise
            wait_s = 15 * (attempt + 1)
            print(f"  IAM propagation delay — retrying update_agent in {wait_s}s...")
            time.sleep(wait_s)
    print("  Updated agent instruction and resource role")


def main() -> int:
    parser = argparse.ArgumentParser(description="Deploy IncidentIQ Lambda action group")
    parser.add_argument("--agent-id", help="Override BEDROCK_AGENT_ID from .env")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--skip-lambda", action="store_true")
    parser.add_argument("--lambda-function-name", default=None)
    parser.add_argument("--action-group-name", default=None)
    args = parser.parse_args()

    try:
        cfg = _load_deploy_config()
    except ConfigError as exc:
        print(f"Config error: {exc}", file=sys.stderr)
        return 1

    agent_id = (args.agent_id or cfg.BEDROCK_AGENT_ID).strip()
    if _is_placeholder(agent_id):
        print("BEDROCK_AGENT_ID required (set in .env or pass --agent-id)", file=sys.stderr)
        return 1
    if not cfg.S3_BUCKET:
        print("S3_BUCKET required in .env for OpenAPI schema upload", file=sys.stderr)
        return 1

    lambda_fn = args.lambda_function_name or os.environ.get("LAMBDA_FUNCTION_NAME", "incidentiq-actions")
    action_group_name = args.action_group_name or os.environ.get("ACTION_GROUP_NAME", "incidentiq-ops")
    openapi_key = os.environ.get("ACTION_GROUP_OPENAPI_S3_KEY", "agent/incidentiq-ops/openapi_schema.yaml")
    lambda_role_name = os.environ.get("LAMBDA_EXECUTION_ROLE_NAME", "incidentiq-lambda-role")
    agent_role_name = os.environ.get("BEDROCK_AGENT_RESOURCE_ROLE_NAME", "incidentiq-agent-role")

    region = cfg.AWS_REGION
    session = boto3.Session(region_name=region)
    sts = session.client("sts")
    account = _account_id(sts)
    iam = session.client("iam")
    lambda_client = session.client("lambda")
    s3_client = session.client("s3")
    agent_client = session.client("bedrock-agent")

    kb_id = _resolve_kb_id(cfg, agent_client, agent_id)
    foundation_model = _resolve_foundation_model(cfg, agent_client, agent_id, account)

    print(f"Account: {account}  Region: {region}  Agent: {agent_id}")
    print(f"  KB: {kb_id}  Model: {foundation_model}")
    print()

    print("1. IAM roles")
    lambda_role_arn = _ensure_lambda_role(
        iam, role_name=lambda_role_name, region=region, account=account, dry_run=args.dry_run
    )
    all_lambdas = (lambda_fn,) + ENRICHMENT_LAMBDAS
    agent_role_arn = _ensure_agent_role(
        iam,
        role_name=agent_role_name,
        region=region,
        account=account,
        kb_id=kb_id,
        lambda_functions=all_lambdas,
        s3_bucket=cfg.S3_BUCKET,
        model=foundation_model,
        dry_run=args.dry_run,
    )
    print()

    print("2. Lambda function")
    lambda_arn = _deploy_lambda(
        lambda_client,
        function_name=lambda_fn,
        role_arn=lambda_role_arn,
        region=region,
        dry_run=args.dry_run,
        skip_lambda=args.skip_lambda,
    )
    print()

    print("3. OpenAPI schema")
    _upload_openapi(s3_client, bucket=cfg.S3_BUCKET, key=openapi_key, dry_run=args.dry_run)
    print()

    print("4. Lambda invoke permission")
    _ensure_lambda_permission(
        lambda_client,
        function_name=lambda_fn,
        agent_id=agent_id,
        region=region,
        account=account,
        dry_run=args.dry_run,
    )
    print()

    print("5. Agent sync (instruction + resource role)")
    _sync_agent(
        agent_client,
        agent_id=agent_id,
        agent_role_arn=agent_role_arn,
        foundation_model=foundation_model,
        dry_run=args.dry_run,
    )
    print()

    print("6. Action group")
    _upsert_action_group(
        agent_client,
        agent_id=agent_id,
        action_group_name=action_group_name,
        lambda_arn=lambda_arn,
        s3_bucket=cfg.S3_BUCKET,
        s3_key=openapi_key,
        dry_run=args.dry_run,
    )
    print()

    print("7. Prepare agent")
    if args.dry_run:
        print("  prepare_agent (skipped in dry-run)")
    else:
        agent_client.prepare_agent(agentId=agent_id)
        print("  Prepare started — waiting for PREPARED...")
        _wait_prepared(agent_client, agent_id)
        print("  Agent is PREPARED")

    print()
    print("Done. Test prompts:")
    print('  "What\'s the current status of GIB?"')
    print('  "Show me alerts in GIB from the last 6 hours."')
    print('  python scripts/agent_smoke_test.py --ops')
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
