"""HTTP routes: home page, /ask, workflow triage, /health."""
from __future__ import annotations

import logging

from flask import Blueprint, current_app, jsonify, render_template, request

from app.bedrock_client import BedrockRagClient, RagAnswer
from app.config import Config
from app.data_loader import (
    find_workflow_alert,
    flat_example_questions,
    load_example_questions,
    load_workflow_alerts,
)
from app.errors import BedrockError
from app.text_utils import parse_action_bullets
from app.validators import MAX_QUESTION_LEN, validate_question

log = logging.getLogger(__name__)
bp = Blueprint("main", __name__)


def _client() -> BedrockRagClient:
    cached = current_app.extensions.get("bedrock_client")
    if cached is None:
        cfg: Config = Config.from_env() if not isinstance(current_app.config, Config) else current_app.config
        cached = BedrockRagClient(cfg)
        current_app.extensions["bedrock_client"] = cached
    return cached


def _wants_json() -> bool:
    if request.headers.get("HX-Request"):
        return False
    if request.args.get("format") == "json":
        return True
    best = request.accept_mimetypes.best_match(["application/json", "text/html"])
    return best == "application/json" and request.accept_mimetypes[best] >= request.accept_mimetypes["text/html"]


def _model_label() -> str:
    cfg = current_app.config
    arn = getattr(cfg, "BEDROCK_MODEL_ARN", "") or ""
    if "/" in arn:
        return arn.rsplit("/", 1)[-1]
    return "Bedrock model"


def _handle_ask(question: str) -> RagAnswer:
    question = validate_question(question)
    return _client().ask(question)


def _validation_response(exc: BedrockError, question: str):
    if _wants_json():
        return jsonify(ok=False, reason=exc.code, message=exc.user_message), 400
    return render_template("_answer.html", error=exc.user_message, question=question), 400


def _bedrock_error_response(exc: BedrockError, question: str):
    log.warning("Bedrock error %s: %s", exc.code, exc.user_message)
    if _wants_json():
        return jsonify(ok=False, reason=exc.code, message=exc.user_message), 502
    return render_template("_answer.html", error=exc.user_message, question=question), 502


def _success_response(result: RagAnswer, question: str):
    if _wants_json():
        return jsonify(ok=True, **result.to_dict()), 200
    return render_template(
        "_answer.html",
        result=result,
        question=question,
        model_label=_model_label(),
    )


@bp.get("/")
def index():
    cfg = current_app.config
    return render_template(
        "index.html",
        examples=flat_example_questions(),
        example_groups=load_example_questions(),
        workflow_alerts=load_workflow_alerts(),
        max_len=MAX_QUESTION_LEN,
        model_label=_model_label(),
        kb_id=getattr(cfg, "BEDROCK_KB_ID", ""),
    )


@bp.post("/ask")
def ask():
    if request.is_json:
        payload = request.get_json(silent=True) or {}
        question = str(payload.get("question", ""))
    else:
        question = request.form.get("question") or ""

    question = question.strip()
    try:
        result = _handle_ask(question)
    except BedrockError as exc:
        if exc.code in {"empty_question", "short_question", "oversize_question", "stopwords_only"}:
            return _validation_response(exc, question)
        return _bedrock_error_response(exc, question)

    return _success_response(result, question)


@bp.post("/workflow/triage")
def workflow_triage():
    alert_id = request.form.get("alert_id")
    alert = find_workflow_alert(alert_id)
    question = (request.form.get("question") or (alert or {}).get("question") or "").strip()

    try:
        result = _handle_ask(question)
    except BedrockError as exc:
        if exc.code in {"empty_question", "short_question", "oversize_question", "stopwords_only"}:
            return render_template(
                "_workflow_result.html",
                error=exc.user_message,
                alert=alert,
                question=question,
            ), 400
        return render_template(
            "_workflow_result.html",
            error=exc.user_message,
            alert=alert,
            question=question,
        ), 502

    actions = parse_action_bullets(result.answer)
    effective_decision = alert.get("decision") if alert else None
    effective_reason = alert.get("decision_reason") if alert else None
    if not result.grounded:
        effective_decision = "escalate"
        effective_reason = "Insufficient knowledge-base context — escalate with prepared notes."

    return render_template(
        "_workflow_result.html",
        result=result,
        alert=alert,
        question=question,
        actions=actions,
        effective_decision=effective_decision,
        effective_reason=effective_reason,
        model_label=_model_label(),
    )


@bp.get("/health")
def health():
    return jsonify(status="ok"), 200
