from pydantic import BaseModel, Field

from app.schemas.search_schema import SearchResult


class IncidentAnalysisRequest(BaseModel):
    description: str = Field(
        ...,
        min_length=10,
        max_length=4000,
        description="Description of the operational incident.",
    )
    affected_service: str | None = Field(
        default=None,
        max_length=100,
        description="Optional affected service name.",
    )
    environment: str | None = Field(
        default=None,
        max_length=50,
        description="Optional environment such as production, staging, or dev.",
    )
    top_k: int = Field(
        default=5,
        ge=1,
        le=10,
        description="Number of relevant chunks to retrieve.",
    )


class IncidentAnalysisResponse(BaseModel):
    incident_summary: str
    severity: str
    likely_causes: list[str]
    recommended_checks: list[str]
    missing_information: list[str]
    next_best_action: str
    escalation_recommendation: str
    sources: list[str]
    retrieved_chunks: list[SearchResult]
    confidence: str
    used_context: bool
