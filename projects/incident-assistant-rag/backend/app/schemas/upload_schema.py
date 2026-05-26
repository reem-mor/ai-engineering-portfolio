from pydantic import BaseModel


class UploadResponse(BaseModel):
    filename: str
    saved_as: str
    content_type: str | None
    size_bytes: int
    status: str
