#!/usr/bin/env python3
"""Deploy PITER AWS alignment: piter-escalation, guardrail, agent prepare, alias update.

Idempotent mutations approved for PITER AiOps demo scope only.
Safe defaults: notification mock mode, no live SNS/SES from Lambda env.
"""
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

from app.bedrock_agent_client import AGENT_INSTRUCTION  # noqa: E402
from dotenv import load_dotenv  # noqa: E402

import boto3  # noqa: E402
from botocore.exceptions import ClientError  # noqa: E402

AGENT_ID = "HH4YGSLZUE"
ALIAS_ID = "O2EM03R4R3"
ALIAS_NAME = "live"
GUARDRAIL_ID = "rti921amc6u3"
KB_ID = "RBTJM6NIG9"
ESCALATION_FN = "piter-escalation"
ESCALATION_AG = "piter-escalation"
OPENAPI_KEY = "agent/piter-escalation/openapi_schema.yaml"
AGENT_ROLE = "incidentiq-agent-role"
AGENT_POLICY = "incidentiq-agent-resource"
LAMBDA_ROLE = "incidentiq-lambda-role"
NOTIFICATIONS_POLICY = "PITER-AiOps-Notifications"
LEGACY_OPS_AG = "incidentiq-ops"

LAMBDA_ARNS = (
    "incidentiq-actions",
    "iiq-correlate",
    "iiq-context",
    "iiq-similar",
    ESCALATION_FN,
)

SAFE_LAMBDA_ENV = {
    "PITER_NOTIFICATION_MODE": "mock",
    "PITER_ENABLE_LIVE_DISPATCH": "false",
    "PITER_NOTIFICATION_REQUIRE_CONFIRMATION": "true",
    "PITER_NOTIFICATION_ALLOWLIST": "",
    "PITER_NOTIFICATION_CONFIRMATION_TOKEN": "",
    "PITER_NOTIFICATION_ALLOWED_SEVERITIES": "P1,P2",
    "PITER_NOTIFICATION_MAX_SENDS_PER_INCIDENT": "1",
}


def _wait_prepared(agent_client, agent_id: str, *, timeout_s: int = 420) -> None:
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        status = agent_client.get_agent(agentId=agent_id)["agent"]["agentStatus"]
        if status == "PREPARED":
            return
        if status == "FAILED":
            raise RuntimeError("Agent preparation failed")
        time.sleep(8)
    raise TimeoutError(f"Agent {agent_id} not PREPARED within {timeout_s}s")


def _latest_version(agent_client, agent_id: str) -> str:
    versions = agent_client.list_agent_versions(agentId=agent_id, maxResults=50).get(
        "agentVersionSummaries", []
    )
    numeric = [v for v in versions if v.get("agentVersion", "").isdigit()]
    if not numeric:
        raise RuntimeError("No numeric agent versions found")
    return max(numeric, key=lambda v: int(v["agentVersion"]))["agentVersion"]


def _package_escalation_lambda() -> bytes:
    src = ROOT / "action_groups" / "piter-escalation" / "lambda_function.py"
    buf = BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.write(src, arcname="lambda_function.py")
    return buf.getvalue()


def _deploy_escalation_lambda(lambda_client, role_arn: str, *, dry_run: bool) -> str:
    if dry_run:
        return f"arn:aws:lambda:us-east-1:000000000000:function:{ESCALATION_FN}"
    payload = _package_escalation_lambda()
    try:
        lambda_client.get_function(FunctionName=ESCALATION_FN)
        lambda_client.update_function_code(FunctionName=ESCALATION_FN, ZipFile=payload)
        print(f"  Updated Lambda: {ESCALATION_FN}")
    except ClientError as exc:
        if exc.response["Error"]["Code"] != "ResourceNotFoundException":
            raise
        lambda_client.create_function(
            FunctionName=ESCALATION_FN,
            Runtime="python3.12",
            Role=role_arn,
            Handler="lambda_function.lambda_handler",
            Code={"ZipFile": payload},
            Timeout=15,
            MemorySize=256,
            Architectures=["arm64"],
            Description="PITER escalation preview/mock/gated-live notifications",
            Environment={"Variables": SAFE_LAMBDA_ENV},
            Tags={"Project": "piter-aiops", "Component": "escalation"},
        )
        print(f"  Created Lambda: {ESCALATION_FN}")
    lambda_client.get_waiter("function_active").wait(FunctionName=ESCALATION_FN)
    for attempt in range(6):
        try:
            lambda_client.update_function_configuration(
                FunctionName=ESCALATION_FN,
                Environment={"Variables": SAFE_LAMBDA_ENV},
                Timeout=15,
                MemorySize=256,
            )
            lambda_client.get_waiter("function_updated").wait(FunctionName=ESCALATION_FN)
            break
        except ClientError as exc:
            if exc.response["Error"]["Code"] != "ResourceConflictException" or attempt >= 5:
                raise
            time.sleep(10)
    return lambda_client.get_function(FunctionName=ESCALATION_FN)["Configuration"]["FunctionArn"]


def _attach_notifications_policy(iam, account: str, *, dry_run: bool) -> None:
    policy_arn = f"arn:aws:iam::{account}:policy/{NOTIFICATIONS_POLICY}"
    if dry_run:
        print(f"  Would attach {policy_arn} -> {LAMBDA_ROLE}")
        return
    try:
        iam.get_policy(PolicyArn=policy_arn)
    except ClientError as exc:
        if exc.response["Error"]["Code"] == "NoSuchEntity":
            print(f"  SKIP notifications policy (not found): {NOTIFICATIONS_POLICY}")
            return
        raise
    attached = iam.list_attached_role_policies(RoleName=LAMBDA_ROLE).get("AttachedPolicies", [])
    if any(p["PolicyArn"] == policy_arn for p in attached):
        print(f"  Notifications policy already on {LAMBDA_ROLE}")
        return
    iam.attach_role_policy(RoleName=LAMBDA_ROLE, PolicyArn=policy_arn)
    print(f"  Attached {NOTIFICATIONS_POLICY} -> {LAMBDA_ROLE}")


def _update_agent_role_policy(iam, *, region: str, account: str, bucket: str, model: str, dry_run: bool) -> None:
    resources = [f"arn:aws:lambda:{region}:{account}:function:{name}" for name in LAMBDA_ARNS]
    doc = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "BedrockKnowledgeBaseRetrieve",
                "Effect": "Allow",
                "Action": ["bedrock:Retrieve", "bedrock:RetrieveAndGenerate"],
                "Resource": f"arn:aws:bedrock:{region}:{account}:knowledge-base/{KB_ID}",
            },
            {
                "Sid": "InvokeActionGroupLambda",
                "Effect": "Allow",
                "Action": "lambda:InvokeFunction",
                "Resource": resources,
            },
            {
                "Sid": "ReadActionGroupOpenApiSchema",
                "Effect": "Allow",
                "Action": ["s3:GetObject", "s3:ListBucket"],
                "Resource": [
                    f"arn:aws:s3:::{bucket}",
                    f"arn:aws:s3:::{bucket}/agent/*",
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
                "Resource": [
                    model,
                    f"arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-haiku-4-5-20251001-v1:0",
                    f"arn:aws:bedrock:us-east-2::foundation-model/anthropic.claude-haiku-4-5-20251001-v1:0",
                    f"arn:aws:bedrock:us-west-2::foundation-model/anthropic.claude-haiku-4-5-20251001-v1:0",
                ],
            },
            {
                "Sid": "BedrockApplyGuardrail",
                "Effect": "Allow",
                "Action": [
                    "bedrock:GetGuardrail",
                    "bedrock:ApplyGuardrail",
                ],
                "Resource": f"arn:aws:bedrock:{region}:{account}:guardrail/{GUARDRAIL_ID}",
            },
        ],
    }
    if dry_run:
        print(f"  Would update IAM role policy {AGENT_ROLE}/{AGENT_POLICY}")
        return
    iam.put_role_policy(RoleName=AGENT_ROLE, PolicyName=AGENT_POLICY, PolicyDocument=json.dumps(doc))
    print(f"  Updated {AGENT_ROLE}/{AGENT_POLICY} (includes {ESCALATION_FN})")


def _lambda_permission(lambda_client, *, agent_id: str, region: str, account: str, dry_run: bool) -> None:
    sid = f"bedrock-agent-{ESCALATION_FN}"
    source_arn = f"arn:aws:bedrock:{region}:{account}:agent/{agent_id}"
    if dry_run:
        print(f"  Would add Lambda permission {sid}")
        return
    try:
        lambda_client.add_permission(
            FunctionName=ESCALATION_FN,
            StatementId=sid,
            Action="lambda:InvokeFunction",
            Principal="bedrock.amazonaws.com",
            SourceArn=source_arn,
        )
        print(f"  Added Lambda permission: {sid}")
    except ClientError as exc:
        if exc.response["Error"]["Code"] != "ResourceConflictException":
            raise
        print(f"  Lambda permission exists: {sid}")


def _find_action_group(agent_client, name: str) -> dict | None:
    token = None
    while True:
        kwargs: dict = {"agentId": AGENT_ID, "agentVersion": "DRAFT"}
        if token:
            kwargs["nextToken"] = token
        resp = agent_client.list_agent_action_groups(**kwargs)
        for group in resp.get("actionGroupSummaries", []):
            if group.get("actionGroupName") == name:
                return group
        token = resp.get("nextToken")
        if not token:
            return None


def _upsert_escalation_action_group(
    agent_client, *, lambda_arn: str, bucket: str, dry_run: bool
) -> None:
    if dry_run:
        print(f"  Would upsert action group {ESCALATION_AG}")
        return
    existing = _find_action_group(agent_client, ESCALATION_AG)
    api_schema = {"s3": {"s3BucketName": bucket, "s3ObjectKey": OPENAPI_KEY}}
    executor = {"lambda": lambda_arn}
    description = "PITER escalation policy preview and gated notification workflow"
    if existing:
        agent_client.update_agent_action_group(
            agentId=AGENT_ID,
            agentVersion="DRAFT",
            actionGroupId=existing["actionGroupId"],
            actionGroupName=ESCALATION_AG,
            actionGroupExecutor=executor,
            apiSchema=api_schema,
            description=description,
            actionGroupState="ENABLED",
        )
        print(f"  Updated action group: {ESCALATION_AG}")
    else:
        agent_client.create_agent_action_group(
            agentId=AGENT_ID,
            agentVersion="DRAFT",
            actionGroupName=ESCALATION_AG,
            actionGroupExecutor=executor,
            apiSchema=api_schema,
            description=description,
            actionGroupState="ENABLED",
        )
        print(f"  Created action group: {ESCALATION_AG}")


def _publish_guardrail(bedrock_client, *, dry_run: bool) -> str:
    if dry_run:
        return "1"
    try:
        resp = bedrock_client.create_guardrail_version(guardrailIdentifier=GUARDRAIL_ID)
        version = resp["version"]
        print(f"  Published guardrail {GUARDRAIL_ID} version {version}")
        return version
    except ClientError as exc:
        if exc.response["Error"]["Code"] != "ConflictException":
            raise
        listed = bedrock_client.list_guardrails(maxResults=20).get("guardrails", [])
        for item in listed:
            if item.get("id") == GUARDRAIL_ID or item.get("guardrailId") == GUARDRAIL_ID:
                version = str(item.get("version", "1"))
                print(f"  Guardrail version already published: {version}")
                return version
        return "1"


def _update_agent_with_guardrail(
    agent_client, *, guardrail_version: str, dry_run: bool
) -> None:
    agent = agent_client.get_agent(agentId=AGENT_ID)["agent"]
    if dry_run:
        print(f"  Would attach guardrail {GUARDRAIL_ID} v{guardrail_version}")
        return
    agent_client.update_agent(
        agentId=AGENT_ID,
        agentName=agent["agentName"],
        agentResourceRoleArn=agent["agentResourceRoleArn"],
        foundationModel=agent["foundationModel"],
        instruction=AGENT_INSTRUCTION,
        guardrailConfiguration={
            "guardrailIdentifier": GUARDRAIL_ID,
            "guardrailVersion": guardrail_version,
        },
    )
    print(f"  Updated agent instruction + guardrail v{guardrail_version}")


def _set_action_group_state(agent_client, name: str, state: str, *, dry_run: bool) -> None:
    if dry_run:
        print(f"  Would set {name} -> {state}")
        return
    existing = _find_action_group(agent_client, name)
    if not existing:
        print(f"  SKIP action group not found: {name}")
        return
    detail = agent_client.get_agent_action_group(
        agentId=AGENT_ID,
        agentVersion="DRAFT",
        actionGroupId=existing["actionGroupId"],
    )["agentActionGroup"]
    agent_client.update_agent_action_group(
        agentId=AGENT_ID,
        agentVersion="DRAFT",
        actionGroupId=existing["actionGroupId"],
        actionGroupName=detail["actionGroupName"],
        actionGroupExecutor=detail.get("actionGroupExecutor", {}),
        apiSchema=detail.get("apiSchema", {}),
        description=detail.get("description", ""),
        actionGroupState=state,
    )
    print(f"  Action group {name} -> {state}")


def _prepare_and_update_alias(agent_client, *, dry_run: bool) -> tuple[str, str]:
    """Prepare DRAFT and point the live alias at a new numbered version.

    Bedrock creates a numbered version when an alias is created or when
    ``update_agent_alias`` is called without ``routingConfiguration``. Pinning
    ``routingConfiguration`` to ``_latest_version()`` before a snapshot exists
    leaves the alias on an old version (DRAFT-only changes never go live).
    """
    if dry_run:
        return "4", ALIAS_ID
    alias_before = agent_client.get_agent_alias(agentId=AGENT_ID, agentAliasId=ALIAS_ID)[
        "agentAlias"
    ]
    prior_routing = alias_before.get("routingConfiguration") or []
    prior_version = prior_routing[0].get("agentVersion") if prior_routing else None

    agent_client.prepare_agent(agentId=AGENT_ID)
    print("  prepare_agent started...")
    _wait_prepared(agent_client, AGENT_ID)

    agent_client.update_agent_alias(
        agentId=AGENT_ID,
        agentAliasId=ALIAS_ID,
        agentAliasName=alias_before["agentAliasName"],
        description=alias_before.get("description", "PITER AiOps live alias"),
    )
    deadline = time.time() + 180
    version = prior_version or "1"
    while time.time() < deadline:
        alias = agent_client.get_agent_alias(agentId=AGENT_ID, agentAliasId=ALIAS_ID)["agentAlias"]
        status = alias.get("agentAliasStatus")
        routing = alias.get("routingConfiguration") or []
        if routing and routing[0].get("agentVersion"):
            version = routing[0]["agentVersion"]
            if version != prior_version and status == "PREPARED":
                break
        if status == "FAILED":
            raise RuntimeError(f"Alias {ALIAS_ID} failed during version snapshot")
        time.sleep(5)
    else:
        version = _latest_version(agent_client, AGENT_ID)
        print(f"  WARN: alias routing unchanged; latest numeric version is {version}")

    print(f"  Alias {ALIAS_NAME} ({ALIAS_ID}) -> version {version}")
    return version, ALIAS_ID


def _invoke_lambda_mock(lambda_client) -> None:
    event = {
        "messageVersion": "1.0",
        "actionGroup": ESCALATION_AG,
        "apiPath": "/escalation",
        "httpMethod": "POST",
        "parameters": [
            {"name": "operation", "value": "preview"},
            {"name": "service", "value": "bet-service"},
            {"name": "severity", "value": "P1"},
            {"name": "incident_id", "value": "INC-PREFLIGHT"},
            {"name": "recipient", "value": "role-primary-oncall"},
        ],
    }
    resp = lambda_client.invoke(FunctionName=ESCALATION_FN, Payload=json.dumps(event).encode())
    payload = json.loads(resp["Payload"].read())
    status = payload.get("response", {}).get("httpStatusCode")
    body = json.loads(payload["response"]["responseBody"]["application/json"]["body"])
    if status != 200 or body.get("mode") != "preview":
        raise RuntimeError(f"Lambda mock invoke failed: {payload}")
    print(f"  Lambda preview invoke OK (recipient masked: {body['escalation']['recipient']})")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument(
        "--disable-legacy-ops",
        action="store_true",
        help="Disable incidentiq-ops after piter-escalation is wired",
    )
    parser.add_argument("--skip-guardrail", action="store_true")
    parser.add_argument("--skip-alias", action="store_true")
    args = parser.parse_args()

    load_dotenv(ROOT / ".env")
    region = os.environ.get("PITER_AWS_REGION", os.environ.get("AWS_REGION", "us-east-1"))
    bucket = os.environ.get("PITER_S3_BUCKET", os.environ.get("S3_BUCKET", "")).strip()
    if not bucket:
        print("PITER_S3_BUCKET or S3_BUCKET required", file=sys.stderr)
        return 1

    session = boto3.Session(region_name=region, profile_name=os.environ.get("AWS_PROFILE") or None)
    sts = session.client("sts")
    account = sts.get_caller_identity()["Account"]
    iam = session.client("iam")
    lambda_client = session.client("lambda")
    s3 = session.client("s3")
    agent_client = session.client("bedrock-agent")
    bedrock_client = session.client("bedrock")

    agent = agent_client.get_agent(agentId=AGENT_ID)["agent"]
    model = agent["foundationModel"]
    lambda_role_arn = iam.get_role(RoleName=LAMBDA_ROLE)["Role"]["Arn"]

    print(f"Account {account[:3]}***{account[-3:]}  Region {region}  Agent {AGENT_ID}")
    print("\n=== 1. Deploy piter-escalation Lambda ===")
    lambda_arn = _deploy_escalation_lambda(lambda_client, lambda_role_arn, dry_run=args.dry_run)
    _attach_notifications_policy(iam, account, dry_run=args.dry_run)

    print("\n=== 2. IAM agent role (add piter-escalation invoke) ===")
    _update_agent_role_policy(
        iam, region=region, account=account, bucket=bucket, model=model, dry_run=args.dry_run
    )

    print("\n=== 3. OpenAPI upload ===")
    openapi_src = ROOT / "action_groups" / "piter-escalation" / "openapi_schema.yaml"
    if args.dry_run:
        print(f"  Would upload s3://{bucket}/{OPENAPI_KEY}")
    else:
        s3.upload_file(str(openapi_src), bucket, OPENAPI_KEY, ExtraArgs={"ContentType": "application/x-yaml"})
        print(f"  Uploaded s3://{bucket}/{OPENAPI_KEY}")

    print("\n=== 4. Lambda permission + action group ===")
    _lambda_permission(lambda_client, agent_id=AGENT_ID, region=region, account=account, dry_run=args.dry_run)
    _upsert_escalation_action_group(agent_client, lambda_arn=lambda_arn, bucket=bucket, dry_run=args.dry_run)

    if not args.skip_guardrail:
        print("\n=== 5. Guardrail publish + attach ===")
        guardrail_version = _publish_guardrail(bedrock_client, dry_run=args.dry_run)
        _update_agent_with_guardrail(agent_client, guardrail_version=guardrail_version, dry_run=args.dry_run)
    else:
        print("\n=== 5. Guardrail (skipped) ===")

    if args.disable_legacy_ops:
        print("\n=== 6. Disable legacy incidentiq-ops ===")
        _set_action_group_state(agent_client, LEGACY_OPS_AG, "DISABLED", dry_run=args.dry_run)

    print("\n=== 7. Prepare agent + update alias ===")
    if args.skip_alias:
        if not args.dry_run:
            agent_client.prepare_agent(agentId=AGENT_ID)
            _wait_prepared(agent_client, AGENT_ID)
        print("  Alias update skipped")
    else:
        version, alias_id = _prepare_and_update_alias(agent_client, dry_run=args.dry_run)
        print(f"  Result: alias {alias_id} -> v{version}")

    if not args.dry_run:
        print("\n=== 8. Lambda smoke (preview) ===")
        _invoke_lambda_mock(lambda_client)

    print("\nDone.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
