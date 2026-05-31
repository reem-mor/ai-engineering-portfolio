export interface Citation {
  snippet: string;
  source_uri: string;
  source_label: string;
  index: number;
}

export interface RagAnswer {
  answer: string;
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
