import type { SearchResult } from "./common";
export type IncidentAnalysisRequest = { description: string; affected_service?: string; environment?: string; top_k: number; };
export type IncidentAnalysisResponse = { incident_summary: string; severity: string; likely_causes: string[]; recommended_checks: string[]; missing_information: string[]; next_best_action: string; escalation_recommendation: string; sources: string[]; confidence: "high" | "medium" | "low" | "none"; used_context: boolean; retrieved_chunks: SearchResult[]; };
