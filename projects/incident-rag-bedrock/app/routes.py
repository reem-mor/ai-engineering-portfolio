"""HTTP routes: home page, /ask (HTMX partial), /health."""
from __future__ import annotations

import logging

from flask import Blueprint, current_app, jsonify, render_template, request

from app.bedrock_client import BedrockRagClient, MAX_QUESTION_LEN
from app.config import Config
from app.errors import BedrockError

log = logging.getLogger(__name__)
bp = Blueprint("main", __name__)


EXAMPLE_QUESTIONS = [
    "What should I check first when users cannot log in after a deployment?",
    "How do I triage an authentication service incident?",
    "Which runbook should I follow for database connectivity issues?",
    "What are the escalation steps for a P1 production outage?",
    "Summarize the standard health-check checklist before resolving an incident.",
]


def _client() -> BedrockRagClient:
    # Lazily build the client once per process so unit tests can inject a fake.
    cached = current_app.extensions.get("bedrock_client")
    if cached is None:
        cfg: Config = Config.from_env() if not isinstance(current_app.config, Config) else current_app.config
        cached = BedrockRagClient(cfg)
        current_app.extensions["bedrock_client"] = cached
    return cached


@bp.get("/")
def index():
    return render_template(
        "index.html",
        examples=EXAMPLE_QUESTIONS,
        max_len=MAX_QUESTION_LEN,
    )


@bp.post("/ask")
def ask():
    question = (request.form.get("question") or "").strip()

    if not question:
        return (
            render_template(
                "_answer.html",
                error="Please enter a question.",
                question=question,
            ),
            400,
        )
    if len(question) > MAX_QUESTION_LEN:
        return (
            render_template(
                "_answer.html",
                error=f"Question too long ({len(question)}/{MAX_QUESTION_LEN}).",
                question=question,
            ),
            400,
        )

    try:
        result = _client().ask(question)
    except BedrockError as exc:
        log.warning("Bedrock error %s: %s", exc.code, exc.user_message)
        return (
            render_template(
                "_answer.html",
                error=exc.user_message,
                question=question,
            ),
            502,
        )

    return render_template(
        "_answer.html",
        result=result,
        question=question,
    )


@bp.get("/health")
def health():
    return jsonify(status="ok"), 200
