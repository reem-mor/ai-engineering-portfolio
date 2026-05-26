import traceback

from fastapi import APIRouter, HTTPException, status

from app.rag.rag_pipeline import RAGPipeline
from app.schemas.chat_schema import ChatRequest, ChatResponse
from app.services.history_service import HistoryService

router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post("", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    """
    Answer a user question using the indexed FAISS knowledge base.

    Flow:
    1. Validate the request.
    2. Run the RAG pipeline.
    3. Save chat history only if history/database is available.
    4. Return answer + retrieved sources.
    """
    try:
        pipeline = RAGPipeline.create_default()

        response = pipeline.answer_question(
            question=request.question,
            top_k=request.top_k,
        )

        # History should never break the main RAG response.
        try:
            HistoryService().save_chat_interaction(
                question=request.question,
                response=response,
            )
        except Exception as history_error:
            print("\n========== CHAT HISTORY SAVE WARNING ==========")
            print(repr(history_error))
            traceback.print_exc()
            print("===============================================\n")

        return response

    except FileNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "FAISS index was not found. "
                "Go to Knowledge Base and index documents before using chat."
            ),
        ) from error

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error

    except Exception as error:
        print("\n========== CHAT ROUTE ERROR ==========")
        print(repr(error))
        traceback.print_exc()
        print("======================================\n")

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error while answering the question: {error}",
        ) from error
