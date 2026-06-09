export type Priority = "P1" | "P2" | "P3" | "P4";

export type PageKey = "home" | "analytics" | "history" | "analyzer" | "system";

export type HealthResponse = {
  status: "ok" | "degraded" | string;
  checks?: {
    app?: string;
    s3?: string;
    bedrock?: string;
  };
};

export type AlertRow = {
  alert_id: string;
  seconds_offset: string;
  timestamp: string;
  environment: string;
  service: string;
  severity: string;
  title: string;
  status: string;
  source: string;
  is_noise_candidate?: string;
  is_duplicate_candidate?: string;
  correlation_id?: string;
  incident_candidate_id?: string;
  is_trigger?: string;
  [key: string]: string | undefined;
};

export type AlertStreamResponse = {
  ok: boolean;
  total: number;
  label: string;
  duration_seconds: number;
  by_severity: Record<string, number>;
  noise_suppressed: number;
  active_count: number;
  active_alerts?: AlertRow[];
  warning_signals?: number;
  p1_trigger?: AlertRow | null;
  p1_count?: number;
  rows?: AlertRow[];
  active_only?: boolean;
};

export type BootstrapResponse = {
  ok: boolean;
  csrf_token?: string;
  kb_id?: string;
  s3_bucket?: string;
  s3_prefix?: string;
  execution_mode_hint?: string;
  notification?: {
    mode?: string;
    require_confirmation?: boolean;
    live_dispatch_enabled?: boolean;
    dispatch_ready?: boolean;
    email_configured?: boolean;
    sms_configured?: boolean;
    allowlist_count?: number;
    demo_email_configured?: boolean;
    demo_sms_configured?: boolean;
  };
  alert_stream?: AlertStreamResponse;
};

export type Investigation = {
  id: string;
  conclusion: string;
  conclusionDetail: string;
  alertTime: string;
  alert: string;
  service: string;
  environment: string;
  entities: string;
  source: string;
  status: string;
  priority: Priority;
  impact: string;
};

export type InvestigationsResponse = {
  ok: boolean;
  investigations: Investigation[];
  summary: {
    total?: number;
    active_count?: number;
    noise_suppressed?: number;
    p1_trigger?: AlertRow | null;
  };
};

export type PiterBlock = {
  priority: string;
  investigation: string;
  triage: string;
  escalation: string;
  resolution: string;
};

export type PiterStages = {
  priority?: string;
  investigation?: string;
  triage?: string;
  escalation?: string;
  resolution?: string;
};

export type Source = {
  document?: string;
  excerpt?: string;
  score?: number | null;
  source_uri?: string;
};

export type ToolResult = {
  name: string;
  result: unknown;
};

export type TriageResponse = {
  ok: boolean;
  answer?: string;
  piter?: PiterBlock;
  business_impact?: string;
  confidence?: string;
  sources?: Source[];
  tool_results?: ToolResult[];
  memory?: { session_id?: string; last_question?: string };
  session_id?: string;
  mode?: string;
  fallback_used?: boolean;
  message?: string;
  reason?: string;
  priority?: string;
  piter_stages?: PiterStages;
  alert?: Record<string, unknown>;
  suspect_deployment?: unknown;
  similar_incidents?: unknown[];
  escalation_policy?: Record<string, unknown>;
};

export type ChatResponse = TriageResponse;

export type HistoryMessage = {
  role: "user" | "assistant";
  content: string;
  ts?: number;
  mode?: string;
};

export type HistoryResponse = {
  ok: boolean;
  session_id: string;
  messages: HistoryMessage[];
  count: number;
};

export type AnalyzePayload = {
  service: string;
  environment: string;
  severity: string;
  symptom: string;
  description?: string;
  alert_time: string;
  session_id?: string;
  alert_id?: string;
};

export type MetricsResult = Record<string, unknown> & {
  ok?: boolean;
  error?: string;
  safe_preview_only?: boolean;
  sends_notifications?: boolean;
};

export type EscalationNotifyPayload = {
  channel: "email" | "sms" | "whatsapp";
  incident_id: string;
  service: string;
  severity: string;
  confirmation_token: string;
  message?: string;
  idempotency_key?: string;
  escalation_context?: Record<string, unknown>;
};

export type EscalationNotifyResponse = {
  ok: boolean;
  sent?: boolean;
  blocked?: boolean;
  mode?: string;
  channel?: string;
  message_id?: string;
  recipient?: string;
  message?: string;
  reasons?: string[];
  timestamp?: string;
};

export type AgentDecision = {
  id: string;
  at: number;
  text: string;
  kind: "noise" | "group" | "escalation" | "p1" | "info";
};

export type ChatDockPrefill = {
  message?: string;
  sessionId?: string | null;
  alert?: Partial<AlertRow>;
};

export type PersistedInvestigation = {
  session_id: string;
  created_at?: number;
  alert_id?: string;
  timestamp?: string;
  severity?: string;
  service?: string;
  environment?: string;
  symptom?: string;
  mode?: string;
  fallback_used?: boolean;
};

export type IncidentsHistoryResponse = {
  ok: boolean;
  investigations: PersistedInvestigation[];
  count: number;
};

export type IncidentDetailResponse = {
  ok: boolean;
  session_id: string;
  created_at?: number;
  alert: Record<string, unknown>;
  triage_card: Record<string, unknown>;
  citations: unknown[];
  tool_outputs: Record<string, unknown>;
  followups: Array<{ question: string; answer: Record<string, unknown>; ts?: number }>;
};
