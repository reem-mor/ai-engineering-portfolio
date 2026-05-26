import { apiRequest } from "./client";
import type { IncidentAnalysisRequest, IncidentAnalysisResponse } from "../types/incident";

export function analyzeIncident(request: IncidentAnalysisRequest): Promise<IncidentAnalysisResponse> {
  return apiRequest<IncidentAnalysisResponse>("/incident/analyze", { method: "POST", body: request });
}
