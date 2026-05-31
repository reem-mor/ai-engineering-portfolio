"""Shared pytest fixtures: build a Flask app with a fake Bedrock client."""
from __future__ import annotations

import pytest

from app import create_app
from app.config import Config


class _FakeBedrockClient:
    """Fake BedrockRagClient that returns canned responses, controlled per-test."""

    def __init__(self):
        self.next_response = None
        self.next_error = None
        self.calls: list[str] = []

    def ask(self, question: str):
        self.calls.append(question)
        if self.next_error is not None:
            raise self.next_error
        return self.next_response


@pytest.fixture
def fake_config():
    return Config(
        AWS_REGION="us-east-1",
        BEDROCK_KB_ID="kb-test",
        BEDROCK_MODEL_ARN="arn:aws:bedrock:us-east-1::foundation-model/test",
        BEDROCK_NUM_RESULTS=5,
        SECRET_KEY="test-secret",
        FLASK_ENV="testing",
    )


@pytest.fixture
def fake_bedrock():
    return _FakeBedrockClient()


@pytest.fixture
def app(fake_config, fake_bedrock):
    app = create_app(fake_config)
    app.config.update(TESTING=True, WTF_CSRF_ENABLED=False)
    app.extensions["bedrock_client"] = fake_bedrock
    return app


@pytest.fixture
def client(app):
    return app.test_client()
