import traceback

from fastapi import APIRouter, HTTPException, status

from app.reasoning.incident_reasoner import IncidentReasoner
from app.schemas.incident_schema import (
    IncidentAnalysisRequest,
    IncidentAnalysisResponse,
)
from app.services.history_service import HistoryService

router = APIRouter(prefix="/incident", tags=["Incident Analysis"])


@router.post("/analyze", response_model=IncidentAnalysisResponse)
def analyze_incident(request: IncidentAnalysisRequest) -> IncidentAnalysisResponse:
    """
    Analyze an operational incident using the indexed RAG knowledge base.

    History/database saving is optional and must not break the main response.
    """
    try:
        reasoner = IncidentReasoner.create_default()

        response = reasoner.analyze(
            description=request.description,
            affected_service=request.affected_service,
            environment=request.environment,
            top_k=request.top_k,
        )

        # Database/history is optional. Never let it break incident analysis.
        try:
            HistoryService().save_incident_analysis(
                description=request.description,
                response=response,
                affected_service=request.affected_service,
                environment=request.environment,
            )
        except Exception as history_error:
            print("\n========== INCIDENT HISTORY SAVE WARNING ==========")
            print(repr(history_error))
            traceback.print_exc()
            print("===================================================\n")

        return response

    except FileNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "FAISS index was not found. "
                "Go to Knowledge Base and index documents before analyzing incidents."
            ),
        ) from error

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error

    except Exception as error:
        print("\n========== INCIDENT ANALYSIS ERROR ==========")
        print(repr(error))
        traceback.print_exc()
        print("============================================\n")

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error while analyzing the incident: {error}",
        ) from error
