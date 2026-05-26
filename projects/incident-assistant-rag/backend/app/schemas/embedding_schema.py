from pydantic import BaseModel

from app.schemas.chunk_schema import DocumentChunk


class EmbeddedChunk(BaseModel):
    chunk: DocumentChunk
    embedding: list[float]
