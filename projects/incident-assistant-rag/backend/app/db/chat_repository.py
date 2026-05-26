from app.db.supabase_client import get_supabase_client
from app.schemas.search_schema import SearchResult


class ChatRepository:
    def __init__(self) -> None:
        self.client = get_supabase_client()

    def create_session(self, title: str = "New chat") -> dict:
        result = self.client.table("chat_sessions").insert({"title": title}).execute()
        return result.data[0]

    def save_message(self, session_id: str, role: str, content: str, confidence: str | None = None, used_context: bool = False) -> dict:
        result = self.client.table("chat_messages").insert({"session_id": session_id, "role": role, "content": content, "confidence": confidence, "used_context": used_context}).execute()
        return result.data[0]

    def save_retrieval_logs(self, message_id: str, retrieved_chunks: list[SearchResult]) -> None:
        if not retrieved_chunks:
            return
        rows = [{"message_id": message_id, "chunk_id": chunk.chunk_id, "source_file": chunk.source_file, "chunk_index": chunk.chunk_index, "score": chunk.score, "chunk_preview": chunk.text[:500]} for chunk in retrieved_chunks]
        self.client.table("retrieval_logs").insert(rows).execute()
