"""Unit tests for BedrockRagClient using botocore Stubber — no real AWS calls."""
from __future__ import annotations

import boto3
import pytest
from botocore.stub import Stubber

from app.bedrock_client import BedrockRagClient
from app.config import Config
from app.errors import BedrockError


@pytest.fixture
def config():
    return Config(
        AWS_REGION="us-east-1",
        BEDROCK_KB_ID="KBTEST1234",
        BEDROCK_MODEL_ARN="arn:aws:bedrock:us-east-1::foundation-model/test",
        BEDROCK_NUM_RESULTS=5,
        SECRET_KEY="x",
        FLASK_ENV="testing",
    )


def _make_client_with_stub(config: Config):
    raw = boto3.client("bedrock-agent-runtime", region_name=config.AWS_REGION)
    stub = Stubber(raw)
    client = BedrockRagClient(config, client=raw)
    return client, stub


def test_ask_parses_grounded_answer(config):
    client, stub = _make_client_with_stub(config)
    stub.add_response(
        "retrieve_and_generate",
        {
            "output": {"text": "Roll back the latest deployment, then verify health."},
            "citations": [
                {
                    "retrievedReferences": [
                        {
                            "content": {"text": "Use kubectl rollout undo to roll back."},
                            "location": {
                                "type": "S3",
                                "s3Location": {"uri": "s3://kb/deployment_runbook.md"},
                            },
                        }
                    ]
                }
            ],
            "sessionId": "session-abc",
        },
    )

    with stub:
        result = client.ask("Deployment broke prod, what now?")

    assert result.grounded is True
    assert "Roll back" in result.answer
    assert len(result.citations) == 1
    assert result.citations[0].source_uri == "s3://kb/deployment_runbook.md"
    assert result.session_id == "session-abc"


def test_ask_handles_no_citations(config):
    client, stub = _make_client_with_stub(config)
    stub.add_response(
        "retrieve_and_generate",
        {"output": {"text": "Sorry, I don't know."}, "citations": [], "sessionId": "sess-x"},
    )
    with stub:
        result = client.ask("unrelated question")
    assert result.grounded is False
    assert result.citations == []


def test_ask_rejects_empty_question(config):
    client, _ = _make_client_with_stub(config)
    with pytest.raises(BedrockError) as exc:
        client.ask("   ")
    assert exc.value.code == "empty_question"


def test_ask_rejects_oversize_question(config):
    client, _ = _make_client_with_stub(config)
    with pytest.raises(BedrockError) as exc:
        client.ask("x" * 1000)
    assert exc.value.code == "oversize_question"


def test_ask_translates_throttling_error(config):
    client, stub = _make_client_with_stub(config)
    stub.add_client_error(
        "retrieve_and_generate",
        service_error_code="ThrottlingException",
        service_message="Rate exceeded",
        http_status_code=429,
    )
    with stub:
        with pytest.raises(BedrockError) as exc:
            client.ask("anything")
    assert exc.value.code == "ThrottlingException"
    assert "throttling" in exc.value.user_message.lower()


def test_ask_translates_access_denied(config):
    client, stub = _make_client_with_stub(config)
    stub.add_client_error(
        "retrieve_and_generate",
        service_error_code="AccessDeniedException",
        service_message="forbidden",
        http_status_code=403,
    )
    with stub:
        with pytest.raises(BedrockError) as exc:
            client.ask("anything")
    assert exc.value.code == "AccessDeniedException"
