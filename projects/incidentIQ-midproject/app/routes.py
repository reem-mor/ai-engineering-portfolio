"""HTTP routes: SPA bootstrap, /ask, workflow triage, uploads, /health."""
from __future__ import annotations

import logging

from flask import Blueprint, current_app, jsonify, render_template, request, send_from_directory
from flask_wtf.csrf import generate_csrf

from app.bedrock_agent_client import build_session_attributes
from app.bedrock_client import RagAnswer
from app.rag_factory import RagClient, get_local_client, get_rag_client
from app.config import Config
from app.data_loader import (
    find_workflow_alert,
    flat_example_questions,
    grouped_example_questions,
    load_workflow_alerts,
)
from app.errors import BedrockError
from app.spa import _SPA_ROOT, spa_enabled
from app.upload_service import DocumentUploadService
from app.upload_validators import ALLOWED_UPLOAD_SUFFIXES
from app.validators import MAX_QUESTION_LEN, validate_question
from app.workflow import build_workflow_payload
from app.services.triage_service import DEMO_ALERT, run_follow_up, run_triage

log = logging.getLogger(__name__)
bp = Blueprint("main", __name__)

_VALIDATION_CODES = {"empty_question", "short_question", "oversize_question", "stopwords_only"}


def _app_config() -> Config:
    cfg = current_app.config.get("INCIDENTIQ_CONFIG")
    if isinstance(cfg, Config):
        return cfg
    return Config.from_env()


def _client() -> RagClient:
    cached = current_app.extensions.get("bedrock_client")
    if cached is None:
        cached = get_rag_client(_app_config())
        current_app.extensions["bedrock_client"] = cached
    return cached


def _local_client() -> RagClient:
    cached = current_app.extensions.get("local_client")
    if cached is None:
        cached = get_local_client()
        current_app.extensions["local_client"] = cached
    return cached


def _fallback_enabled() -> bool:
    """Local fallback is on by default but skipped during tests of the error path."""
    return bool(current_app.config.get("LOCAL_FALLBACK", True))


def _upload_service() -> DocumentUploadService:
    cached = current_app.extensions.get("upload_service")
    if cached is None:
        cached = DocumentUploadService(_app_config())
        current_app.extensions["upload_service"] = cached
    return cached


def _wants_json() -> bool:
    if request.headers.get("HX-Request"):
        return False
    if request.args.get("format") == "json":
        return True
    if request.is_json:
        return True
    best = request.accept_mimetypes.best_match(["application/json", "text/html"])
    return best == "application/json" and request.accept_mimetypes[best] >= request.accept_mimetypes["text/html"]


def _cfg_get(key: str, default: str = "") -> str:
    """Read Flask config keys set via Config.from_object (dict storage)."""
    value = current_app.config.get(key, default)
    return value if value is not None else default


def _model_label() -> str:
    arn = _cfg_get("BEDROCK_MODEL_ARN")
    if "/" in arn:
        return arn.rsplit("/", 1)[-1]
    return "Bedrock model"


def _bootstrap_context() -> dict:
    max_bytes = current_app.config.get("MAX_UPLOAD_BYTES", 5_242_880)
    if not isinstance(max_bytes, int):
        max_bytes = int(max_bytes or 5_242_880)
    return {
        "examples": flat_example_questions(),
        "example_groups": grouped_example_questions(),
        "workflow_alerts": load_workflow_alerts(),
        "max_len": MAX_QUESTION_LEN,
        "model_label": _model_label(),
        "kb_id": _cfg_get("BEDROCK_KB_ID"),
        "s3_bucket": _cfg_get("S3_BUCKET"),
        "s3_prefix": _cfg_get("S3_PREFIX"),
        "max_upload_mb": max(1, max_bytes // (1024 * 1024)),
        "allowed_types": sorted(ALLOWED_UPLOAD_SUFFIXES),
        "sync_kb_default": bool(_cfg_get("BEDROCK_DATA_SOURCE_ID")),
        "spa_enabled": spa_enabled(),
    }


def _handle_ask(
    question: str,
    *,
    session_id: str | None = None,
    session_attributes: dict[str, str] | None = None,
    prompt_session_attributes: dict[str, str] | None = None,
) -> RagAnswer:
    question = validate_question(question)
    client = _client()

    def _invoke(target: RagClient) -> RagAnswer:
        if session_attributes is not None and hasattr(target, "ask"):
            try:
                return target.ask(
                    question,
                    session_id=session_id,
                    session_attributes=session_attributes,
                    prompt_session_attributes=prompt_session_attributes,
                )
            except TypeError:
                # Backend without session-attribute support (e.g. local client).
                return target.ask(question, session_id=session_id)
        return target.ask(question, session_id=session_id)

    try:
        return _invoke(client)
    except BedrockError as exc:
        if exc.code in _VALIDATION_CODES or not _fallback_enabled():
            raise
        log.warning("Bedrock failed (%s) — answering from LOCAL knowledge base", exc.code)
        return _invoke(_local_client())


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


@bp.get("/api/bootstrap")
def api_bootstrap():
    payload = _bootstrap_context()
    payload["csrf_token"] = generate_csrf()
    return jsonify(ok=True, **payload), 200


@bp.get("/")
def index():
    if spa_enabled():
        return send_from_directory(_SPA_ROOT, "index.html")
    ctx = _bootstrap_context()
    return render_template(
        "index.html",
        examples=ctx["examples"],
        example_groups=ctx["example_groups"],
        workflow_alerts=ctx["workflow_alerts"],
        max_len=ctx["max_len"],
        model_label=ctx["model_label"],
        kb_id=ctx["kb_id"],
        s3_bucket=ctx["s3_bucket"],
        s3_prefix=ctx["s3_prefix"],
        max_upload_mb=ctx["max_upload_mb"],
        allowed_types=", ".join(ctx["allowed_types"]),
        sync_kb_default=ctx["sync_kb_default"],
    )


@bp.get("/ask")
def ask_get_not_allowed():
    return jsonify(ok=False, message="Method not allowed. Use POST."), 405


@bp.post("/ask")
def ask():
    session_id: str | None = None
    if request.is_json:
        payload = request.get_json(silent=True) or {}
        question = str(payload.get("question", ""))
        raw_session = payload.get("session_id")
        if raw_session:
            session_id = str(raw_session).strip() or None
    else:
        question = request.form.get("question") or ""
        raw_session = request.form.get("session_id")
        if raw_session:
            session_id = str(raw_session).strip() or None

    question = question.strip()
    try:
        result = _handle_ask(question, session_id=session_id)
    except BedrockError as exc:
        if exc.code in {"empty_question", "short_question", "oversize_question", "stopwords_only"}:
            return _validation_response(exc, question)
        return _bedrock_error_response(exc, question)

    return _success_response(result, question)


def _workflow_triage_core(
    alert_id: str | None,
    question: str,
    *,
    session_id: str | None = None,
):
    alert = find_workflow_alert(alert_id)
    question = (question or (alert or {}).get("question") or "").strip()
    session_attrs, prompt_attrs = build_session_attributes(
        alert_id=alert_id,
        service=str((alert or {}).get("service") or ""),
        environment=str((alert or {}).get("environment") or ""),
        severity=str((alert or {}).get("severity") or ""),
        symptom=str((alert or {}).get("symptom") or ""),
        alert_time=str((alert or {}).get("alert_time") or ""),
        triage_complete="false",
    )
    result = _handle_ask(
        question,
        session_id=session_id,
        session_attributes=session_attrs,
        prompt_session_attributes=prompt_attrs,
    )
    payload = build_workflow_payload(
        result=result,
        alert=alert,
        question=question,
        model_label=_model_label(),
    )
    return alert, question, payload


@bp.post("/workflow/triage")
def workflow_triage():
    if request.is_json:
        body = request.get_json(silent=True) or {}
        alert_id = body.get("alert_id")
        question = str(body.get("question", "")).strip()
    else:
        alert_id = request.form.get("alert_id")
        question = (request.form.get("question") or "").strip()

    try:
        alert, question, payload = _workflow_triage_core(alert_id, question)
    except BedrockError as exc:
        if exc.code in {"empty_question", "short_question", "oversize_question", "stopwords_only"}:
            if _wants_json():
                return jsonify(ok=False, reason=exc.code, message=exc.user_message), 400
            return render_template(
                "_workflow_result.html",
                error=exc.user_message,
                alert=find_workflow_alert(alert_id),
                question=question,
            ), 400
        if _wants_json():
            return jsonify(ok=False, reason=exc.code, message=exc.user_message), 502
        return render_template(
            "_workflow_result.html",
            error=exc.user_message,
            alert=find_workflow_alert(alert_id),
            question=question,
        ), 502

    if _wants_json():
        return jsonify(ok=True, **payload), 200

    return render_template("_workflow_result.html", **payload)


@bp.post("/api/workflow/triage")
def api_workflow_triage():
    body = request.get_json(silent=True) or {}
    alert_id = body.get("alert_id")
    question = str(body.get("question", "")).strip()
    session_id = body.get("session_id")
    if session_id is not None:
        session_id = str(session_id).strip() or None
    try:
        _alert, _question, payload = _workflow_triage_core(
            alert_id, question, session_id=session_id
        )
    except BedrockError as exc:
        status = 400 if exc.code in {"empty_question", "short_question", "oversize_question", "stopwords_only"} else 502
        return jsonify(ok=False, reason=exc.code, message=exc.user_message), status
    return jsonify(ok=True, **payload), 200


@bp.get("/console")
def console():
    """Self-contained local-first triage console for the live demo."""
    return render_template("console.html")


def _ask_fn():
    """Closure that asks the active RAG backend with local auto-fallback."""
    return lambda question: _handle_ask(question)


@bp.get("/api/demo-alert")
def api_demo_alert():
    """Return the canned demo alert (Postgres CPU 95% on prod-db-1, NJ-DGE, P2)."""
    return jsonify(ok=True, alert=DEMO_ALERT), 200


@bp.post("/api/triage")
def api_triage():
    """Run triage for a free-form alert and return one triage card."""
    body = request.get_json(silent=True) or {}
    session_id = body.get("session_id")
    if session_id is not None:
        session_id = str(session_id).strip() or None
    alert = {
        "alert_id": str(body.get("alert_id") or "").strip() or None,
        "service": str(body.get("service", "")).strip(),
        "environment": str(body.get("environment", "")).strip(),
        "severity": str(body.get("severity", "")).strip(),
        "symptom": str(body.get("symptom") or body.get("description") or "").strip(),
        "description": str(body.get("description") or body.get("symptom") or "").strip(),
        "alert_time": str(body.get("alert_time", "")).strip(),
        "duration_minutes": body.get("duration_minutes", 60),
    }
    if not alert["service"] or not alert["symptom"]:
        return jsonify(ok=False, reason="invalid_alert",
                       message="An alert needs at least a service and a symptom/description."), 400
    try:
        card = run_triage(alert, ask_fn=_ask_fn(), session_id=session_id)
    except BedrockError as exc:
        status = 400 if exc.code in _VALIDATION_CODES else 502
        return jsonify(ok=False, reason=exc.code, message=exc.user_message), status
    return jsonify(ok=True, **card), 200


@bp.post("/api/follow-up")
def api_follow_up():
    """Answer a follow-up question reusing the incident session memory."""
    body = request.get_json(silent=True) or {}
    session_id = str(body.get("session_id") or "").strip()
    question = str(body.get("question") or "").strip()
    if not session_id:
        return jsonify(ok=False, reason="missing_session",
                       message="A follow-up needs the session_id from the triage card."), 400
    if not question:
        return jsonify(ok=False, reason="empty_question", message="Please enter a follow-up question."), 400
    try:
        result = run_follow_up(session_id, question, ask_fn=_ask_fn())
    except BedrockError as exc:
        status = 400 if exc.code in _VALIDATION_CODES else 502
        return jsonify(ok=False, reason=exc.code, message=exc.user_message), status
    if result is None:
        return jsonify(ok=False, reason="unknown_session",
                       message="That incident session was not found. Run triage first."), 404
    return jsonify(ok=True, **result), 200


@bp.get("/health")
def health():
    if request.args.get("deep") != "1":
        return jsonify(status="ok"), 200

    checks: dict[str, str] = {"app": "ok"}
    bucket = _cfg_get("S3_BUCKET")
    kb_id = _cfg_get("BEDROCK_KB_ID")
    model_arn = _cfg_get("BEDROCK_MODEL_ARN")

    if not bucket:
        checks["s3"] = "missing_config"
    else:
        checks["s3"] = "configured"

    if not kb_id or not model_arn:
        checks["bedrock"] = "missing_config"
    else:
        checks["bedrock"] = "configured"

    status = "ok" if all(v in {"ok", "configured"} for v in checks.values()) else "degraded"
    return jsonify(status=status, checks=checks), 200


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
    sync_kb = request.form.get("sync_kb") == "on" or request.form.get("sync_kb") == "true"
    filename = upload_file.filename if upload_file else None
    body = upload_file.read() if upload_file else b""

    try:
        result = _upload_service().upload(filename, body, sync_kb=sync_kb)
    except BedrockError as exc:
        status = 400 if exc.code in _UPLOAD_VALIDATION_CODES else 502
        if _wants_json():
            return jsonify(ok=False, reason=exc.code, message=exc.user_message), status
        return render_template("_upload_result.html", error=exc.user_message), status

    payload = {"ok": True, **result.to_dict()}
    if result.sync_warning:
        payload["message"] = result.sync_warning
        if _wants_json():
            return jsonify(**payload), 202
        return render_template(
            "_upload_result.html",
            result=result,
            warning=result.sync_warning,
        ), 202

    if _wants_json():
        return jsonify(**payload), 200
    return render_template("_upload_result.html", result=result), 200
