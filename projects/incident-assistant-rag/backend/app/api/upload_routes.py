from fastapi import APIRouter, File, HTTPException, UploadFile, status

from app.core.config import settings
from app.db.document_repository import DocumentRepository
from app.schemas.upload_schema import UploadResponse
from app.services.upload_service import UploadService

router = APIRouter(prefix="/upload", tags=["Upload"])


@router.post("", response_model=UploadResponse)
async def upload_document(file: UploadFile = File(...)) -> UploadResponse:
    try:
        saved_filename, size_bytes = await UploadService().save_upload(file)
        if settings.database_enabled:
            try:
                DocumentRepository().create_document(filename=file.filename or "unknown", saved_as=saved_filename, source_type="uploaded", content_type=file.content_type, size_bytes=size_bytes, status="uploaded")
            except Exception:
                pass
        return UploadResponse(filename=file.filename or "unknown", saved_as=saved_filename, content_type=file.content_type, size_bytes=size_bytes, status="uploaded")
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error)) from error
