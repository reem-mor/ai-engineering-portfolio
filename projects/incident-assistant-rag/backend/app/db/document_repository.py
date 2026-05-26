from app.db.supabase_client import get_supabase_client


class DocumentRepository:
    def __init__(self) -> None:
        self.client = get_supabase_client()

    def create_document(self, filename: str, saved_as: str | None, source_type: str, content_type: str | None = None, size_bytes: int | None = None, status: str = "uploaded", chunk_count: int = 0) -> dict:
        result = self.client.table("documents").insert({"filename": filename, "saved_as": saved_as, "source_type": source_type, "content_type": content_type, "size_bytes": size_bytes, "status": status, "chunk_count": chunk_count}).execute()
        return result.data[0]

    def list_documents(self) -> list[dict]:
        result = self.client.table("documents").select("*").order("created_at", desc=True).execute()
        return result.data
