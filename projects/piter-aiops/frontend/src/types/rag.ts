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
  use_bedrock?: boolean;
  rag_backend?: string;
  execution_mode_hint?: string;
  notification?: {
    mode: string;
    require_confirmation: boolean;
    max_sends_per_incident: number;
    live_dispatch_enabled?: boolean;
    sms_configured?: boolean;
    email_configured?: boolean;
    allowlist_count?: number;
    demo_sms_configured?: boolean;
    demo_email_configured?: boolean;
  };
  alert_stream?: AlertStreamSummary;
}

export interface AlertStreamSummary {
  total: number;
  label: string;
  duration_seconds: number;
  by_severity: Record<string, number>;
  noise_suppressed: number;
  warning_signals: number;
  p1_trigger?: Record<string, string> | null;
  p1_count: number;
}

export interface TriageCitation {
  document: string;
  excerpt: string;
  score?: number | null;
}

export interface TriageCard {
  answer: string;
  citations: TriageCitation[];
  recommended_steps: string[];
  suspect_deploys: unknown[];
  suspect_deployment?: unknown;
  owner: Record<string, unknown>;
  impact: Record<string, unknown>;
  similar_incidents: SimilarIncident[];
  grounded: boolean;
  matched_runbook: string | null;
  session_id: string;
  memory_used: boolean;
  mode: string;
  alert?: Record<string, unknown>;
  priority: string;
  requires_escalation: boolean;
  piter_stages?: Record<string, string>;
}

export interface FollowUpResult {
  answer: string;
  session_id: string;
  memory_used: boolean;
  mode: string;
  kind?: string;
  citations?: TriageCitation[];
  owner?: Record<string, unknown>;
  impact?: Record<string, unknown>;
}

export interface KbDocumentMeta {
  id: string;
  title: string;
  doc_type: string;
  services: string;
  environments: string;
  severity_applicable: string;
  tags: string;
  last_updated: string;
  author: string;
  version: string;
  indexed: boolean;
  sync_status: string;
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

export interface EscalationNotifyResult {
  ok: boolean;
  sent: boolean;
  mode?: string;
  channel?: string;
  blocked?: boolean;
  reasons?: string[];
  recipient?: string;
  message_id?: string;
  idempotency_key?: string;
  error?: string;
  message?: string;
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
