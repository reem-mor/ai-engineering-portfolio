export interface PiterSections {
  priority: string;
  investigation: string;
  triage_plan: string[];
  escalation: string[];
  resolution: string;
  business_impact: string;
  sources: string;
  confidence: string;
}

export interface AnswerSections {
  summary: string;
  steps: string[];
  escalation: string[];
  why: string;
  piter_sections?: PiterSections;
}

export interface Citation {
  snippet: string;
  source_uri: string;
  source_label: string;
  index: number;
  score?: number | null;
  chunk_index?: number | null;
  preview?: string;
}

export interface RagAnswer {
  answer: string;
  answer_sections?: AnswerSections;
  citations: Citation[];
  session_id: string | null;
  grounded: boolean;
  latency_ms: number;
  matched_runbook: string | null;
}

export interface WorkflowAlert {
  id: string;
  severity: string;
  service: string;
  title: string;
  firedAt: string;
  source: string;
  question: string;
  matchedRunbook?: string;
  actions?: string[];
  decision?: "auto-resolve" | "tier1-resolve" | "escalate" | string;
  decisionReason?: string;
  baselineMin: number;
  assistedMin: number;
  impactPerMin: number;
}

export interface BootstrapPayload {
  ok: boolean;
  examples: string[];
  example_groups: Record<string, string[]>;
  workflow_alerts: Record<string, unknown>[];
  max_len: number;
  model_label: string;
  kb_id: string;
  s3_bucket: string;
  s3_prefix: string;
  max_upload_mb: number;
  allowed_types: string[];
  sync_kb_default: boolean;
  csrf_token?: string;
  spa_enabled?: boolean;
}

export interface DeploymentMatch {
  service?: string;
  environment?: string;
  deployed_at?: string;
  change?: string;
  deployed_by?: string;
  hop?: string;
  [key: string]: unknown;
}

export interface OwnerContext {
  owner_team?: string;
  escalation_path?: string;
  pagerduty_service?: string;
  display_name?: string;
  service?: string;
  environment?: string;
  warning?: string;
  error?: string;
  [key: string]: unknown;
}

export interface SimilarIncident {
  incident_id?: string;
  date?: string;
  severity?: string;
  root_cause?: string;
  mttr_minutes?: number;
  customer_impact?: string;
  resolution?: string;
  [key: string]: unknown;
}

export interface TriageEnrichment {
  deployments?: DeploymentMatch[];
  likely_deploy_correlation?: boolean;
  owner_team?: string | OwnerContext;
  escalation_path?: string;
  pagerduty_service?: string;
  revenue_impact_usd_per_hour?: number;
  player_impact_pct?: number;
  regulatory_flag?: boolean;
  escalation_minutes?: number;
  similar_incidents?: SimilarIncident[];
  tools?: Record<string, unknown>[];
  raw_tool_outputs?: string[];
  dependency_hop?: { depends_on?: string[]; depended_by?: string[] };
  [key: string]: unknown;
}

export interface ExternalStatus {
  provider?: string;
  status?: string;
  summary?: string;
  url?: string;
}

export interface WorkflowTriagePayload {
  ok: boolean;
  result?: RagAnswer;
  alert?: Record<string, unknown> | null;
  question?: string;
  actions?: string[];
  matched_runbook?: string | null;
  effective_decision?: string;
  effective_reason?: string;
  saved_min?: number;
  impact_avoided?: number;
  model_label?: string;
  enrichment?: TriageEnrichment | null;
  owner_team?: string | OwnerContext | null;
  similar_incidents?: SimilarIncident[] | null;
  external_status?: ExternalStatus | null;
  session_id?: string | null;
  message?: string;
  reason?: string;
}

export interface UploadResultPayload {
  ok: boolean;
  message?: string;
  reason?: string;
  partial?: boolean;
  sync_warning?: string;
  filename?: string;
  s3_key?: string;
  s3_uri?: string;
  size_bytes?: number;
  sync_started?: boolean;
  ingestion_job_id?: string | null;
}

/** Demo MTTR and dollar estimates by severity — not real financial data. */
export const SEVERITY_IMPACT: Record<string, { minutes: number; dollars: number }> = {
  P1: { minutes: 30, dollars: 5000 },
  P2: { minutes: 15, dollars: 2500 },
  P3: { minutes: 5, dollars: 500 },
};

export function severityImpact(severity: string): { minutes: number; dollars: number } {
  const key = (severity || "P3").toUpperCase();
  return SEVERITY_IMPACT[key] ?? SEVERITY_IMPACT.P3;
}
