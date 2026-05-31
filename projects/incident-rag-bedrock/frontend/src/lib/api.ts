import type {
  BootstrapPayload,
  RagAnswer,
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
): Promise<WorkflowTriagePayload> {
  const response = await fetch("/api/workflow/triage", {
    method: "POST",
    headers: withCsrf(JSON_HEADERS),
    credentials: "same-origin",
    body: JSON.stringify({ alert_id: alertId, question: question ?? "" }),
  });
  return parseJson<WorkflowTriagePayload>(response);
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
