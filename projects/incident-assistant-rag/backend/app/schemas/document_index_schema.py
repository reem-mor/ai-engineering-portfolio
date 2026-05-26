from pydantic import BaseModel


class DocumentIndexResponse(BaseModel):
    status: str
    indexed_files: list[str]
    indexed_file_count: int
    message: str


class DocumentListResponse(BaseModel):
    files: list[str]
    file_count: int
