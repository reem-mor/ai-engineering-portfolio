from pydantic import BaseModel, Field

from app.schemas.search_schema import SearchResult


class ChatRequest(BaseModel):
    question: str = Field(..., min_length=1)
    top_k: int = Field(default=5, ge=1, le=10)


class ChatResponse(BaseModel):
    answer: str
    sources: list[str]
    retrieved_chunks: list[SearchResult]
    confidence: str
    used_context: bool
