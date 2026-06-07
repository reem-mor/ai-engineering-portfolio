import { CheckCircle2, FileSpreadsheet, FileText, ShieldAlert, X } from "lucide-react";
import { useState } from "react";
import { notifyEscalation } from "@/lib/api";
import type { EscalationContext } from "@/types/rag";
import type { Citation, EscalationNotifyResult } from "@/types/rag";
import { classNames } from "@/lib/ui-utils";

export type ChatTurn = {
  role: "user" | "assistant";
  text: string;
  citations?: Citation[];
};

const DOC_TYPE_TONE: Record<string, string> = {
  runbook: "cyan",
  policy: "purple",
  incident: "red",
  environment: "blue",
  glossary: "teal",
  csv: "green",
  json: "amber",
  md: "cyan",
  txt: "slate",
  pdf: "red",
  docx: "blue",
};

export function DocTypeBadge({ type }: { type: string }) {
  const key = type.toLowerCase().replace(/^\./, "");
  const tone = DOC_TYPE_TONE[key] ?? "slate";
  const Icon = key === "csv" ? FileSpreadsheet : FileText;
  return (
    <span
      className={classNames(
        "inline-flex items-center gap-1 rounded-md border px-2 py-0.5 text-[11px] font-medium uppercase tracking-wide",
        tone === "cyan" && "border-cyan-400/30 bg-cyan-400/10 text-cyan-100",
        tone === "purple" && "border-violet-400/30 bg-violet-400/10 text-violet-100",
        tone === "red" && "border-red-400/30 bg-red-400/10 text-red-100",
        tone === "blue" && "border-blue-400/30 bg-blue-400/10 text-blue-100",
        tone === "teal" && "border-teal-400/30 bg-teal-400/10 text-teal-100",
        tone === "green" && "border-emerald-400/30 bg-emerald-400/10 text-emerald-100",
        tone === "amber" && "border-amber-400/30 bg-amber-400/10 text-amber-100",
        tone === "slate" && "border-slate-500/30 bg-slate-500/10 text-slate-200",
      )}
    >
      <Icon className="size-3" />
      {type}
    </span>
  );
}

export function ChatThread({
  turns,
  loading,
  emptyHint,
}: {
  turns: ChatTurn[];
  loading?: boolean;
  emptyHint: string;
}) {
  if (!turns.length && !loading) {
    return (
      <p className="text-sm leading-relaxed text-slate-500">{emptyHint}</p>
    );
  }
  return (
    <div className="space-y-3">
      {turns.map((turn, index) => (
        <div
          key={`${turn.role}-${index}`}
          className={classNames(
            "max-w-[95%] rounded-lg px-3 py-2.5 text-sm leading-relaxed",
            turn.role === "user"
              ? "ml-auto border border-violet-400/30 bg-violet-500/15 text-violet-50"
              : "mr-auto border border-slate-700 bg-slate-900/80 text-slate-200",
          )}
        >
          <div className="mb-1 text-[10px] font-semibold uppercase tracking-wider text-slate-500">
            {turn.role === "user" ? "Operator" : "PITER Agent"}
          </div>
          <div className="whitespace-pre-wrap">{turn.text}</div>
          {turn.citations && turn.citations.length > 0 && (
            <div className="mt-2 border-t border-slate-700/80 pt-2 text-[11px] text-slate-400">
              <span className="font-medium text-slate-500">Sources: </span>
              {turn.citations.slice(0, 3).map((c) => c.source_label).join(" · ")}
            </div>
          )}
        </div>
      ))}
      {loading && (
        <div className="mr-auto rounded-lg border border-slate-700 bg-slate-900/60 px-3 py-2 text-xs text-slate-400">
          Agent is thinking…
        </div>
      )}
    </div>
  );
}

export function AgentEnrichmentPipeline({
  activeCount,
}: {
  activeCount: number;
}) {
  const steps = [
    "Reading incident context and session memory",
    "Retrieving bet-service runbook from Knowledge Base",
    "Calling piter-recent-deployments enrichment tool",
    "Calling piter-service-context for owner and impact",
    "Searching similar past incidents (piter-similar-incidents)",
    "Correlating warning signals before P1 threshold",
    "Generating source-grounded triage action plan",
    "Preparing safe escalation preview (mock mode)",
  ];
  return (
    <div className="rounded-xl border border-emerald-500/25 bg-emerald-500/5 p-4">
      <div className="mb-3 flex items-center gap-2 text-xs font-semibold uppercase tracking-[0.2em] text-emerald-200/80">
        <CheckCircle2 className="size-4 text-emerald-300" />
        Agent enrichment pipeline
      </div>
      <div className="grid grid-cols-2 gap-2 max-[760px]:grid-cols-1">
        {steps.map((step, index) => {
          const done = index < activeCount;
          return (
            <div
              key={step}
              className={classNames(
                "flex items-start gap-2 rounded-lg border px-3 py-2 text-xs",
                done
                  ? "border-emerald-500/30 bg-emerald-500/10 text-emerald-100"
                  : "border-slate-700/80 bg-slate-950/40 text-slate-500",
              )}
            >
              <CheckCircle2
                className={classNames("mt-0.5 size-3.5 shrink-0", done ? "text-emerald-300" : "text-slate-600")}
              />
              <span>{step}</span>
            </div>
          );
        })}
      </div>
    </div>
  );
}

export function AgentDecisionsLog({
  stormState,
  noiseSuppressed,
}: {
  stormState: string;
  noiseSuppressed: number;
}) {
  const entries: { time: string; text: string }[] = [];
  if (stormState !== "idle") {
    entries.push({ time: "T+0s", text: "Ingesting simulated alert batch (399 deterministic alerts)" });
    entries.push({ time: "T+12s", text: `Suppressed ${noiseSuppressed} duplicate P3/P4 alerts as noise` });
    entries.push({ time: "T+45s", text: "Noise pattern detected: repeated wallet-service memory warnings" });
    entries.push({ time: "T+90s", text: "Warning signal: bet-service latency p95 elevated" });
    entries.push({ time: "T+125s", text: "Grouping alerts by service + symptom fingerprint" });
  }
  if (stormState === "critical" || stormState === "investigating" || stormState === "resolved") {
    entries.push({ time: "T+175s", text: "P1 candidate detected — bet-service 100% error rate on GIB-UKGC" });
    entries.push({ time: "T+176s", text: "Alert storm paused for human review and triage" });
  }
  if (stormState === "investigating" || stormState === "resolved") {
    entries.push({ time: "T+180s", text: "Running /api/triage with RAG + Lambda-style enrichment" });
  }
  if (stormState === "resolved") {
    entries.push({ time: "T+195s", text: "Escalation preview prepared — notification mode: mock" });
    entries.push({ time: "T+200s", text: "Session memory enabled for follow-up questions" });
  }

  return (
    <div className="space-y-2">
      {entries.length === 0 ? (
        <p className="text-sm text-slate-500">Start the demo to stream agent decisions.</p>
      ) : (
        entries.map((entry) => (
          <div
            key={`${entry.time}-${entry.text}`}
            className="flex gap-3 rounded-lg border border-slate-700/80 bg-slate-950/50 px-3 py-2 text-sm"
          >
            <span className="shrink-0 font-mono text-xs text-cyan-300/80">{entry.time}</span>
            <span className="text-slate-300">{entry.text}</span>
          </div>
        ))
      )}
    </div>
  );
}

export type StreamRow = {
  time: string;
  service: string;
  alert: string;
  severity: string;
  status: string;
};

export function AlertStreamTable({
  rows,
  visibleTotal,
  total,
}: {
  rows: StreamRow[];
  visibleTotal: number;
  total: number;
}) {
  return (
    <div>
      <div className="mb-2 flex items-center justify-between text-xs text-slate-500">
        <span>Incoming alert stream</span>
        <span>
          {visibleTotal} visible · {total} total
        </span>
      </div>
      <div className="overflow-x-auto rounded-lg border border-slate-700/80">
        <table className="w-full min-w-[640px] text-left text-sm">
          <thead className="border-b border-slate-700 bg-slate-950/60 text-[11px] uppercase tracking-wider text-slate-500">
            <tr>
              {["Time", "Service", "Alert", "Sev", "Status"].map((h) => (
                <th key={h} className="px-3 py-2 font-medium">
                  {h}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.map((row) => (
              <tr key={`${row.time}-${row.alert}`} className="border-b border-slate-800/80 last:border-0">
                <td className="px-3 py-2 font-mono text-xs text-slate-400">{row.time}</td>
                <td className="px-3 py-2 text-slate-200">{row.service}</td>
                <td className="px-3 py-2 text-slate-300">{row.alert}</td>
                <td className="px-3 py-2">
                  <SeverityBadge severity={row.severity} />
                </td>
                <td className="px-3 py-2 text-xs text-slate-500">{row.status}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export function SeverityBadge({ severity }: { severity: string }) {
  const tone =
    severity === "P1"
      ? "border-red-500/40 bg-red-500/15 text-red-100"
      : severity === "P2"
        ? "border-amber-400/40 bg-amber-400/15 text-amber-100"
        : severity === "P3"
          ? "border-blue-400/40 bg-blue-400/15 text-blue-100"
          : "border-slate-500/40 bg-slate-500/15 text-slate-200";
  return (
    <span className={classNames("rounded-full border px-2 py-0.5 text-[11px] font-semibold", tone)}>
      {severity}
    </span>
  );
}

export function P1CandidateCard({
  title,
  description,
  onAnalyze,
  onEscalate,
  onChat,
  onContinue,
  showActions,
}: {
  title: string;
  description: string;
  onAnalyze: () => void;
  onEscalate: () => void;
  onChat: () => void;
  onContinue: () => void;
  showActions: boolean;
}) {
  if (!showActions) return null;
  return (
    <section className="rounded-xl border border-amber-400/35 bg-gradient-to-br from-amber-500/10 via-slate-900/80 to-slate-950/90 p-5 neon-ring-ingest">
      <div className="flex flex-wrap items-center gap-2">
        <ShieldAlert className="size-5 text-red-300" />
        <span className="rounded-full border border-red-500/40 bg-red-500/15 px-2.5 py-0.5 text-xs font-bold text-red-100">
          P1 INCIDENT CANDIDATE DETECTED
        </span>
      </div>
      <h3 className="mt-3 text-xl font-semibold text-white">{title}</h3>
      <p className="mt-2 max-w-3xl text-sm leading-relaxed text-slate-300">{description}</p>
      <div className="mt-4 flex flex-wrap gap-2">
        <button
          type="button"
          onClick={onAnalyze}
          className="cursor-pointer rounded-md bg-cyan-300 px-4 py-2 text-sm font-semibold text-slate-950 hover:bg-cyan-200"
        >
          Run PITER analysis
        </button>
        <button
          type="button"
          onClick={onEscalate}
          className="cursor-pointer rounded-md border border-orange-400/40 bg-orange-500/10 px-4 py-2 text-sm font-medium text-orange-100 hover:bg-orange-500/20"
        >
          Escalate on-call
        </button>
        <button
          type="button"
          onClick={onChat}
          className="cursor-pointer rounded-md border border-slate-600 px-4 py-2 text-sm text-slate-200 hover:bg-slate-800"
        >
          Open agent chat
        </button>
        <button
          type="button"
          onClick={onContinue}
          className="cursor-pointer rounded-md border border-slate-600 px-4 py-2 text-sm text-slate-200 hover:bg-slate-800"
        >
          Continue live stream
        </button>
      </div>
    </section>
  );
}

export function NoisePatternCard({
  visible,
  suppressed,
}: {
  visible: boolean;
  suppressed: number;
}) {
  if (!visible) return null;
  return (
    <div className="rounded-xl border border-emerald-500/25 bg-emerald-500/5 p-4">
      <div className="text-xs font-semibold uppercase tracking-wider text-emerald-200/80">
        Noise pattern detected
      </div>
      <p className="mt-2 text-sm text-slate-300">
        <span className="font-medium text-slate-100">wallet-service · memory_utilization_high</span>
        {" — "}
        repeated P4 warnings below escalation threshold grouped automatically.
      </p>
      <div className="mt-3 flex flex-wrap gap-2 text-xs">
        <span className="rounded-full border border-emerald-400/30 bg-emerald-400/10 px-2.5 py-1 text-emerald-100">
          {suppressed} duplicates suppressed
        </span>
        <span className="rounded-full border border-slate-600 px-2.5 py-1 text-slate-400">
          Pattern frequency: 83 alerts / 8 min window (demo)
        </span>
      </div>
    </div>
  );
}

export function EscalationTriggeredCard({
  visible,
  incidentTitle,
  ownerTeam,
  onCallRole,
  payloadLines,
  notificationMode,
  liveDispatchEnabled,
  onEscalateLive,
}: {
  visible: boolean;
  incidentTitle: string;
  ownerTeam: string;
  onCallRole: string;
  payloadLines: string[];
  notificationMode?: string;
  liveDispatchEnabled?: boolean;
  onEscalateLive?: () => void;
}) {
  if (!visible) return null;
  const previewOnly = notificationMode !== "live" || !liveDispatchEnabled;
  return (
    <div className="rounded-xl border border-orange-500/30 bg-gradient-to-br from-orange-500/10 to-slate-950/90 p-4">
      <div className="flex items-start gap-3">
        <ShieldAlert className="size-5 shrink-0 text-orange-300" />
        <div className="min-w-0 flex-1">
          <div className="font-semibold text-white">
            {previewOnly ? "Escalation preview triggered" : "Escalation triggered"}
          </div>
          <p className="mt-1 text-xs text-slate-400">
            {previewOnly
              ? `P1 incident dispatch preview — mode ${notificationMode ?? "mock"}; live SNS/SES requires all gates.`
              : "P1 incident dispatched to on-call team."}
          </p>
          <dl className="mt-3 grid gap-1 text-sm">
            <div>
              <span className="text-slate-500">Incident: </span>
              <span className="text-slate-200">{incidentTitle}</span>
            </div>
            <div>
              <span className="text-slate-500">Sent to: </span>
              <span className="font-medium text-white">{ownerTeam}</span>
            </div>
            <div>
              <span className="text-slate-500">On-call: </span>
              <span className="font-medium text-white">{onCallRole}</span>
            </div>
          </dl>
          <div className="mt-3 rounded-lg border border-slate-700 bg-slate-950/60 p-3">
            <div className="text-xs font-semibold uppercase tracking-wider text-slate-500">Payload</div>
            <ul className="mt-2 list-inside list-disc space-y-1 text-xs text-slate-300">
              {payloadLines.map((line) => (
                <li key={line}>{line}</li>
              ))}
            </ul>
          </div>
          {onEscalateLive ? (
            <button
              type="button"
              onClick={onEscalateLive}
              className="mt-4 cursor-pointer rounded-md border border-orange-400/40 bg-orange-500/15 px-4 py-2 text-sm font-medium text-orange-100 hover:bg-orange-500/25"
            >
              Escalate on-call (SMS / email)
            </button>
          ) : null}
        </div>
      </div>
    </div>
  );
}

export function EscalationNotifyModal({
  open,
  onClose,
  incidentId,
  service,
  severity,
  escalationContext,
  notificationMode,
  liveDispatchEnabled,
  demoSmsConfigured,
  demoWhatsappConfigured,
  demoEmailConfigured,
  smsDeliveryReady = true,
  smsConsoleUrl,
  smsBillingUrl,
}: {
  open: boolean;
  onClose: () => void;
  incidentId: string;
  service: string;
  severity: string;
  escalationContext: EscalationContext;
  notificationMode: string;
  liveDispatchEnabled: boolean;
  demoSmsConfigured: boolean;
  demoWhatsappConfigured: boolean;
  demoEmailConfigured: boolean;
  smsDeliveryReady?: boolean;
  smsConsoleUrl?: string | null;
  smsBillingUrl?: string | null;
}) {
  const [token, setToken] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<EscalationNotifyResult | null>(null);

  if (!open) return null;

  async function send(channel: "sms" | "email" | "whatsapp") {
    setLoading(true);
    setResult(null);
    try {
      const response = await notifyEscalation({
        channel,
        incident_id: incidentId,
        service,
        severity,
        confirmation_token: token,
        escalation_context: escalationContext,
        idempotency_key: `${incidentId}:${channel}:${crypto.randomUUID()}`,
      });
      setResult(response);
    } catch (err) {
      setResult({
        ok: false,
        sent: false,
        message: err instanceof Error ? err.message : "Notification request failed",
      });
    } finally {
      setLoading(false);
    }
  }

  const ready = notificationMode === "live" && liveDispatchEnabled;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/70 p-4 backdrop-blur-sm">
      <div
        role="dialog"
        aria-modal="true"
        aria-labelledby="escalation-notify-title"
        className="w-full max-w-lg rounded-xl border border-slate-700 bg-slate-900 p-5 shadow-2xl"
      >
        <div className="flex items-start justify-between gap-3">
          <div>
            <h2 id="escalation-notify-title" className="text-lg font-semibold text-white">
              Escalate on-call
            </h2>
            <p className="mt-1 text-sm text-slate-400">
              {escalationContext.incident_title} · {escalationContext.on_call_name}
            </p>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="cursor-pointer rounded-md p-1 text-slate-400 hover:bg-slate-800 hover:text-white"
            aria-label="Close"
          >
            <X className="size-5" />
          </button>
        </div>

        <div className="mt-4 space-y-3 text-sm text-slate-300">
          <p>
            Mode: <span className="font-medium text-white">{notificationMode}</span>
            {ready ? " — live dispatch armed" : " — preview / blocked until live gates pass"}
          </p>
          <label className="block">
            <span className="text-xs uppercase tracking-wider text-slate-500">
              Confirmation token (from .env)
            </span>
            <input
              type="password"
              value={token}
              onChange={(e) => setToken(e.target.value)}
              className="mt-1 w-full rounded-md border border-slate-600 bg-slate-950 px-3 py-2 text-sm text-white"
              placeholder="PITER_NOTIFICATION_CONFIRMATION_TOKEN"
            />
          </label>
        </div>

        {!smsDeliveryReady && demoSmsConfigured ? (
          <div className="mt-4 rounded-lg border border-amber-500/30 bg-amber-500/10 p-3 text-xs text-amber-100">
            <p className="font-medium">AWS SMS not enabled on this account yet.</p>
            <p className="mt-1 opacity-90">
              Use <strong>Send email</strong> now, or enable SMS in the AWS console (accept terms +
              set spend limit + verify sandbox phone).
            </p>
            <p className="mt-2 flex flex-wrap gap-3">
              {smsConsoleUrl ? (
                <a href={smsConsoleUrl} target="_blank" rel="noreferrer" className="underline">
                  End User Messaging SMS
                </a>
              ) : null}
              {smsBillingUrl ? (
                <a href={smsBillingUrl} target="_blank" rel="noreferrer" className="underline">
                  Account verification
                </a>
              ) : null}
            </p>
          </div>
        ) : null}

        <div className="mt-4 flex flex-wrap gap-2">
          {demoWhatsappConfigured ? (
            <button
              type="button"
              disabled={loading || !token}
              onClick={() => send("whatsapp")}
              className="cursor-pointer rounded-md bg-emerald-400 px-4 py-2 text-sm font-semibold text-slate-950 hover:bg-emerald-300 disabled:cursor-not-allowed disabled:opacity-40"
            >
              Send WhatsApp
            </button>
          ) : null}
          <button
            type="button"
            disabled={loading || !token || !demoEmailConfigured}
            onClick={() => send("email")}
            className={classNames(
              "cursor-pointer rounded-md px-4 py-2 text-sm font-semibold disabled:cursor-not-allowed disabled:opacity-40",
              smsDeliveryReady
                ? "border border-slate-600 text-slate-200 hover:bg-slate-800"
                : "bg-cyan-300 text-slate-950 hover:bg-cyan-200",
            )}
          >
            Send email
          </button>
          <button
            type="button"
            disabled={loading || !token || !demoSmsConfigured || !smsDeliveryReady}
            onClick={() => send("sms")}
            className="cursor-pointer rounded-md border border-slate-600 px-4 py-2 text-sm text-slate-200 hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-40"
            title={!smsDeliveryReady ? "Enable AWS End User Messaging SMS first" : undefined}
          >
            Send SMS
          </button>
        </div>

        {result ? (
          <div
            className={classNames(
              "mt-4 rounded-lg border p-3 text-sm",
              result.sent
                ? "border-emerald-500/30 bg-emerald-500/10 text-emerald-100"
                : "border-amber-500/30 bg-amber-500/10 text-amber-100",
            )}
          >
            {result.sent ? (
              <>
                <div className="font-semibold">Sent via {result.channel}</div>
                <div className="mt-1 text-xs opacity-90">
                  Recipient: {result.recipient} · MessageId: {result.message_id ?? "n/a"}
                </div>
              </>
            ) : (
              <>
                <div className="font-semibold">Not sent</div>
                <ul className="mt-2 list-inside list-disc text-xs">
                  {(result.reasons ?? [result.message ?? result.error ?? "Request blocked"]).map(
                    (line) => (
                      <li key={line}>{line}</li>
                    ),
                  )}
                </ul>
              </>
            )}
          </div>
        ) : null}
      </div>
    </div>
  );
}

export function MetadataGrid({ items }: { items: { label: string; value: string }[] }) {
  return (
    <dl className="grid grid-cols-2 gap-3 max-[640px]:grid-cols-1">
      {items.map((item) => (
        <div key={item.label} className="rounded-lg border border-slate-700/80 bg-slate-950/40 p-3">
          <dt className="text-[10px] font-medium uppercase tracking-wider text-slate-500">
            {item.label}
          </dt>
          <dd className="mt-1 text-sm text-slate-200">{item.value}</dd>
        </div>
      ))}
    </dl>
  );
}

export function MemoryFlowPanel({
  sessionId,
  incidentLabel,
  lastQuestion,
  lastAnswer,
  memoryUsed,
  onReset,
}: {
  sessionId: string;
  incidentLabel: string;
  lastQuestion: string | null;
  lastAnswer: string | null;
  memoryUsed: boolean;
  onReset: () => void;
}) {
  return (
    <div className="rounded-xl border border-violet-400/25 bg-violet-500/5 p-4">
      <div className="flex items-center justify-between gap-2">
        <div className="text-sm font-semibold text-violet-100">Memory active</div>
        <span
          className={classNames(
            "rounded-full px-2 py-0.5 text-[10px] font-bold uppercase",
            memoryUsed ? "bg-emerald-500/20 text-emerald-200" : "bg-slate-700 text-slate-400",
          )}
        >
          {memoryUsed ? "ON" : "READY"}
        </span>
      </div>
      <div className="mt-3 space-y-2 text-xs">
        <MemoryField label="Current incident" value={incidentLabel} />
        <MemoryField label="Session ID" value={sessionId} mono />
        <MemoryField label="Last question" value={lastQuestion ?? "—"} />
        <MemoryField label="Last assistant answer" value={lastAnswer?.slice(0, 220) ?? "—"} />
      </div>
      <div className="mt-3 rounded-lg border border-cyan-400/20 bg-cyan-400/5 px-3 py-2 text-[11px] leading-relaxed text-cyan-100/90">
        Memory rule: follow-up questions reuse the active incident session context. The system
        stores, summarizes, retrieves, and reuses relevant investigation context — it does not
        permanently train the model.
      </div>
      <button
        type="button"
        onClick={onReset}
        className="mt-3 cursor-pointer rounded-md border border-slate-600 px-3 py-1.5 text-xs text-slate-300 hover:bg-slate-800"
      >
        Reset memory preview
      </button>
    </div>
  );
}

function MemoryField({
  label,
  value,
  mono,
}: {
  label: string;
  value: string;
  mono?: boolean;
}) {
  return (
    <div>
      <div className="text-[10px] uppercase tracking-wider text-slate-500">{label}</div>
      <div
        className={classNames(
          "mt-0.5 rounded border border-slate-700/80 bg-slate-950/50 px-2 py-1.5 text-slate-300",
          mono && "font-mono text-[11px]",
        )}
      >
        {value}
      </div>
    </div>
  );
}

export function UploadInstructions({
  allowedTypes,
  maxMb,
}: {
  allowedTypes: string[];
  maxMb: number;
}) {
  return (
    <div className="mb-4 grid gap-3 rounded-lg border border-slate-700/80 bg-slate-950/40 p-3 text-xs text-slate-400">
      <div>
        <span className="font-medium text-slate-300">Accepted formats: </span>
        {allowedTypes.map((t) => (
          <span key={t} className="mr-1.5 inline-block">
            <DocTypeBadge type={t.replace(".", "")} />
          </span>
        ))}
      </div>
      <div>
        <span className="font-medium text-slate-300">Max file size:</span> {maxMb} MB (server
        enforced)
      </div>
      <div>
        <span className="font-medium text-slate-300">Indexing:</span> local/demo corpus by default.
        Bedrock Knowledge Base sync only when explicitly enabled — not automatic from this UI.
      </div>
      <div>
        <span className="font-medium text-slate-300">After upload:</span> use “Ask about uploaded
        document” in the inventory table or agent chat to test retrieval.
      </div>
    </div>
  );
}
