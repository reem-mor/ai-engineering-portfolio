from app.db.supabase_client import get_supabase_client
from app.schemas.incident_schema import IncidentAnalysisResponse


class IncidentRepository:
    def __init__(self) -> None:
        self.client = get_supabase_client()

    def save_analysis(self, description: str, response: IncidentAnalysisResponse, affected_service: str | None = None, environment: str | None = None) -> dict:
        result = self.client.table("incident_analyses").insert({"description": description, "affected_service": affected_service, "environment": environment, "severity": response.severity, "incident_summary": response.incident_summary, "likely_causes": response.likely_causes, "recommended_checks": response.recommended_checks, "missing_information": response.missing_information, "next_best_action": response.next_best_action, "escalation_recommendation": response.escalation_recommendation, "confidence": response.confidence, "used_context": response.used_context}).execute()
        return result.data[0]
