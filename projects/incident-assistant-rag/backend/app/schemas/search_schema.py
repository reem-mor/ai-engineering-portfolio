from pydantic import BaseModel, Field


class SearchResult(BaseModel):
    chunk_id: str
    source_file: str
    chunk_index: int
    text: str
    score: float = Field(..., ge=0.0)
