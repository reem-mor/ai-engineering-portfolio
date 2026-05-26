from fastapi import APIRouter, HTTPException, status

from app.core.config import settings
from app.rag.embeddings import OpenAIEmbeddingProvider
from app.schemas.document_index_schema import (
    DocumentIndexResponse,
    DocumentListResponse,
)
from app.services.document_service import DocumentService

router = APIRouter(prefix="/documents", tags=["Documents"])


@router.get("/samples", response_model=DocumentListResponse)
def list_sample_documents() -> DocumentListResponse:
    try:
        service = DocumentService()
        files = service.list_supported_files(settings.sample_documents_dir)

        return DocumentListResponse(
            files=[file.name for file in files],
            file_count=len(files),
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error


@router.post("/index-samples", response_model=DocumentIndexResponse)
def index_sample_documents() -> DocumentIndexResponse:
    try:
        service = DocumentService(
            embedding_provider=OpenAIEmbeddingProvider(),
        )

        files = service.list_supported_files(settings.sample_documents_dir)

        if not files:
            raise ValueError("No sample documents found for indexing.")

        service.process_embed_and_index_files(files)

        return DocumentIndexResponse(
            status="success",
            indexed_files=[file.name for file in files],
            indexed_file_count=len(files),
            message="Sample documents were processed, embedded, and indexed into FAISS.",
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error

    except Exception as error:
        import traceback

        print("\n========== INDEX SAMPLE DOCUMENTS ERROR ==========")
        print(repr(error))
        traceback.print_exc()
        print("==================================================\n")

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unexpected error while indexing sample documents.",
        ) from error


@router.get("/uploaded", response_model=DocumentListResponse)
def list_uploaded_documents() -> DocumentListResponse:
    try:
        service = DocumentService()
        files = service.list_supported_files(settings.raw_data_dir)

        return DocumentListResponse(
            files=[file.name for file in files],
            file_count=len(files),
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error


@router.post("/index-uploaded", response_model=DocumentIndexResponse)
def index_uploaded_documents() -> DocumentIndexResponse:
    try:
        service = DocumentService(
            embedding_provider=OpenAIEmbeddingProvider(),
        )

        files = service.list_supported_files(settings.raw_data_dir)

        if not files:
            raise ValueError("No uploaded documents found for indexing.")

        service.process_embed_and_index_files(files)

        return DocumentIndexResponse(
            status="success",
            indexed_files=[file.name for file in files],
            indexed_file_count=len(files),
            message="Uploaded documents were processed, embedded, and indexed into FAISS.",
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error

    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unexpected error while indexing uploaded documents.",
        ) from error
