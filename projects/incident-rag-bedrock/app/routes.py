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
from app.upload_service import DocumentUploadService
from app.upload_validators import ALLOWED_UPLOAD_SUFFIXES
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


def _upload_service() -> DocumentUploadService:
    cached = current_app.extensions.get("upload_service")
    if cached is None:
        cfg: Config = Config.from_env() if not isinstance(current_app.config, Config) else current_app.config
        cached = DocumentUploadService(cfg)
        current_app.extensions["upload_service"] = cached
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
    max_bytes = getattr(cfg, "MAX_UPLOAD_BYTES", 5_242_880)
    return render_template(
        "index.html",
        examples=flat_example_questions(),
        example_groups=load_example_questions(),
        workflow_alerts=load_workflow_alerts(),
        max_len=MAX_QUESTION_LEN,
        model_label=_model_label(),
        kb_id=getattr(cfg, "BEDROCK_KB_ID", ""),
        s3_bucket=getattr(cfg, "S3_BUCKET", ""),
        s3_prefix=getattr(cfg, "S3_PREFIX", ""),
        max_upload_mb=max(1, max_bytes // (1024 * 1024)),
        allowed_types=", ".join(sorted(ALLOWED_UPLOAD_SUFFIXES)),
        sync_kb_default=bool(getattr(cfg, "BEDROCK_DATA_SOURCE_ID", "")),
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
    if not actions and alert:
        fallback = alert.get("actions")
        if isinstance(fallback, list):
            actions = [str(a) for a in fallback if str(a).strip()]

    effective_decision = alert.get("decision") if alert else None
    effective_reason = alert.get("decision_reason") if alert else None
    if not result.grounded:
        effective_decision = "escalate"
        effective_reason = "Insufficient knowledge-base context — escalate with prepared notes."

    matched_runbook = result.matched_runbook
    if not matched_runbook and result.citations:
        matched_runbook = result.citations[0].source_label
    if not matched_runbook and alert:
        matched_runbook = alert.get("matched_runbook")

    saved_min = 0
    impact_avoided = 0
    if alert:
        saved_min = max(0, int(alert.get("baseline_min", 0)) - int(alert.get("assisted_min", 0)))
        impact_avoided = saved_min * int(alert.get("impact_per_min", 0))

    return render_template(
        "_workflow_result.html",
        result=result,
        alert=alert,
        question=question,
        actions=actions,
        matched_runbook=matched_runbook,
        effective_decision=effective_decision,
        effective_reason=effective_reason,
        saved_min=saved_min,
        impact_avoided=impact_avoided,
        model_label=_model_label(),
    )


@bp.get("/health")
def health():
    return jsonify(status="ok"), 200


_UPLOAD_VALIDATION_CODES = {
    "missing_file",
    "unsupported_type",
    "empty_file",
    "file_too_large",
    "upload_disabled",
}


@bp.post("/documents/upload")
def upload_document():
    upload_file = request.files.get("document")
    sync_kb = request.form.get("sync_kb") == "on"
    filename = upload_file.filename if upload_file else None
    body = upload_file.read() if upload_file else b""

    try:
        result = _upload_service().upload(filename, body, sync_kb=sync_kb)
    except BedrockError as exc:
        status = 400 if exc.code in _UPLOAD_VALIDATION_CODES else 502
        if _wants_json():
            return jsonify(ok=False, reason=exc.code, message=exc.user_message), status
        return render_template("_upload_result.html", error=exc.user_message), status

    if _wants_json():
        return jsonify(ok=True, **result.to_dict()), 200
    return render_template("_upload_result.html", result=result), 200
