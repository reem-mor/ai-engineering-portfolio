from app.core.config import settings
from app.db.chat_repository import ChatRepository
from app.db.incident_repository import IncidentRepository
from app.schemas.chat_schema import ChatResponse
from app.schemas.incident_schema import IncidentAnalysisResponse


class HistoryService:
    def save_chat_interaction(self, question: str, response: ChatResponse, session_id: str | None = None) -> None:
        if not settings.database_enabled:
            return
        try:
            repository = ChatRepository()
            if session_id is None:
                session = repository.create_session(title=question[:80])
                session_id = session["id"]
            repository.save_message(session_id=session_id, role="user", content=question)
            assistant_message = repository.save_message(session_id=session_id, role="assistant", content=response.answer, confidence=response.confidence, used_context=response.used_context)
            repository.save_retrieval_logs(message_id=assistant_message["id"], retrieved_chunks=response.retrieved_chunks)
        except Exception:
            return

    def save_incident_analysis(self, description: str, response: IncidentAnalysisResponse, affected_service: str | None = None, environment: str | None = None) -> None:
        if not settings.database_enabled:
            return
        try:
            IncidentRepository().save_analysis(description=description, response=response, affected_service=affected_service, environment=environment)
        except Exception:
            return
