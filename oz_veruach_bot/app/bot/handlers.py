"""Telegram update handlers for Phase 0.

Handlers are intentionally thin and side-effect-light so they can be unit-tested with
mocked ``Update``/``Context`` objects (no live Telegram calls). Phase 0 ships ``/start``
onboarding and a safe echo; later phases route messages through the LangGraph node graph.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from app.bot.dispatch import dispatch_intent
from app.bot.router import route
from app.core.errors import user_fallback_message
from app.core.i18n import detect_language, t
from app.core.logging import get_logger
from app.core.settings import get_settings
from app.graph.router_node import classify as llm_classify

if TYPE_CHECKING:
    from telegram import Update
    from telegram.ext import ContextTypes

_log = get_logger("bot.handlers")

# Telegram hard-limits messages to 4096 chars; echo is truncated well below that.
_MAX_ECHO_LEN = 3500


async def start_command(update: Update, _context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle ``/start``: greet the user and explain capabilities.

    Phase 0 does not yet persist subscribers; that arrives with the repo layer.
    """
    message = update.effective_message
    if message is None:
        return
    user = update.effective_user
    language = detect_language(message.text)
    _log.info(
        "start_command",
        user_id=getattr(user, "id", None),
        language=language,
    )
    await message.reply_text(t("start", language))


async def myid_command(update: Update, _context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle ``/myid``: report the caller's numeric Telegram ID and role.

    Lets owners collect Alex's and Sagy's IDs without a third-party bot, then add them
    to the allowlists via env.
    """
    message = update.effective_message
    user = update.effective_user
    if message is None or user is None:
        return
    language = detect_language(message.text)
    settings = get_settings()
    if settings.is_owner(user.id):
        role = t("role_owner", language)
    elif settings.is_admin(user.id):
        role = t("role_admin", language)
    else:
        role = t("role_student", language)
    _log.info("myid_command", user_id=user.id, language=language)
    await message.reply_text(t("myid", language).format(id=user.id, role=role))


async def text_message(update: Update, _context: ContextTypes.DEFAULT_TYPE) -> None:
    """Route a non-command text message.

    Runs the deterministic keyword router first; recognized intents (Phase 1: schedule)
    are answered directly. Unrecognized text falls back to a safe echo until later phases
    add their intents. Errors become a localized fallback so no stack trace ever leaks.
    """
    message = update.effective_message
    if message is None:
        return
    text = (message.text or "").strip()
    language = detect_language(text)
    try:
        if not text:
            await message.reply_text(t("empty_message", language))
            return
        # Deterministic keyword fast-path first; fall back to the LLM router only when
        # it doesn't match (and only if a provider is configured).
        intent = route(text) or await llm_classify(text)
        if intent is not None:
            reply = await dispatch_intent(intent, language)
            if reply is not None:
                _log.info("intent_handled", intent=intent.name, scope=intent.scope)
                await message.reply_text(reply)
                return
        truncated = text[:_MAX_ECHO_LEN]
        await message.reply_text(f"{t('echo_prefix', language)}: {truncated}")
    except Exception:  # convert any failure into a safe user reply
        _log.exception("text_failed", user_id=getattr(update.effective_user, "id", None))
        await message.reply_text(user_fallback_message(language))


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Global error handler: log the exception and reply with a safe fallback."""
    _log.exception("unhandled_update_error", error=str(context.error))
    from telegram import Update as _Update  # local import keeps test mocks simple

    if isinstance(update, _Update) and update.effective_message is not None:
        language = detect_language(update.effective_message.text)
        await update.effective_message.reply_text(user_fallback_message(language))
