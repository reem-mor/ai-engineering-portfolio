import type {
  AlertStreamSummary,
  BootstrapPayload,
  EscalationContext,
  EscalationNotifyResult,
  FollowUpResult,
  KbDocumentMeta,
  RagAnswer,
  SessionHistoryPayload,
  TriageCard,
  UploadResultPayload,
  WorkflowAlert,
  WorkflowTriagePayload,
} from "@/types/rag";

const JSON_HEADERS: HeadersInit = {
  Accept: "application/json",
  "Content-Type": "application/json",
};

let csrfToken: string | undefined;

export function setCsrfToken(token: string | undefined) {
  csrfToken = token;
}

function withCsrf(headers: HeadersInit = {}): HeadersInit {
  if (!csrfToken) return headers;
  return { ...headers, "X-CSRFToken": csrfToken };
}

async function parseJson<T>(response: Response): Promise<T> {
  const data = (await response.json()) as T & { message?: string };
  if (!response.ok) {
    const msg =
      typeof data === "object" && data && "message" in data && data.message
        ? String(data.message)
        : response.statusText;
    throw new Error(msg || `Request failed (${response.status})`);
  }
  return data;
}

export function normalizeWorkflowAlert(raw: Record<string, unknown>): WorkflowAlert {
  return {
    id: String(raw.id ?? ""),
    severity: String(raw.severity ?? ""),
    service: String(raw.service ?? ""),
    title: String(raw.title ?? ""),
    firedAt: String(raw.fired_at ?? raw.firedAt ?? ""),
    source: String(raw.source ?? ""),
    question: String(raw.question ?? ""),
    matchedRunbook: raw.matched_runbook
      ? String(raw.matched_runbook)
      : raw.matchedRunbook
        ? String(raw.matchedRunbook)
        : undefined,
    actions: Array.isArray(raw.actions)
      ? raw.actions.map((a) => String(a))
      : undefined,
    decision: raw.decision ? String(raw.decision) : undefined,
    decisionReason: raw.decision_reason
      ? String(raw.decision_reason)
      : raw.decisionReason
        ? String(raw.decisionReason)
        : undefined,
    baselineMin: Number(raw.baseline_min ?? raw.baselineMin ?? 0),
    assistedMin: Number(raw.assisted_min ?? raw.assistedMin ?? 0),
    impactPerMin: Number(raw.impact_per_min ?? raw.impactPerMin ?? 0),
  };
}

export async function fetchBootstrap(): Promise<BootstrapPayload> {
  const response = await fetch("/api/bootstrap", {
    headers: { Accept: "application/json" },
    credentials: "same-origin",
  });
  const data = await parseJson<BootstrapPayload>(response);
  if (data.csrf_token) setCsrfToken(data.csrf_token);
  return data;
}

export type InvestigationRow = {
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
  priority: "P1" | "P2" | "P3" | "P4";
  impact: string;
};

export async function fetchInvestigations(limit = 12): Promise<{
  investigations: InvestigationRow[];
  summary: Record<string, unknown>;
}> {
  const response = await fetch(`/api/investigations?limit=${limit}`, {
    headers: { Accept: "application/json" },
    credentials: "same-origin",
  });
  const data = await parseJson<{
    ok: boolean;
    investigations: InvestigationRow[];
    summary: Record<string, unknown>;
  }>(response);
  return { investigations: data.investigations, summary: data.summary };
}

export async function fetchAlertStream(
  mode: "none" | "include" | "active" = "none",
): Promise<AlertStreamSummary & { rows?: Record<string, string>[] }> {
  const qs =
    mode === "active" ? "?active=true" : mode === "include" ? "?include_rows=true" : "";
  const response = await fetch(`/api/alert-stream${qs}`, {
    headers: { Accept: "application/json" },
    credentials: "same-origin",
  });
  const data = await parseJson<{ ok: boolean } & AlertStreamSummary & { rows?: Record<string, string>[] }>(response);
  return data;
}

export async function fetchKbManifest(): Promise<{ documents: KbDocumentMeta[]; sections: Record<string, KbDocumentMeta[]> }> {
  const response = await fetch("/api/kb/manifest", {
    headers: { Accept: "application/json" },
    credentials: "same-origin",
  });
  const data = await parseJson<{ ok: boolean; documents: KbDocumentMeta[]; sections: Record<string, KbDocumentMeta[]> }>(
    response,
  );
  return { documents: data.documents, sections: data.sections };
}

export async function runTriageCard(
  alert: Record<string, unknown>,
  sessionId?: string | null,
): Promise<TriageCard> {
  const body: Record<string, unknown> = { ...alert };
  if (sessionId) body.session_id = sessionId;

  const response = await fetch("/api/triage", {
    method: "POST",
    headers: withCsrf(JSON_HEADERS),
    credentials: "same-origin",
    body: JSON.stringify(body),
  });
  const data = await parseJson<{ ok: boolean } & TriageCard>(response);
  if (!data.ok) throw new Error("Triage failed");
  return data;
}

export async function followUp(sessionId: string, question: string): Promise<FollowUpResult> {
  const response = await fetch("/api/follow-up", {
    method: "POST",
    headers: withCsrf(JSON_HEADERS),
    credentials: "same-origin",
    body: JSON.stringify({ session_id: sessionId, question }),
  });
  const data = await parseJson<{ ok: boolean } & FollowUpResult>(response);
  if (!data.ok) throw new Error("Follow-up failed");
  return data;
}

export async function fetchSessionHistory(sessionId: string): Promise<SessionHistoryPayload> {
  const response = await fetch(`/api/sessions/${encodeURIComponent(sessionId)}/history`, {
    headers: { Accept: "application/json" },
    credentials: "same-origin",
  });
  return parseJson<SessionHistoryPayload>(response);
}

export async function notifyEscalation(payload: {
  channel: "sms" | "email" | "whatsapp";
  incident_id: string;
  service: string;
  severity: string;
  confirmation_token: string;
  message?: string;
  idempotency_key?: string;
  escalation_context?: EscalationContext;
}): Promise<EscalationNotifyResult> {
  const response = await fetch("/api/escalation/notify", {
    method: "POST",
    headers: withCsrf(JSON_HEADERS),
    credentials: "same-origin",
    body: JSON.stringify(payload),
  });
  const data = (await response.json()) as EscalationNotifyResult;
  if (!response.ok && !data.message && data.reasons?.length) {
    data.message = data.reasons.join("; ");
  }
  return data;
}

export function executionModeLabel(
  mode: string | undefined,
  ragBackend: string | undefined,
  useBedrock: boolean | undefined,
): string {
  if (mode === "local" || useBedrock === false) return "Local fallback";
  if (ragBackend === "retrieve_and_generate") return "Direct Bedrock KB";
  if (mode === "bedrock") return "Bedrock Agent";
  return "Bedrock Agent / KB";
}

export function triageToRagAnswer(card: TriageCard): RagAnswer {
  return {
    answer: card.answer,
    citations: (card.citations ?? []).map((c, index) => ({
      snippet: c.excerpt,
      source_uri: c.document,
      source_label: c.document,
      index: index + 1,
      score: c.score ?? null,
    })),
    session_id: card.session_id,
    grounded: card.grounded,
    latency_ms: 0,
    matched_runbook: card.matched_runbook,
  };
}

export async function askQuestion(
  question: string,
  sessionId?: string | null,
): Promise<RagAnswer> {
  const body: { question: string; session_id?: string } = { question };
  if (sessionId) body.session_id = sessionId;

  const response = await fetch("/ask", {
    method: "POST",
    headers: withCsrf(JSON_HEADERS),
    credentials: "same-origin",
    body: JSON.stringify(body),
  });
  const data = await parseJson<{ ok: boolean } & RagAnswer>(response);
  if (!data.ok) throw new Error("Ask failed");
  const { ok: _ok, ...answer } = data;
  return answer;
}

export async function triageAlert(
  alertId: string,
  question?: string,
  sessionId?: string | null,
): Promise<WorkflowTriagePayload> {
  const body: { alert_id: string; question: string; session_id?: string } = {
    alert_id: alertId,
    question: question ?? "",
  };
  if (sessionId) body.session_id = sessionId;

  const response = await fetch("/api/workflow/triage", {
    method: "POST",
    headers: withCsrf(JSON_HEADERS),
    credentials: "same-origin",
    body: JSON.stringify(body),
  });
  const payload = await parseJson<WorkflowTriagePayload>(response);
  const sid = payload.result?.session_id ?? payload.session_id ?? null;
  return { ...payload, session_id: sid };
}

export async function uploadDocument(
  file: File,
  syncKb: boolean,
): Promise<UploadResultPayload> {
  const body = new FormData();
  body.append("document", file);
  if (syncKb) body.append("sync_kb", "on");

  const response = await fetch("/documents/upload?format=json", {
    method: "POST",
    credentials: "same-origin",
    body,
  });
  const data = await parseJson<UploadResultPayload>(response);
  if (response.status === 202 && data.ok) {
    return {
      ...data,
      message: data.sync_warning ?? data.message ?? "Uploaded; Knowledge Base sync pending.",
    };
  }
  return data;
}
