"""Thin Telegram long-polling adapter over the agent core.

Keeps almost no logic of its own: free text goes to the :class:`Dispatcher`;
``/submit`` runs the guided :class:`SubmissionSession`. Per-chat submission
sessions are held in ``bot_data`` so the email send flow stays deterministic and
out of the LLM's hands.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, cast

from course_assistant.agent.dispatcher import Dispatcher, detect_language
from course_assistant.config import Settings, get_settings
from course_assistant.homework.email import build_email_service
from course_assistant.homework.session import SubmissionSession

if TYPE_CHECKING:
    from telegram import Update
    from telegram.ext import ContextTypes

_HELP = {
    "he": (
        "שלום! אני העוזר של קורס עוז ורוח.\n"
        "אפשר לשאול אותי על הקלטות, מצגות, שיעורי בית וקוד לפי מספר שיעור, "
        "או על תוכן הקורס.\n"
        "פקודות: /submit להגשת שיעורי בית, /help לעזרה."
    ),
    "en": (
        "Hi! I'm the Oz VeRuach course assistant.\n"
        "Ask me about recordings, slides, homework, or code by lesson number, "
        "or about course content.\n"
        "Commands: /submit to submit homework, /help for help."
    ),
}

_SESSIONS_KEY = "submission_sessions"


def _sessions(context: ContextTypes.DEFAULT_TYPE) -> dict[int, SubmissionSession]:
    data = context.application.bot_data.setdefault(_SESSIONS_KEY, {})
    return cast("dict[int, SubmissionSession]", data)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = update.message.text if update.message else ""
    await update.message.reply_text(_HELP[detect_language(text or "")])  # type: ignore[union-attr]


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(_HELP["he"] + "\n\n" + _HELP["en"])  # type: ignore[union-attr]


async def submit_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    settings: Settings = context.application.bot_data["settings"]
    lang = detect_language(update.message.text or "")  # type: ignore[union-attr]
    session = SubmissionSession(
        settings=settings,
        email_service=build_email_service(settings),
        lang=lang,
    )
    _sessions(context)[update.effective_chat.id] = session  # type: ignore[union-attr]
    await update.message.reply_text(session.start())  # type: ignore[union-attr]


async def text_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id  # type: ignore[union-attr]
    text = update.message.text or ""  # type: ignore[union-attr]
    sessions = _sessions(context)
    session = sessions.get(chat_id)
    if session is not None and not session.done:
        reply = session.handle(text)
        if session.done:
            sessions.pop(chat_id, None)
        await update.message.reply_text(reply)  # type: ignore[union-attr]
        return
    dispatcher: Dispatcher = context.application.bot_data["dispatcher"]
    await update.message.reply_text(dispatcher.respond(text))  # type: ignore[union-attr]


def build_application(settings: Settings, dispatcher: Dispatcher) -> Any:
    """Construct the Telegram Application with handlers wired up."""
    from telegram.ext import (
        Application,
        CommandHandler,
        MessageHandler,
        filters,
    )

    if settings.telegram_bot_token is None:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is not configured.")

    app = Application.builder().token(settings.telegram_bot_token.get_secret_value()).build()
    app.bot_data["settings"] = settings
    app.bot_data["dispatcher"] = dispatcher
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("submit", submit_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_message))
    return app


def main() -> None:  # pragma: no cover - live entry point
    """Build everything from settings and run the bot in long-polling mode."""
    from course_assistant.drive.service import GoogleDriveService
    from course_assistant.rag.embeddings import OpenAIEmbedder
    from course_assistant.rag.stores import ChromaVectorStore

    settings = get_settings()
    drive = GoogleDriveService(settings)
    store = ChromaVectorStore(OpenAIEmbedder(settings), persist_dir=settings.chroma_dir)
    dispatcher = Dispatcher(drive, store, settings)
    app = build_application(settings, dispatcher)
    app.run_polling()


__all__ = ["build_application", "main"]
