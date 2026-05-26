from pydantic import BaseModel


class DocumentChunk(BaseModel):
    chunk_id: str
    source_file: str
    chunk_index: int
    text: str
