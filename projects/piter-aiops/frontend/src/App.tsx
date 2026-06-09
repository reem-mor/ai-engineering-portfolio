import { useEffect, useMemo, useRef, useState, type RefObject } from "react";
import {
  Activity,
  AlertTriangle,
  Archive,
  Bell,
  Bot,
  Brain,
  CheckCircle2,
  ChevronRight,
  Clock3,
  Database,
  FileText,
  Flame,
  Gauge,
  GitBranch,
  History,
  Layers,
  Lock,
  MessageSquare,
  Network,
  Paperclip,
  Play,
  Search,
  ServerCog,
  ShieldCheck,
  Sparkles,
  Target,
  TerminalSquare,
  TrendingDown,
  Zap,
} from "lucide-react";

import {
  askQuestion,
  executionModeLabel,
  fetchAlertStream,
  fetchInvestigations,
  fetchKbManifest,
  fetchSessionHistory,
  type InvestigationRow,
  followUp,
  runTriageCard,
  triageToRagAnswer,
  uploadDocument,
} from "@/lib/api";
import { buildEscalationContext } from "@/lib/escalation";
import { clearChatTurns, loadChatTurns, saveChatTurns } from "@/lib/chat-memory";
import {
  AgentDecisionsLog,
  AgentEnrichmentPipeline,
  AlertStreamTable,
  BusinessImpactPanel,
  ChatThread,
  DocTypeBadge,
  EscalationNotifyModal,
  EscalationTriggeredCard,
  IncidentQueuePanel,
  McpToolCallsPanel,
  MemoryFlowPanel,
  MetadataGrid,
  NoisePatternCard,
  P1CandidateCard,
  UploadInstructions,
  type ChatTurn,
  type StreamRow,
} from "@/components/piter/ops-ui";
import { useBootstrap } from "@/context/bootstrap";
import type { AlertStreamSummary, BootstrapPayload, Citation, KbDocumentMeta, RagAnswer, SessionHistoryPayload, TriageCard } from "@/types/rag";

type NavKey =
  | "storm"
  | "dashboard"
  | "investigations"
  | "chat"
  | "memory"
  | "knowledge"
  | "tools"
  | "architecture"
  | "settings";

type ConclusionBadge =
  | "Critical"
  | "Malicious"
  | "Suspicious"
  | "Inconclusive"
  | "Benign"
  | "Noise";

type Investigation = {
  id: string;
  conclusion: ConclusionBadge;
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

type StormState = "idle" | "streaming" | "paused" | "critical" | "investigating" | "resolved";

const NAV_ITEMS: {
  key: NavKey;
  label: string;
  icon: React.ComponentType<{ className?: string }>;
}[] = [
  { key: "storm", label: "Live Demo", icon: Activity },
  { key: "dashboard", label: "Dashboard", icon: Gauge },
  { key: "investigations", label: "Incidents", icon: Search },
  { key: "chat", label: "Chat", icon: MessageSquare },
  { key: "memory", label: "History", icon: History },
  { key: "knowledge", label: "Knowledge / RAG", icon: Database },
  { key: "tools", label: "MCP Tools", icon: ServerCog },
  { key: "architecture", label: "Architecture", icon: Network },
  { key: "settings", label: "Settings", icon: ShieldCheck },
];

/** Compressed playback of the 5-minute alert storm corpus (~400 rows). */
const STORM_DEMO_MS = 20_000;
const STORM_TICK_MS = 80;

const STORM_INVESTIGATION_ID = "ALT-2026-06-10-0251";

const EMPTY_INVESTIGATION: Investigation = {
  id: "loading",
  conclusion: "Inconclusive",
  conclusionDetail: "Loading investigations from alert stream…",
  alertTime: "—",
  alert: "—",
  service: "—",
  environment: "—",
  entities: "—",
  source: "Alert stream API",
  status: "Loading",
  priority: "P4",
  impact: "—",
};

function mapInvestigation(row: InvestigationRow): Investigation {
  return {
    ...row,
    conclusion: row.conclusion as ConclusionBadge,
  };
}

function averageMttrMinutes(triageCard: TriageCard | null): number | null {
  const values = (triageCard?.similar_incidents ?? [])
    .map((item) => item.mttr_minutes)
    .filter((value): value is number => typeof value === "number" && value > 0);
  if (!values.length) return null;
  return Math.round(values.reduce((sum, value) => sum + value, 0) / values.length);
}

const KPI_CARDS_STATIC = [
  {
    label: "Active Incidents",
    value: "3",
    sub: "1 critical in review",
    icon: Flame,
    tone: "red",
  },
  {
    label: "P1 / P2 / P3",
    value: "1 / 1 / 2",
    sub: "priority mix",
    icon: AlertTriangle,
    tone: "amber",
  },
  {
    label: "Median Triage Time",
    value: "4.2 min",
    sub: "agent-assisted",
    icon: Clock3,
    tone: "cyan",
  },
  { label: "MTTR Reduced", value: "31 min", sub: "vs baseline estimate", icon: TrendingDown, tone: "teal" },
  {
    label: "Cost Avoided",
    value: "$18.6k",
    sub: "estimated impact",
    icon: Target,
    tone: "green",
  },
  { label: "Escalations Triggered", value: "1", sub: "allowlist gated", icon: Bell, tone: "amber" },
  { label: "Knowledge Sources", value: "11+", sub: "KB sections", icon: Database, tone: "blue" },
  { label: "Lambda Tools", value: "4", sub: "final tool map", icon: ServerCog, tone: "cyan" },
  { label: "Memory Sessions", value: "7", sub: "context reused", icon: Brain, tone: "purple" },
];

const PIPELINE = [
  { label: "Priority", body: "P1 classification from impact, severity, and regulated market." },
  {
    label: "Investigation",
    body: "Correlates warning shots, deploys, similar incidents, and KB evidence.",
  },
  { label: "Triage", body: "Turns evidence into concrete operator steps with citations." },
  { label: "Escalation", body: "Previews owner, policy, and masked notification recipients." },
  { label: "Resolution", body: "Produces validation steps and post-mortem draft." },
];

const TOOLS = [
  {
    name: "piter-recent-deployments",
    purpose: "Recent deployments, correlation, rollback availability",
    input: "service, environment, alert_time, lookback_hours",
    output: "suspect_deployment, dependency_hop, rollback_available",
    status: "mock data / live-ready source",
    latency: "42 ms",
    used: true,
  },
  {
    name: "piter-service-context",
    purpose: "Ownership, on-call role, impact, priority, regulatory exposure",
    input: "service, environment, severity",
    output: "owner_team, escalation_path, business_impact",
    status: "mock data / live-ready source",
    latency: "31 ms",
    used: true,
  },
  {
    name: "piter-similar-incidents",
    purpose: "Historical incident matching, root cause, resolution, previous MTTR",
    input: "service, symptom, limit",
    output: "similar_incidents, root_cause, resolution, mttr_minutes",
    status: "mock data / live-ready source",
    latency: "58 ms",
    used: true,
  },
  {
    name: "piter-escalation",
    purpose: "Escalation policy preview and safe notification workflow",
    input: "operation, service, severity, incident_id, recipient, token",
    output: "policy, masked_recipient, blocked_reasons, idempotency_key",
    status: "mock by default / live-blocked",
    latency: "27 ms",
    used: true,
  },
];

const KB_DOCS = [
  {
    name: "api_gateway_5xx.md",
    type: "runbook",
    service: "api-gateway",
    env: "GIB-UKGC",
    severity: "P1/P2",
    score: "0.91",
    status: "indexed",
  },
  {
    name: "RB-010 Deployment Rollback Procedure",
    type: "runbook",
    service: "all",
    env: "all",
    severity: "P1/P2",
    score: "0.87",
    status: "indexed",
  },
  {
    name: "Severity and Escalation Policy",
    type: "policy",
    service: "all",
    env: "regulated",
    severity: "P1-P4",
    score: "0.84",
    status: "indexed",
  },
  {
    name: "Regulated Market Environments",
    type: "environment",
    service: "all",
    env: "GIB-UKGC",
    severity: "P1/P2",
    score: "0.79",
    status: "indexed",
  },
  {
    name: "Checkout Outage Postmortem Reference",
    type: "incident",
    service: "checkout-api",
    env: "GIB-UKGC",
    severity: "P1",
    score: "0.72",
    status: "indexed",
  },
];

const WARNING_ALERTS = [
  "T+090s bet-service latency p95 increased to 2.4s",
  "T+125s connection pool exhausted briefly on bet-service",
  "T+155s bet-service 5xx rate above 2% (3.8%)",
  "T+170s bet-service circuit breaker tripped briefly",
  "T+175s P1: bet-service nodes unresponsive, 100% error rate",
];

function conclusionTone(conclusion: ConclusionBadge): string {
  const map: Record<ConclusionBadge, string> = {
    Critical: "red",
    Malicious: "red",
    Suspicious: "amber",
    Inconclusive: "blue",
    Benign: "green",
    Noise: "slate",
  };
  return map[conclusion] ?? "cyan";
}

function statusTone(status: string): string {
  if (status === "Escalated") return "red";
  if (status === "Noise Grouped" || status === "Resolved" || status === "False Positive")
    return "green";
  if (status === "Investigating" || status === "In Process") return "cyan";
  return "amber";
}

function stormPhaseLabel(state: StormState): string {
  const map: Record<StormState, string> = {
    idle: "Ready",
    streaming: "Streaming alerts",
    paused: "Paused",
    critical: "P1 detected — auto-paused",
    investigating: "Running PITER triage",
    resolved: "Incident resolved",
  };
  return map[state];
}

function classNames(...items: Array<string | false | null | undefined>) {
  return items.filter(Boolean).join(" ");
}

function toneClasses(tone: string) {
  const map: Record<string, string> = {
    red: "border-red-500/30 bg-red-500/10 text-red-200",
    amber: "border-amber-400/30 bg-amber-400/10 text-amber-100",
    green: "border-emerald-400/30 bg-emerald-400/10 text-emerald-100",
    teal: "border-teal-400/30 bg-teal-400/10 text-teal-100",
    cyan: "border-cyan-400/30 bg-cyan-400/10 text-cyan-100",
    blue: "border-blue-400/30 bg-blue-400/10 text-blue-100",
    purple: "border-violet-400/30 bg-violet-400/10 text-violet-100",
    slate: "border-slate-500/30 bg-slate-500/10 text-slate-200",
  };
  return map[tone] ?? map.cyan;
}

function priorityClasses(priority: string) {
  if (priority === "P1") return "border-red-500/40 bg-red-500/15 text-red-100";
  if (priority === "P2") return "border-amber-400/40 bg-amber-400/15 text-amber-100";
  if (priority === "P3") return "border-blue-400/40 bg-blue-400/15 text-blue-100";
  return "border-slate-500/40 bg-slate-500/15 text-slate-100";
}

function AppShell() {
  const { data, loading, error } = useBootstrap();
  const [active, setActive] = useState<NavKey>("storm");
  const [investigations, setInvestigations] = useState<Investigation[]>([EMPTY_INVESTIGATION]);
  const [selected, setSelected] = useState<Investigation>(EMPTY_INVESTIGATION);
  const [stormState, setStormState] = useState<StormState>("idle");
  const [triageCard, setTriageCard] = useState<TriageCard | null>(null);
  const [answer, setAnswer] = useState<RagAnswer | null>(null);
  const [memoryUsed, setMemoryUsed] = useState(false);
  const [chatInput, setChatInput] = useState("Who should I escalate this to?");
  const [chatLoading, setChatLoading] = useState(false);
  const [chatError, setChatError] = useState<string | null>(null);
  const [lastQuestion, setLastQuestion] = useState<string | null>(null);
  const [chatTurns, setChatTurns] = useState<ChatTurn[]>([]);
  const [sessionHistory, setSessionHistory] = useState<SessionHistoryPayload | null>(null);
  const [kbDocs, setKbDocs] = useState<KbDocumentMeta[]>([]);
  const [invStatuses, setInvStatuses] = useState<Record<string, string>>({});
  const [escalationModalOpen, setEscalationModalOpen] = useState(false);
  const [alertCorpus, setAlertCorpus] = useState<Record<string, string>[]>([]);
  const [stormVisibleCount, setStormVisibleCount] = useState(8);
  const [p1Dismissed, setP1Dismissed] = useState(false);
  const [workflowLoading, setWorkflowLoading] = useState(false);
  const [stormMarkedResolved, setStormMarkedResolved] = useState(false);
  const [uploadLoading, setUploadLoading] = useState(false);
  const stormTimerRef = useRef<number | null>(null);
  const stormTickRef = useRef<number | null>(null);
  const chatUploadRef = useRef<HTMLInputElement | null>(null);

  const streamSummary: AlertStreamSummary = data?.alert_stream ?? {
    total: 400,
    label: "Alert storm corpus (400 alerts)",
    duration_seconds: 300,
    by_severity: { P1: 1, P2: 32, P3: 88, P4: 279 },
    noise_suppressed: 367,
    warning_signals: 5,
    p1_count: 1,
  };

  const executionLabel = executionModeLabel(
    triageCard?.mode ?? answer?.session_id ? triageCard?.mode : undefined,
    data?.rag_backend,
    data?.use_bedrock,
  );
  const modelLabel = triageCard?.mode
    ? executionModeLabel(triageCard.mode, data?.rag_backend, data?.use_bedrock)
    : data?.execution_mode_hint || data?.model_label || "Bedrock Agent / KB";
  const sessionId = triageCard?.session_id ?? answer?.session_id ?? "demo-session-preview";
  const notificationMode = data?.notification?.mode ?? "preview";
  const liveDispatchEnabled = data?.notification?.live_dispatch_enabled ?? false;
  const demoSmsConfigured = data?.notification?.demo_sms_configured ?? false;
  const demoWhatsappConfigured = data?.notification?.demo_whatsapp_configured ?? false;
  const demoEmailConfigured = data?.notification?.demo_email_configured ?? false;
  const smsDeliveryReady = data?.notification?.sms_delivery_ready ?? false;
  const smsConsoleUrl = data?.notification?.sms_console_url;
  const smsBillingUrl = data?.notification?.sms_billing_url;
  const escalationContext = useMemo(
    () => buildEscalationContext(triageCard, selected, streamSummary),
    [triageCard, selected, streamSummary],
  );

  function refreshSessionHistory(sid: string | null | undefined) {
    if (!sid) {
      setSessionHistory(null);
      return;
    }
    fetchSessionHistory(sid)
      .then((history) => setSessionHistory(history))
      .catch(() => setSessionHistory(null));
  }

  const landingAlerts = useMemo(() => {
    if (streamSummary.active_alerts?.length) return streamSummary.active_alerts;
    return alertCorpus.filter((r) => r.is_noise_candidate !== "true").slice(0, 15);
  }, [streamSummary, alertCorpus]);

  useEffect(() => {
    fetchAlertStream("include")
      .then((payload) => setAlertCorpus(payload.rows ?? []))
      .catch(() => setAlertCorpus([]));
  }, []);

  useEffect(() => {
    fetchInvestigations(12)
      .then((payload) => {
        const rows = payload.investigations.map(mapInvestigation);
        if (!rows.length) return;
        setInvestigations(rows);
        setSelected((prev) => (prev.id === "loading" ? rows[0] : prev));
      })
      .catch(() => {
        setInvestigations([]);
      });
  }, []);

  useEffect(() => {
    return () => {
      if (stormTimerRef.current) window.clearTimeout(stormTimerRef.current);
      if (stormTickRef.current) window.clearInterval(stormTickRef.current);
    };
  }, []);

  useEffect(() => {
    fetchKbManifest()
      .then((manifest) => setKbDocs(manifest.documents))
      .catch(() => setKbDocs([]));
  }, []);

  useEffect(() => {
    if (!sessionId || sessionId === "demo-session-preview") return;
    const stored = loadChatTurns(sessionId);
    if (stored.length) {
      setChatTurns((prev) => (prev.length ? prev : stored));
    }
  }, [sessionId]);

  useEffect(() => {
    saveChatTurns(sessionId, chatTurns);
  }, [sessionId, chatTurns]);

  useEffect(() => {
    if (!sessionHistory?.followups?.length) return;
    setChatTurns((prev) => {
      if (prev.length > 0) return prev;
      const turns: ChatTurn[] = [];
      for (const followup of sessionHistory.followups) {
        turns.push({ role: "user", text: followup.question });
        turns.push({
          role: "assistant",
          text: followup.answer.answer,
          citations: (followup.answer.citations ?? []).map((c, index) => ({
            snippet: c.excerpt,
            source_uri: c.document,
            source_label: c.document,
            index: index + 1,
            score: c.score ?? null,
          })),
        });
      }
      return turns;
    });
  }, [sessionHistory]);

  const mttrMinutes = useMemo(() => averageMttrMinutes(triageCard), [triageCard]);

  const kpiCards = useMemo(() => {
    const stormResolved =
      (invStatuses[STORM_INVESTIGATION_ID] ?? investigations[0]?.status) === "Resolved";
    const dynamicStatic = KPI_CARDS_STATIC.map((card, index) => {
      if (index === 0 && triageCard) {
        return {
          ...card,
          value: stormResolved ? "2" : "3",
          sub: stormResolved ? "storm incident closed" : "1 critical in review",
        };
      }
      if (index === 2 && triageCard) {
        return {
          ...card,
          value: workflowLoading ? "…" : triageCard.mode === "local" ? "0.8s" : "~11s",
          sub: "last PITER triage",
        };
      }
      if (index === 3 && mttrMinutes) {
        return {
          ...card,
          value: `${mttrMinutes} min`,
          sub: "similar incidents baseline",
        };
      }
      if (index === 5 && stormState === "resolved") {
        return { ...card, value: "1", sub: "storm workflow" };
      }
      return card;
    });
    return [
      {
        label: "Alerts Processed",
        value: String(streamSummary.total),
        sub: "~400 alert storm",
        icon: Activity,
        tone: "cyan",
      },
      {
        label: "Noise Suppressed",
        value: String(streamSummary.noise_suppressed),
        sub: "P3/P4 grouped",
        icon: TrendingDown,
        tone: "green",
      },
      ...dynamicStatic,
    ];
  }, [streamSummary, triageCard, mttrMinutes, workflowLoading, stormState, invStatuses]);

  async function askAgent(question = chatInput) {
    const q = question.trim();
    if (!q) return;
    setChatLoading(true);
    setChatError(null);
    setLastQuestion(q);
    setChatTurns((prev) => [...prev, { role: "user", text: q }]);
    try {
      if (triageCard?.session_id) {
        const result = await followUp(triageCard.session_id, q);
        setMemoryUsed(result.memory_used);
        const citations = (result.citations ?? []).map((c, index) => ({
          snippet: c.excerpt,
          source_uri: c.document,
          source_label: c.document,
          index: index + 1,
          score: c.score ?? null,
        }));
        setAnswer({
          answer: result.answer,
          citations,
          session_id: result.session_id,
          grounded: true,
          latency_ms: 0,
          matched_runbook: triageCard.matched_runbook,
        });
        setChatTurns((prev) => [...prev, { role: "assistant", text: result.answer, citations }]);
        refreshSessionHistory(result.session_id);
      } else {
        const result = await askQuestion(
          `For incident ${selected.id} (${selected.alert}), ${q}`,
          answer?.session_id ?? undefined,
        );
        setAnswer(result);
        setChatTurns((prev) => [
          ...prev,
          { role: "assistant", text: result.answer, citations: result.citations },
        ]);
      }
    } catch (exc) {
      setChatError(exc instanceof Error ? exc.message : "Agent request failed");
    } finally {
      setChatLoading(false);
    }
  }

  function resetMemoryPreview() {
    clearChatTurns(sessionId);
    setChatTurns([]);
    setLastQuestion(null);
    setMemoryUsed(false);
    setAnswer(null);
    setSessionHistory(null);
    setChatError(null);
  }

  function clearStormTimer() {
    if (stormTimerRef.current) {
      window.clearTimeout(stormTimerRef.current);
      stormTimerRef.current = null;
    }
    if (stormTickRef.current) {
      window.clearInterval(stormTickRef.current);
      stormTickRef.current = null;
    }
  }

  function preP1RowCount(corpus: Record<string, string>[]) {
    return corpus.filter((r) => r.severity !== "P1" && r.is_trigger !== "true").length;
  }

  function startStorm() {
    clearStormTimer();
    setP1Dismissed(false);
    setStormVisibleCount(6);
    setStormState("streaming");
    setStormMarkedResolved(false);
    setSelected(investigations[0] ?? EMPTY_INVESTIGATION);
    const preP1Total = preP1RowCount(alertCorpus) || Math.max(streamSummary.total - 1, 1);
    const steps = Math.ceil(STORM_DEMO_MS / STORM_TICK_MS);
    const batch = Math.max(1, Math.ceil(preP1Total / steps));
    stormTickRef.current = window.setInterval(() => {
      setStormVisibleCount((n) => Math.min(n + batch, preP1Total));
    }, STORM_TICK_MS);
    stormTimerRef.current = window.setTimeout(() => {
      clearStormTimer();
      setStormVisibleCount(preP1Total);
      setStormState("critical");
    }, STORM_DEMO_MS);
  }

  function continueLiveStorm() {
    setP1Dismissed(true);
  }

  function pauseStorm() {
    if (stormState === "streaming") {
      clearStormTimer();
      setStormState("paused");
    }
  }

  function resetStorm() {
    clearStormTimer();
    setStormVisibleCount(8);
    setP1Dismissed(false);
    setStormState("idle");
    setStormMarkedResolved(false);
    setWorkflowLoading(false);
  }

  function updateInvStatus(id: string, status: string) {
    setInvStatuses((prev) => ({ ...prev, [id]: status }));
  }

  function getInvStatus(inv: Investigation) {
    return invStatuses[inv.id] ?? inv.status;
  }

  function markStormResolved() {
    updateInvStatus(STORM_INVESTIGATION_ID, "Resolved");
    setStormMarkedResolved(true);
    setChatTurns((prev) => [
      ...prev,
      {
        role: "assistant",
        text: "Incident marked resolved. Validation checklist complete; post-mortem draft and MTTR metrics are recorded for this session.",
      },
    ]);
  }

  async function handleChatUpload(file: File) {
    setUploadLoading(true);
    setChatError(null);
    try {
      const result = await uploadDocument(file, true);
      setChatTurns((prev) => [...prev, { role: "user", text: `Uploaded: ${file.name}` }]);
      fetchKbManifest()
        .then((manifest) => setKbDocs(manifest.documents))
        .catch(() => undefined);
      if (triageCard?.session_id) {
        const question = `How does the uploaded document "${file.name}" relate to this ${selected.service} incident?`;
        setChatLoading(true);
        setLastQuestion(question);
        const followUpResult = await followUp(triageCard.session_id, question);
        setMemoryUsed(followUpResult.memory_used);
        const citations = (followUpResult.citations ?? []).map((c, index) => ({
          snippet: c.excerpt,
          source_uri: c.document,
          source_label: c.document,
          index: index + 1,
          score: c.score ?? null,
        }));
        setAnswer({
          answer: followUpResult.answer,
          citations,
          session_id: followUpResult.session_id,
          grounded: true,
          latency_ms: 0,
          matched_runbook: triageCard.matched_runbook,
        });
        setChatTurns((prev) => [
          ...prev,
          { role: "assistant", text: followUpResult.answer, citations },
        ]);
        refreshSessionHistory(followUpResult.session_id);
      } else {
        setChatTurns((prev) => [
          ...prev,
          {
            role: "assistant",
            text:
              result.message ??
              "Document indexed to the knowledge base. Run PITER analysis to query it in incident context.",
          },
        ]);
      }
    } catch (exc) {
      setChatError(exc instanceof Error ? exc.message : "Upload failed");
    } finally {
      setUploadLoading(false);
      setChatLoading(false);
    }
  }

  async function runWorkflow() {
    setWorkflowLoading(true);
    setStormState("investigating");
    setChatError(null);
    setStormMarkedResolved(false);
    setSelected(investigations[0] ?? EMPTY_INVESTIGATION);
    updateInvStatus(STORM_INVESTIGATION_ID, "In Process");
    try {
      const trigger = streamSummary.p1_trigger;
      const alertPayload = trigger
        ? {
            alert_id: trigger.alert_id,
            service: trigger.service,
            environment: trigger.environment,
            severity: trigger.severity,
            symptom: trigger.title,
            description: trigger.title,
            alert_time: trigger.timestamp,
            duration_minutes: 45,
          }
        : {
            alert_id: "ALT-DEMO-P1-001",
            service: "bet-service",
            environment: "GIB-UKGC",
            severity: "P1",
            symptom: "CRITICAL: bet-service nodes unresponsive — 100% error rate on GIB-UKGC",
            description: "CRITICAL: bet-service nodes unresponsive — 100% error rate on GIB-UKGC",
            alert_time: "2026-06-10T10:02:55.000Z",
            duration_minutes: 45,
          };
      const card = await runTriageCard(alertPayload);
      const rag = triageToRagAnswer(card);
      setTriageCard(card);
      setAnswer(rag);
      refreshSessionHistory(card.session_id);
      setMemoryUsed(false);
      setLastQuestion("What should I check first?");
      setChatTurns([
        {
          role: "assistant",
          text: rag.answer,
          citations: rag.citations,
        },
      ]);
      updateInvStatus(STORM_INVESTIGATION_ID, "Escalated");
      setStormState("resolved");
    } catch (exc) {
      setChatError(exc instanceof Error ? exc.message : "Triage workflow failed");
      setStormState("critical");
    } finally {
      setWorkflowLoading(false);
    }
  }

  function openInvestigation(inv: Investigation) {
    setSelected(inv);
    setActive("investigations");
  }

  if (loading) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-slate-950 text-slate-200">
        <div className="flex items-center gap-3 rounded-lg border border-slate-700 bg-slate-900 px-4 py-3 text-sm">
          <Sparkles className="size-4 animate-pulse text-cyan-300" />
          Loading PITER AiOps...
        </div>
      </main>
    );
  }

  if (error) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-slate-950 p-6 text-slate-200">
        <div className="max-w-md rounded-lg border border-red-500/30 bg-red-950/40 p-5">
          <div className="font-semibold text-red-100">Could not load PITER AiOps</div>
          <p className="mt-2 text-sm text-red-100/75">{error}</p>
        </div>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-[#08111f] text-slate-100">
      <div className="grid min-h-screen grid-cols-[250px_minmax(0,1fr)] max-[980px]:grid-cols-1">
        <Sidebar active={active} setActive={setActive} useBedrock={data?.use_bedrock ?? false} />
        <section className="min-w-0">
          <TopBar
            active={active}
            modelLabel={modelLabel}
            executionLabel={executionLabel}
            notificationMode={notificationMode}
            useBedrock={data?.use_bedrock ?? false}
            onAskAgent={() => askAgent()}
          />
          <div className="mx-auto max-w-[1540px] px-5 py-5 xl:pr-[380px]">
            {active === "dashboard" && (
              <Dashboard
                startStorm={() => {
                  setActive("storm");
                  startStorm();
                }}
                kpiCards={kpiCards}
                streamSummary={streamSummary}
                onOpenInvestigations={() => setActive("investigations")}
                onOpenStorm={() => setActive("storm")}
              />
            )}
            {active === "investigations" && (
              <Investigations
                investigations={investigations}
                selected={selected}
                setSelected={setSelected}
                openInvestigation={openInvestigation}
                triageCard={triageCard}
                answer={answer}
                getInvStatus={getInvStatus}
                updateInvStatus={updateInvStatus}
                onAskAgent={() => askAgent()}
              />
            )}
            {active === "storm" && (
              <AlertStorm
                stormState={stormState}
                startStorm={startStorm}
                pauseStorm={pauseStorm}
                resetStorm={resetStorm}
                continueLiveStorm={continueLiveStorm}
                p1Dismissed={p1Dismissed}
                runWorkflow={runWorkflow}
                workflowLoading={workflowLoading}
                stormMarkedResolved={stormMarkedResolved}
                onMarkResolved={markStormResolved}
                mttrMinutes={mttrMinutes}
                answer={answer}
                triageCard={triageCard}
                selected={selected}
                streamSummary={streamSummary}
                alertCorpus={alertCorpus}
                landingAlerts={landingAlerts}
                stormVisibleCount={stormVisibleCount}
                notificationMode={notificationMode}
                liveDispatchEnabled={liveDispatchEnabled}
                onOpenEscalation={() => setEscalationModalOpen(true)}
                onOpenChat={() => setActive("chat")}
                sessionHistory={sessionHistory}
              />
            )}
            {active === "chat" && (
              <ChatWorkspace
                selected={selected}
                sessionId={sessionId}
                chatTurns={chatTurns}
                chatInput={chatInput}
                setChatInput={setChatInput}
                askAgent={askAgent}
                loading={chatLoading}
                error={chatError}
                memoryUsed={memoryUsed}
                triageCard={triageCard}
                onResetMemory={resetMemoryPreview}
              />
            )}
            {active === "memory" && (
              <ContextMemory
                sessionId={sessionId}
                lastQuestion={lastQuestion}
                lastAnswer={answer?.answer ?? null}
                memoryUsed={memoryUsed}
                triageCard={triageCard}
                selected={selected}
                chatTurns={chatTurns}
                sessionHistory={sessionHistory}
                onReset={resetMemoryPreview}
              />
            )}
            {active === "knowledge" && (
              <KnowledgeBase
                citations={answer?.citations ?? []}
                kbDocs={kbDocs}
                allowedTypes={data?.allowed_types ?? [".csv", ".json", ".md", ".txt", ".pdf", ".docx"]}
                maxUploadMb={data?.max_upload_mb ?? 5}
                onRefresh={() =>
                  fetchKbManifest()
                    .then((manifest) => setKbDocs(manifest.documents))
                    .catch(() => setKbDocs([]))
                }
                onAskAboutDoc={(title) => {
                  setChatInput(`Ask about uploaded document: ${title}`);
                  askAgent(`Summarize relevance of ${title} for bet-service P1 on GIB-UKGC`);
                }}
              />
            )}
            {active === "tools" && (
              <ToolsPanel triageCard={triageCard} notificationMode={notificationMode} />
            )}
            {active === "architecture" && <Architecture data={data} />}
            {active === "settings" && (
              <Settings notificationMode={notificationMode} data={data} />
            )}
          </div>
        </section>
      </div>
      <AgentPanel
        selected={selected}
        triageCard={triageCard}
        chatInput={chatInput}
        setChatInput={setChatInput}
        askAgent={askAgent}
        loading={chatLoading || uploadLoading}
        error={chatError}
        lastQuestion={lastQuestion}
        memoryUsed={memoryUsed}
        executionLabel={executionLabel}
        chatTurns={chatTurns}
        onResetMemory={resetMemoryPreview}
        allowedTypes={data?.allowed_types ?? [".csv", ".json", ".md", ".txt", ".pdf", ".docx"]}
        maxUploadMb={data?.max_upload_mb ?? 5}
        uploadLoading={uploadLoading}
        onUpload={handleChatUpload}
        uploadInputRef={chatUploadRef}
        canMarkResolved={stormState === "resolved" && Boolean(triageCard) && !stormMarkedResolved}
        onMarkResolved={markStormResolved}
        stormMarkedResolved={stormMarkedResolved}
        mttrMinutes={mttrMinutes}
      />
      <EscalationNotifyModal
        open={escalationModalOpen}
        onClose={() => setEscalationModalOpen(false)}
        incidentId={escalationContext.incident_id}
        service={escalationContext.service}
        severity={escalationContext.severity}
        escalationContext={escalationContext}
        notificationMode={notificationMode}
        liveDispatchEnabled={liveDispatchEnabled}
        demoSmsConfigured={demoSmsConfigured}
        demoWhatsappConfigured={demoWhatsappConfigured}
        demoEmailConfigured={demoEmailConfigured}
        smsDeliveryReady={smsDeliveryReady}
        smsConsoleUrl={smsConsoleUrl}
        smsBillingUrl={smsBillingUrl}
      />
    </main>
  );
}

export default function App() {
  return <AppShell />;
}

function Sidebar({
  active,
  setActive,
  useBedrock,
}: {
  active: NavKey;
  setActive: (key: NavKey) => void;
  useBedrock: boolean;
}) {
  return (
    <aside className="border-r border-slate-800 bg-[#0c0f14] px-4 py-4 max-[980px]:border-b max-[980px]:border-r-0">
      <div className="flex items-center gap-3 rounded-lg border border-slate-700/80 bg-slate-900/60 px-3 py-3">
        <div className="flex size-10 items-center justify-center rounded-md bg-violet-600 text-white">
          <Zap className="size-5" />
        </div>
        <div>
          <div className="text-sm font-semibold tracking-wide">PITER AiOps</div>
          <div className="text-[11px] uppercase tracking-[0.15em] text-slate-400">
            Incident Operations
          </div>
        </div>
      </div>
      <nav className="mt-5 grid gap-1 max-[980px]:grid-cols-4 max-[700px]:grid-cols-2">
        {NAV_ITEMS.map((item) => (
          <button
            key={item.key}
            type="button"
            onClick={() => setActive(item.key)}
            className={classNames(
              "flex items-center gap-2 rounded-md px-3 py-2 text-left text-sm transition",
              active === item.key
                ? "bg-violet-600/15 text-violet-100 shadow-[inset_0_0_0_1px_rgba(139,92,246,0.25)]"
                : "text-slate-400 hover:bg-slate-800/70 hover:text-slate-100",
            )}
          >
            <item.icon className="size-4 shrink-0" />
            <span className="truncate">{item.label}</span>
          </button>
        ))}
      </nav>
      <div className="mt-5 rounded-lg border border-slate-700/70 bg-slate-900/70 p-3 text-xs text-slate-300">
        <div className="flex items-center gap-2 text-violet-200">
          <ShieldCheck className="size-4" />
          Guardrails active
        </div>
        <p className="mt-2 leading-relaxed text-slate-400">
          Grounded answers only. Destructive actions and policy bypass requests are blocked.
        </p>
      </div>
      <div className="mt-4 text-[10px] text-slate-600">
        v0.9.0 · Demo Build · {useBedrock ? "AWS Connected" : "Local / Mock"}
      </div>
    </aside>
  );
}

function TopBar({
  active,
  modelLabel,
  executionLabel,
  notificationMode,
  useBedrock,
  onAskAgent,
}: {
  active: NavKey;
  modelLabel: string;
  executionLabel: string;
  notificationMode: string;
  useBedrock: boolean;
  onAskAgent: () => void;
}) {
  const liveDemo = active === "storm";
  return (
    <header className="sticky top-0 z-20 border-b border-slate-800 bg-[#0c0f14]/95 px-5 py-3 backdrop-blur">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="text-xl font-semibold text-slate-100">
            {liveDemo
              ? "PITER AiOps — AI Incident Operations Center"
              : "PITER AiOps Operations Center"}
          </h1>
          <p className="mt-0.5 text-xs text-slate-500">
            {liveDemo
              ? "5-minute alert storm demo · noise suppression · grounded triage"
              : "Regulated-market incident response with source-grounded AI"}
          </p>
        </div>
        <div className="flex flex-wrap items-center gap-2 text-xs">
          <Pill tone="cyan">Demo Mode — AWS {useBedrock ? "Connected" : "Mock"}</Pill>
          <Pill tone="green">Agent: Ready</Pill>
          {!liveDemo ? (
            <>
              <Pill tone="purple">{executionLabel || modelLabel}</Pill>
              <Pill tone="amber">Notify: {notificationMode}</Pill>
            </>
          ) : null}
          <button
            type="button"
            onClick={onAskAgent}
            className="btn-primary px-3 py-1.5 text-xs"
          >
            <MessageSquare className="size-3.5" />
            Ask Agent
          </button>
        </div>
      </div>
    </header>
  );
}

function Dashboard({
  startStorm,
  kpiCards,
  streamSummary,
  onOpenInvestigations,
  onOpenStorm,
}: {
  startStorm: () => void;
  kpiCards: typeof KPI_CARDS_STATIC;
  streamSummary: AlertStreamSummary;
  onOpenInvestigations: () => void;
  onOpenStorm: () => void;
}) {
  const severityEntries = Object.entries(streamSummary.by_severity ?? {});
  return (
    <div className="grid gap-5">
      <SectionHeader
        eyebrow="Enterprise operations"
        title="PITER AiOps Dashboard"
        body="Autonomous incident operations for faster MTTR — noise suppression, enrichment, memory, and safe escalation preview."
      />
      <FilterBar>
        <FilterSelect label="Period" defaultValue="Last 30 days" />
        <FilterSelect label="Priority" defaultValue="All" />
        <FilterSelect label="Status" defaultValue="All" />
        <FilterSelect label="Source" defaultValue="All" />
      </FilterBar>
      <HeroCard
        startStorm={startStorm}
        streamSummary={streamSummary}
        onOpenStorm={onOpenStorm}
      />
      <div className="grid grid-cols-3 gap-3 max-[1280px]:grid-cols-2 max-[680px]:grid-cols-1">
        {kpiCards.map((card) => (
          <MetricCard key={card.label} {...card} />
        ))}
      </div>
      <div className="grid grid-cols-2 gap-4 max-[1100px]:grid-cols-1">
        <Panel title="Alert volume by severity" icon={Activity}>
          <div className="space-y-3">
            {severityEntries.map(([sev, count]) => (
              <ValueBar
                key={sev}
                label={`${sev} (${count})`}
                value={Math.round((count / streamSummary.total) * 100)}
              />
            ))}
          </div>
        </Panel>
        <Panel title="Response metrics" icon={Clock3}>
          <div className="grid grid-cols-2 gap-2">
            <MiniStat label="Median triage" value="4.2 min" />
            <MiniStat label="MTTR reduced" value="31 min" />
            <MiniStat label="Escalations" value="1 (preview)" />
            <MiniStat label="Tool latency p50" value="42 ms" />
          </div>
        </Panel>
        <Panel title="Unreviewed investigations" icon={Search}>
          <div className="space-y-2 text-sm text-slate-300">
            <div className="flex items-center justify-between rounded-lg border border-slate-700 bg-slate-950/50 px-3 py-2">
              <span>INV-2026-0610-005 — Kafka consumer lag</span>
              <Pill tone="amber">In Review</Pill>
            </div>
            <button
              type="button"
              onClick={onOpenInvestigations}
              className="cursor-pointer text-xs text-cyan-300 hover:text-cyan-100"
            >
              Open investigation queue →
            </button>
          </div>
        </Panel>
        <Panel title="Top noisy services" icon={TrendingDown}>
          <div className="space-y-2 text-sm">
            {[
              ["wallet-service", "142 grouped warnings"],
              ["auth-service", "89 synthetic spikes"],
              ["metrics-agent", "67 health checks"],
            ].map(([svc, note]) => (
              <div
                key={svc}
                className="flex justify-between rounded-lg border border-slate-700 bg-slate-950/50 px-3 py-2"
              >
                <span className="text-slate-200">{svc}</span>
                <span className="text-xs text-slate-500">{note}</span>
              </div>
            ))}
          </div>
        </Panel>
        <Panel title="Agent decisions" icon={Bot}>
          <div className="space-y-2 text-xs text-slate-300">
            <div>Grouped {streamSummary.noise_suppressed} P3/P4 alerts as noise</div>
            <div>Detected P1 on bet-service after {streamSummary.warning_signals} warnings</div>
            <div>Matched runbook + 4 enrichment tools on triage</div>
          </div>
        </Panel>
        <Panel title="Business impact" icon={Target}>
          <ValueBar label="Regulated market exposure modeled" value={72} />
          <div className="mt-3 text-sm text-slate-400">
            Early P1 detection and rollback guidance reduced estimated revenue exposure during the storm window.
          </div>
        </Panel>
      </div>
      <div className="grid grid-cols-[1.35fr_0.65fr] gap-4 max-[1100px]:grid-cols-1">
        <Panel title="PITER alert-to-resolution pipeline" icon={GitBranch}>
          <div className="grid grid-cols-5 gap-2 max-[900px]:grid-cols-1">
            {PIPELINE.map((step, index) => (
              <div
                key={step.label}
                className="rounded-lg border border-slate-700/70 bg-slate-900/70 p-3"
              >
                <div className="flex items-center justify-between">
                  <span className="text-xs font-semibold text-cyan-200">{step.label}</span>
                  <span className="text-[11px] text-slate-500">0{index + 1}</span>
                </div>
                <p className="mt-2 text-xs leading-relaxed text-slate-400">{step.body}</p>
              </div>
            ))}
          </div>
        </Panel>
        <Panel title="Business value snapshot" icon={Target}>
          <div className="space-y-3">
            <ValueBar label="Noise grouped before humans" value={86} />
            <ValueBar label="RAG answers with citations" value={94} />
            <ValueBar label="Tool enrichment coverage" value={100} />
            <ValueBar label="Safe escalation readiness" value={78} />
          </div>
        </Panel>
      </div>
    </div>
  );
}

function FilterBar({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex flex-wrap items-center gap-2 rounded-lg border border-slate-700/70 bg-slate-900/40 p-2">
      {children}
    </div>
  );
}

function FilterSelect({ label, defaultValue }: { label: string; defaultValue: string }) {
  return (
    <label
      className="flex cursor-not-allowed items-center gap-2 rounded-md border border-slate-700/60 bg-slate-950/40 px-2.5 py-1.5 text-xs text-slate-400"
      title="Demo filter — display only (no backend query)"
    >
      <span className="text-slate-500">{label}</span>
      <select
        defaultValue={defaultValue}
        disabled
        className="cursor-not-allowed bg-transparent text-slate-500 outline-none"
        aria-label={`${label} (demo display only)`}
      >
        <option>{defaultValue}</option>
      </select>
    </label>
  );
}

function HeroCard({
  startStorm,
  streamSummary,
  onOpenStorm,
}: {
  startStorm: () => void;
  streamSummary: AlertStreamSummary;
  onOpenStorm: () => void;
}) {
  return (
    <section className="overflow-hidden rounded-xl border border-slate-700/80 bg-slate-900/60 p-5">
      <div className="grid grid-cols-[1.3fr_0.7fr] gap-5 max-[900px]:grid-cols-1">
        <div>
          <Pill tone="purple">Active scenario</Pill>
          <h2 className="mt-4 max-w-4xl text-3xl font-semibold tracking-tight text-white">
            Enterprise incident operations from alert storm to resolution
          </h2>
          <p className="mt-3 max-w-3xl text-sm leading-relaxed text-slate-300">
            PITER suppresses noise, enriches incidents with grounded RAG and Lambda tools,
            preserves session memory, and guides operators through Priority, Investigation,
            Triage, Escalation, and Resolution.
          </p>
          <div className="mt-5 flex flex-wrap gap-3">
            <button type="button" onClick={startStorm} className="btn-primary">
              <Play className="size-4" />
              Run alert storm
            </button>
            <button type="button" onClick={onOpenStorm} className="btn-secondary">
              Open storm workspace
              <ChevronRight className="size-4" />
            </button>
          </div>
        </div>
        <div className="rounded-lg border border-slate-700 bg-slate-950/50 p-4">
          <div className="text-xs uppercase tracking-[0.22em] text-slate-400">
            bet-service · GIB-UKGC
          </div>
          <div className="mt-3 rounded-lg border border-red-500/30 bg-red-500/10 p-3">
            <div className="flex items-center gap-2 text-sm font-semibold text-red-100">
              <AlertTriangle className="size-4" />
              P1 — 100% error rate
            </div>
            <p className="mt-2 text-xs leading-relaxed text-red-100/75">
              Warning signals precede hard failure. Escalation requires confirmation token and
              allowlisted recipient.
            </p>
          </div>
          <div className="mt-3 grid grid-cols-2 gap-2 text-xs">
            <MiniStat label="Warnings" value={String(streamSummary.warning_signals)} />
            <MiniStat label="Alerts" value={String(streamSummary.total)} />
            <MiniStat label="Suppressed" value={String(streamSummary.noise_suppressed)} />
            <MiniStat label="Corpus" value={streamSummary.label} />
          </div>
        </div>
      </div>
    </section>
  );
}

function Investigations({
  investigations,
  selected,
  setSelected,
  openInvestigation,
  triageCard,
  answer,
  getInvStatus,
  updateInvStatus,
  onAskAgent,
}: {
  investigations: Investigation[];
  selected: Investigation;
  setSelected: (inv: Investigation) => void;
  openInvestigation: (inv: Investigation) => void;
  triageCard: TriageCard | null;
  answer: RagAnswer | null;
  getInvStatus: (inv: Investigation) => string;
  updateInvStatus: (id: string, status: string) => void;
  onAskAgent: () => void;
}) {
  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set());
  const statuses = investigations.map((inv) => getInvStatus(inv));
  const counters = {
    inReview: statuses.filter((s) => s === "In Review").length,
    reviewed: statuses.filter((s) => s === "Resolved" || s === "False Positive").length,
    all: investigations.length,
    queued: 2,
    running: statuses.filter((s) => s === "Investigating" || s === "In Process").length,
    stopped: statuses.filter((s) => s === "Noise Grouped").length,
  };

  function toggleRow(id: string) {
    setSelectedIds((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  }

  return (
    <div className="grid gap-5">
      <SectionHeader
        eyebrow="Autonomous investigations"
        title="Investigation queue"
        body="Noise grouping, priority classification, RAG evidence, and tool enrichment in one operator table."
      />
      <div className="flex flex-wrap gap-2 text-xs">
        {[
          ["In Review", counters.inReview, "amber"],
          ["Reviewed", counters.reviewed, "green"],
          ["All", counters.all, "cyan"],
          ["Queued", counters.queued, "slate"],
          ["Running", counters.running, "cyan"],
          ["Stopped", counters.stopped, "green"],
        ].map(([label, count, tone]) => (
          <Pill key={String(label)} tone={String(tone)}>
            {label}: {count}
          </Pill>
        ))}
      </div>
      <FilterBar>
        <FilterSelect label="Conclusion" defaultValue="All" />
        <FilterSelect label="Alert Type" defaultValue="All" />
        <FilterSelect label="Source" defaultValue="All" />
        <FilterSelect label="Date" defaultValue="Today" />
        <input
          type="search"
          placeholder="Search investigations…"
          className="min-w-[180px] flex-1 rounded-md border border-slate-700 bg-slate-950/60 px-3 py-1.5 text-xs text-slate-200 outline-none focus:border-cyan-300/40"
          aria-label="Search investigations"
        />
        <FilterSelect label="Sort" defaultValue="ID" />
      </FilterBar>
      <Panel title="Investigation table" icon={Search}>
        <div className="overflow-x-auto">
          <table className="w-full min-w-[1200px] text-left text-sm">
            <thead className="border-b border-slate-700 text-xs uppercase tracking-wider text-slate-500">
              <tr>
                {[
                  "",
                  "Conclusion",
                  "Alert Time",
                  "ID",
                  "Alert",
                  "Service",
                  "Environment",
                  "Entities",
                  "Source",
                  "Status",
                  "Priority",
                  "Actions",
                ].map((h) => (
                  <th key={h || "select"} className="px-3 py-2 font-medium">
                    {h}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {investigations.map((inv) => {
                const status = getInvStatus(inv);
                return (
                  <tr
                    key={inv.id}
                    className={classNames(
                      "border-b border-slate-800",
                      selected.id === inv.id && "bg-cyan-300/5",
                    )}
                  >
                    <td className="px-3 py-3">
                      <input
                        type="checkbox"
                        checked={selectedIds.has(inv.id)}
                        onChange={() => toggleRow(inv.id)}
                        className="size-4 cursor-pointer accent-cyan-400"
                        aria-label={`Select ${inv.id}`}
                      />
                    </td>
                    <td className="px-3 py-3">
                      <Pill tone={conclusionTone(inv.conclusion)}>{inv.conclusion}</Pill>
                      <p className="mt-1 max-w-[220px] text-xs text-slate-500">{inv.conclusionDetail}</p>
                    </td>
                    <td className="px-3 py-3 font-mono text-xs text-slate-400">{inv.alertTime}</td>
                    <td className="px-3 py-3 font-mono text-xs text-cyan-200">{inv.id}</td>
                    <td className="px-3 py-3">{inv.alert}</td>
                    <td className="px-3 py-3">{inv.service}</td>
                    <td className="px-3 py-3">{inv.environment}</td>
                    <td className="px-3 py-3 text-slate-400">{inv.entities}</td>
                    <td className="px-3 py-3 text-slate-300">{inv.source}</td>
                    <td className="px-3 py-3">
                      <Pill tone={statusTone(status)}>{status}</Pill>
                    </td>
                    <td className="px-3 py-3">
                      <span
                        className={classNames(
                          "rounded-full border px-2 py-1 text-xs font-semibold",
                          priorityClasses(inv.priority),
                        )}
                      >
                        {inv.priority}
                      </span>
                    </td>
                    <td className="px-3 py-3">
                      <div className="flex flex-wrap gap-1">
                        <ActionBtn
                          label="Open"
                          onClick={() => {
                            setSelected(inv);
                            openInvestigation(inv);
                          }}
                        />
                        <ActionBtn label="Ask Agent" onClick={onAskAgent} />
                        <ActionBtn
                          label="In Process"
                          title="Demo UI — local status only"
                          onClick={() => updateInvStatus(inv.id, "In Process")}
                        />
                        <ActionBtn
                          label="Resolve"
                          title="Demo UI — local status only"
                          onClick={() => updateInvStatus(inv.id, "Resolved")}
                        />
                        <ActionBtn
                          label="Escalate"
                          title="Demo UI — local status only (use Escalation Preview for notify API)"
                          onClick={() => updateInvStatus(inv.id, "Escalated")}
                        />
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </Panel>
      <InvestigationDetail
        selected={selected}
        answer={answer}
        triageCard={triageCard}
        notificationMode="mock"
      />
    </div>
  );
}

function ActionBtn({
  label,
  onClick,
  title,
}: {
  label: string;
  onClick: () => void;
  title?: string;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      title={title}
      className="cursor-pointer rounded-md border border-violet-400/25 px-2 py-1 text-[11px] text-violet-100 transition-colors hover:bg-violet-500/10"
    >
      {label}
    </button>
  );
}

function AlertStorm({
  stormState,
  startStorm,
  pauseStorm,
  resetStorm,
  continueLiveStorm,
  p1Dismissed,
  runWorkflow,
  workflowLoading,
  stormMarkedResolved,
  onMarkResolved,
  mttrMinutes,
  answer,
  triageCard,
  selected,
  streamSummary,
  alertCorpus,
  landingAlerts,
  stormVisibleCount,
  notificationMode,
  liveDispatchEnabled,
  onOpenEscalation,
  onOpenChat,
  sessionHistory,
}: {
  stormState: StormState;
  startStorm: () => void;
  pauseStorm: () => void;
  resetStorm: () => void;
  continueLiveStorm: () => void;
  p1Dismissed: boolean;
  runWorkflow: () => void;
  workflowLoading: boolean;
  stormMarkedResolved: boolean;
  onMarkResolved: () => void;
  mttrMinutes: number | null;
  answer: RagAnswer | null;
  triageCard: TriageCard | null;
  selected: Investigation;
  streamSummary: AlertStreamSummary;
  alertCorpus: Record<string, string>[];
  landingAlerts: Record<string, string>[];
  stormVisibleCount: number;
  notificationMode: string;
  liveDispatchEnabled: boolean;
  onOpenEscalation: () => void;
  onOpenChat: () => void;
  sessionHistory: SessionHistoryPayload | null;
}) {
  const savedFollowups = sessionHistory?.followups ?? [];
  const progress =
    stormState === "idle"
      ? 0
      : stormState === "streaming" || stormState === "paused"
        ? stormState === "paused"
          ? 55
          : 62
        : stormState === "critical"
          ? 74
          : stormState === "investigating"
            ? 88
            : 100;

  const enrichmentSteps =
    stormState === "idle"
      ? 0
      : stormState === "streaming" || stormState === "paused"
        ? 2
        : stormState === "critical"
          ? 5
          : stormState === "investigating"
            ? 7
            : 8;

  const showP1 =
    !p1Dismissed &&
    (stormState === "critical" ||
      stormState === "investigating" ||
      stormState === "resolved");

  const streamRows = buildAlertStreamRows(alertCorpus, stormState, stormVisibleCount);
  const visibleTotal = streamRows.length;
  const alertsReceived =
    stormState === "idle" ? 0 : Math.min(visibleTotal, streamSummary.total);
  const ownerTeam =
    (triageCard?.owner?.owner_team as string | undefined) ?? "Betting Core Platform";
  const stormEscalation = buildEscalationContext(
    triageCard,
    selected,
    streamSummary,
  );

  return (
    <div className="grid gap-5">
      <div className="grid grid-cols-7 gap-2 max-[1200px]:grid-cols-4 max-[700px]:grid-cols-2">
        <MiniStat
          label="Alerts Received"
          value={stormState === "idle" ? `0 / ${streamSummary.total}` : `${alertsReceived} / ${streamSummary.total}`}
        />
        <MiniStat
          label="Noise Suppressed"
          value={stormState === "idle" ? "0" : String(streamSummary.noise_suppressed)}
        />
        <MiniStat label="Active Incidents" value={showP1 ? "1" : "0"} />
        <MiniStat
          label="P1 / P2 / P3"
          value={
            stormState === "idle"
              ? "0 / 0 / 0"
              : `${streamSummary.p1_count ?? 1} / ${streamSummary.by_severity?.P2 ?? 32} / ${streamSummary.by_severity?.P3 ?? 88}`
          }
        />
        <MiniStat label="Escalations" value={stormState === "resolved" ? "1" : "0"} />
        <MiniStat
          label="MTTR Reduced"
          value={mttrMinutes ? `${mttrMinutes} min vs baseline` : stormState === "resolved" ? "18 min vs baseline" : "0 min vs baseline"}
        />
        <MiniStat
          label="Cost Avoided"
          value={stormState === "resolved" ? "$42k" : "$0"}
        />
      </div>

      <div className="flex flex-wrap items-center gap-2">
        <button
          type="button"
          onClick={startStorm}
          disabled={stormState === "investigating" || workflowLoading}
          className="btn-primary"
        >
          <Play className="size-4" />
          Start 5-Min Alert Storm
        </button>
        <button
          type="button"
          onClick={pauseStorm}
          disabled={stormState !== "streaming"}
          className="btn-secondary"
        >
          Pause
        </button>
        <button
          type="button"
          onClick={() => {
            if (stormState === "paused") startStorm();
          }}
          disabled={stormState !== "paused"}
          className="btn-secondary"
        >
          Continue Live
        </button>
        <button
          type="button"
          onClick={resetStorm}
          className="btn-secondary"
        >
          Reset
        </button>
      </div>

      <P1CandidateCard
        showActions={showP1}
        title="P1 bet-service 100% error rate on GIB-UKGC"
        description="Business risk: regulated betting unavailable during peak window. Revenue, customer trust, and SLA exposure are material. Alert storm paused for human review — run PITER analysis to produce a source-grounded action plan."
        onAnalyze={runWorkflow}
        onEscalate={onOpenEscalation}
        onChat={onOpenChat}
        onContinue={continueLiveStorm}
        analyzing={workflowLoading}
        triageComplete={stormState === "resolved" && Boolean(triageCard)}
      />

      <div className="grid grid-cols-[1.1fr_0.9fr] gap-4 max-[1100px]:grid-cols-1">
        <Panel title="Alert Stream" icon={TerminalSquare}>
          {stormState === "idle" ? (
            landingAlerts.length ? (
              <div className="grid gap-2">
                <p className="text-sm text-slate-500">
                  {landingAlerts.length} active alerts (noise candidates hidden). Start the storm for
                  full playback.
                </p>
                <AlertStreamTable
                  rows={landingAlerts.map(rowToStreamRow)}
                  visibleTotal={landingAlerts.length}
                  total={streamSummary.total}
                />
              </div>
            ) : (
              <p className="text-sm text-slate-500">
                No alerts yet. Press Start 5-Min Alert Storm.
              </p>
            )
          ) : (
            <AlertStreamTable
              rows={streamRows}
              visibleTotal={visibleTotal}
              total={streamSummary.total}
            />
          )}
        </Panel>
        <Panel title="Agent Decisions" icon={Target}>
          {stormState === "idle" ? (
            <p className="text-sm text-slate-500">Agent idle.</p>
          ) : (
            <AgentDecisionsLog stormState={stormState} noiseSuppressed={streamSummary.noise_suppressed} />
          )}
        </Panel>
      </div>

      <div className="grid grid-cols-2 gap-4 max-[900px]:grid-cols-1">
        <NoisePatternCard visible={stormState !== "idle"} suppressed={streamSummary.noise_suppressed} />
        <IncidentQueuePanel stormState={stormState} showP1={showP1} />
      </div>

      <div className="grid grid-cols-2 gap-4 max-[900px]:grid-cols-1">
        <McpToolCallsPanel
          stormState={stormState}
          triageComplete={stormState === "resolved" && Boolean(triageCard)}
        />
        <BusinessImpactPanel
          stormState={stormState}
          noiseSuppressed={streamSummary.noise_suppressed}
          mttrMinutes={mttrMinutes}
        />
      </div>

      {(stormState === "investigating" || stormState === "resolved") && (
        <AgentEnrichmentPipeline activeCount={enrichmentSteps} />
      )}

      <div className="rounded-xl border border-slate-700/80 bg-slate-900/40 p-4">
        <div className="mb-2 flex justify-between text-xs text-slate-400">
          <span>Storm progress</span>
          <span>{progress}%</span>
        </div>
        <div className="h-2 rounded-full bg-slate-800">
          <div
            className="h-full rounded-full bg-cyan-300 transition-all duration-300"
            style={{ width: `${progress}%` }}
          />
        </div>
      </div>

      <Panel title="PITER workflow pipeline" icon={GitBranch}>
        <div className="grid grid-cols-5 gap-2 max-[900px]:grid-cols-1">
          {PIPELINE.map((step, index) => (
            <div
              key={step.label}
              className="rounded-lg border border-cyan-300/15 bg-slate-900/70 p-3"
            >
              <div className="flex items-center justify-between">
                <span className="font-semibold text-cyan-100">{step.label}</span>
                {stormState === "resolved" || index < enrichmentSteps ? (
                  <CheckCircle2 className="size-4 text-emerald-300" />
                ) : (
                  <Clock3 className="size-4 text-slate-500" />
                )}
              </div>
              <p className="mt-2 text-xs leading-relaxed text-slate-400">{step.body}</p>
            </div>
          ))}
        </div>
        <div className="mt-4 rounded-lg border border-slate-700 bg-slate-950/50 p-3">
          <div className="text-xs font-semibold uppercase tracking-wider text-slate-500">
            Saved backend chat history
          </div>
          <div className="mt-2 grid gap-2">
            {savedFollowups.length ? (
              savedFollowups.slice(-4).map((turn) => (
                <div
                  key={`${turn.ts}-${turn.question}`}
                  className="rounded border border-slate-800 bg-slate-900/70 p-2 text-xs"
                >
                  <div className="font-semibold text-cyan-100">{turn.question}</div>
                  <p className="mt-1 line-clamp-2 text-slate-400">{turn.answer.answer}</p>
                </div>
              ))
            ) : (
              <div className="rounded border border-slate-800 bg-slate-900/70 p-2 text-xs text-slate-500">
                Run a follow-up after PITER analysis to persist chat history for this session.
              </div>
            )}
          </div>
        </div>
      </Panel>

      {stormState === "resolved" && (
        <>
          <Panel title="Resolution summary" icon={Target}>
            <div className="grid grid-cols-4 gap-2 max-[900px]:grid-cols-2">
              <MiniStat label="Alerts processed" value={String(streamSummary.total)} />
              <MiniStat label="Noise suppressed" value={String(streamSummary.noise_suppressed)} />
              <MiniStat label="Triage mode" value={triageCard?.mode ?? "pending"} />
              <MiniStat
                label="Historical MTTR"
                value={mttrMinutes ? `${mttrMinutes} min` : "—"}
              />
            </div>
            <div className="mt-4 flex flex-wrap items-center gap-2">
              {stormMarkedResolved ? (
                <span className="inline-flex items-center gap-1.5 rounded-md border border-emerald-400/30 bg-emerald-400/10 px-3 py-2 text-sm font-medium text-emerald-100">
                  <CheckCircle2 className="size-4" />
                  Incident resolved
                </span>
              ) : (
                <button
                  type="button"
                  onClick={onMarkResolved}
                  className="cursor-pointer rounded-md bg-emerald-400 px-4 py-2 text-sm font-semibold text-slate-950 hover:bg-emerald-300"
                >
                  Mark incident resolved
                </button>
              )}
              <button
                type="button"
                onClick={onOpenChat}
                className="cursor-pointer rounded-md border border-slate-600 px-4 py-2 text-sm text-slate-200 hover:bg-slate-800"
              >
                Continue in agent chat
              </button>
            </div>
          </Panel>
          <EscalationTriggeredCard
            visible
            incidentTitle={`${stormEscalation.severity} — ${stormEscalation.incident_title}`}
            ownerTeam={stormEscalation.owner_team ?? ownerTeam}
            onCallRole={stormEscalation.on_call_name ?? "Primary on-call"}
            notificationMode={notificationMode}
            liveDispatchEnabled={liveDispatchEnabled}
            onEscalateLive={onOpenEscalation}
            payloadLines={[
              `Affected service: ${stormEscalation.service}`,
              `Business impact: ${stormEscalation.business_impact ?? "Under assessment"}`,
              `Recent deployment: ${stormEscalation.recent_deployment ?? "via piter-recent-deployments"}`,
              `Top logs: ${stormEscalation.top_error ?? "see console"}`,
              `Customer support: ${stormEscalation.support_complaints ?? "monitoring"}`,
              `Runbook sources (${stormEscalation.runbook_count ?? 5})`,
              `Recommended first actions (${stormEscalation.recommended_actions?.length ?? 6})`,
              `War room: ${stormEscalation.war_room_channel ?? "#war-room"}`,
            ]}
          />
        </>
      )}

      <InvestigationDetail
        selected={selected}
        answer={answer}
        triageCard={triageCard}
        notificationMode={notificationMode}
        streamSummary={streamSummary}
      />
    </div>
  );
}

function rowToStreamRow(row: Record<string, string>): StreamRow {
  const ts = row.timestamp ?? "";
  const time = ts.includes("T") ? (ts.split("T")[1]?.replace(".000Z", "") ?? ts) : ts;
  const severity = row.severity ?? "P4";
  const isP1 = severity === "P1" || row.is_trigger === "true";
  const isWarn = String(row.alert_id ?? "").startsWith("ALT-DEMO-WARN");
  const status =
    isP1
      ? "critical"
      : row.status === "auto-resolved" || (severity === "P4" && !isWarn)
        ? "suppressed"
        : isWarn
          ? "warning"
          : severity === "P3"
            ? "suppressed"
            : "active";
  return {
    time,
    service: row.service ?? "",
    alert: row.title ?? row.alert_id ?? "",
    severity,
    status,
  };
}

function buildAlertStreamRows(
  corpus: Record<string, string>[],
  stormState: StormState,
  visibleCount: number,
): StreamRow[] {
  if (stormState === "idle" || !corpus.length) return [];

  const sorted = [...corpus].sort(
    (a, b) => parseFloat(a.seconds_offset ?? "0") - parseFloat(b.seconds_offset ?? "0"),
  );

  if (stormState === "streaming" || stormState === "paused") {
    const preP1 = sorted.filter((r) => r.severity !== "P1" && r.is_trigger !== "true");
    const limit = Math.min(visibleCount, preP1.length);
    return preP1.slice(0, limit).map(rowToStreamRow);
  }

  return sorted.map(rowToStreamRow);
}

function InvestigationDetail({
  selected,
  answer,
  triageCard,
  notificationMode = "mock",
  streamSummary,
}: {
  selected: Investigation;
  answer: RagAnswer | null;
  triageCard: TriageCard | null;
  notificationMode?: string;
  streamSummary?: AlertStreamSummary;
}) {
  const triageSteps = triageCard?.recommended_steps ?? [
    "Check bet-service health and circuit breaker state.",
    "Compare deploy timestamp with first warning shot.",
    "Validate database and Kafka dependency health.",
  ];
  const impactText =
    (triageCard?.impact?.business_impact as string | undefined) ?? selected.impact;
  const ownerTeam =
    (triageCard?.owner?.owner_team as string | undefined) ?? "Betting Core";
  const similar =
    triageCard?.similar_incidents?.slice(0, 2).map((s) => {
      const label = s.incident_id ?? s.root_cause ?? "similar incident";
      return String(label);
    }) ?? [];
  const deploys =
    triageCard?.suspect_deploys?.slice(0, 2).map((d) => {
      const dep = d as Record<string, unknown>;
      return String(dep.version ?? dep.deploy_id ?? dep.service ?? "deploy");
    }) ?? [];

  const postMortem = {
    summary: selected.alert,
    timeline: WARNING_ALERTS.join(" → "),
    customerImpact: "Betting unavailable for regulated GIB-UKGC users during peak window.",
    businessImpact: impactText,
    rootCause:
      triageCard?.answer?.slice(0, 120) ??
      "Root-cause hypothesis: bad deploy or dependency saturation on bet-service.",
    actionsTaken: triageSteps.slice(0, 3).join("; "),
    validation: "Monitor error rate, settlement lag, and rollback health for 10 minutes.",
    followUp: "Add pre-P1 warning detector; review connection pool sizing.",
    prevention: "Canary deploy gates + automated rollback playbook for bet-service.",
  };

  return (
    <div className="grid grid-cols-[1.15fr_0.85fr] gap-4 max-[1100px]:grid-cols-1">
      <Panel title="Investigation workspace" icon={FileText}>
        <div className="grid gap-4">
          <div className="rounded-lg border border-red-500/30 bg-red-500/10 p-4">
            <div className="flex flex-wrap items-center justify-between gap-3">
              <div>
                <div className="text-xs uppercase tracking-wider text-red-100/70">Priority</div>
                <h3 className="mt-1 text-xl font-semibold text-red-50">{selected.alert}</h3>
              </div>
              <span
                className={classNames(
                  "rounded-full border px-3 py-1 text-sm font-semibold",
                  priorityClasses(selected.priority),
                )}
              >
                {selected.priority}
              </span>
            </div>
            <p className="mt-3 text-sm leading-relaxed text-red-100/80">
              PITER classified this as a critical regulated-market incident because the affected
              service is customer-facing, the error rate reached 100%, and business impact is
              material.
            </p>
          </div>
          {triageCard && (
            <MetadataGrid
              items={[
                { label: "Affected service", value: selected.service },
                {
                  label: "Noise reduction",
                  value: `${streamSummary?.noise_suppressed ?? 366} duplicate alerts suppressed`,
                },
                {
                  label: "Detected pattern",
                  value: `${streamSummary?.warning_signals ?? 5} warning signals before P1`,
                },
                {
                  label: "Recent deployment",
                  value: deploys[0] ?? "via piter-recent-deployments",
                },
                { label: "Confidence", value: triageCard.grounded ? "High (grounded)" : "Medium" },
                { label: "Execution mode", value: triageCard.mode ?? "preview" },
              ]}
            />
          )}
          <div className="grid grid-cols-2 gap-3 max-[760px]:grid-cols-1">
            <EvidenceCard
              title="Investigation findings"
              items={[
                `${streamSummaryFallbackWarnings()} warning signals preceded the P1.`,
                deploys.length
                  ? `Recent deploy correlation: ${deploys.join(", ")}`
                  : "Recent deployment correlation is available via piter-recent-deployments.",
                similar.length
                  ? `Similar incidents: ${similar.join("; ")}`
                  : "Similar incidents show rollback reduced MTTR.",
              ]}
            />
            <EvidenceCard title="Triage plan" items={triageSteps.slice(0, 4)} />
            <EvidenceCard
              title="Escalation recommendation"
              items={[
                `Owner team: ${ownerTeam}`,
                "On-call: Platform SRE (masked in preview)",
                `Notification mode: ${notificationMode} — live dispatch blocked by default`,
              ]}
            />
            <EvidenceCard
              title="Resolution plan"
              items={[
                "Roll back suspect release if correlation is confirmed.",
                "Keep queue idempotency enabled.",
                "Watch error rate and settlement lag for 10 minutes.",
              ]}
            />
            <PostMortemCard postMortem={postMortem} />
            <EvidenceCard
              title="Confidence and uncertainty"
              items={[
                triageCard?.grounded ? "Grounded answer with citations" : "Awaiting triage run",
                `Execution: ${triageCard?.mode ?? "preview"}`,
                "Uncertainty: dependency saturation vs deploy regression",
              ]}
            />
          </div>
        </div>
      </Panel>
      <Panel title="Evidence, tools, and impact" icon={Layers}>
        <div className="grid gap-3">
          <MiniStat label="Business impact" value={impactText} />
          <MiniStat label="Execution mode" value={triageCard?.mode ?? "preview"} />
          <MiniStat label="Matched runbook" value={triageCard?.matched_runbook ?? "pending triage"} />
          <CitationPreview citations={answer?.citations ?? []} />
          {deploys.length > 0 && (
            <EvidenceCard title="Recent deployments" items={deploys.map((d) => String(d))} />
          )}
          {similar.length > 0 && (
            <EvidenceCard title="Similar incidents" items={similar.map((s) => String(s))} />
          )}
          <EscalationPreview ownerTeam={ownerTeam} notificationMode={notificationMode} />
        </div>
      </Panel>
    </div>
  );
}

function streamSummaryFallbackWarnings() {
  return 4;
}

function PostMortemCard({
  postMortem,
}: {
  postMortem: {
    summary: string;
    timeline: string;
    customerImpact: string;
    businessImpact: string;
    rootCause: string;
    actionsTaken: string;
    validation: string;
    followUp: string;
    prevention: string;
  };
}) {
  return (
    <div className="rounded-lg border border-violet-400/25 bg-violet-400/5 p-3">
      <div className="text-sm font-semibold text-violet-100">Post-mortem draft</div>
      <dl className="mt-2 space-y-1.5 text-xs text-slate-400">
        {[
          ["Incident summary", postMortem.summary],
          ["Timeline", postMortem.timeline],
          ["Customer impact", postMortem.customerImpact],
          ["Business impact", postMortem.businessImpact],
          ["Root-cause hypothesis", postMortem.rootCause],
          ["Actions taken", postMortem.actionsTaken],
          ["Resolution validation", postMortem.validation],
          ["Follow-up actions", postMortem.followUp],
          ["Prevention", postMortem.prevention],
        ].map(([k, v]) => (
          <div key={k}>
            <dt className="font-medium text-slate-500">{k}</dt>
            <dd className="mt-0.5 text-slate-300">{v}</dd>
          </div>
        ))}
      </dl>
    </div>
  );
}

function EscalationPreview({
  ownerTeam,
  notificationMode,
}: {
  ownerTeam: string;
  notificationMode: string;
}) {
  return (
    <div className="rounded-lg border border-amber-400/25 bg-amber-400/10 p-3 text-sm text-amber-100">
      <div className="font-semibold">Escalation preview (safe)</div>
      <div className="mt-2 space-y-1 text-xs leading-relaxed text-amber-100/85">
        <div>Policy: P1 regulated market — immediate owner notification</div>
        <div>Owner team: {ownerTeam}</div>
        <div>On-call role: Platform SRE</div>
        <div>Recipient: +972-**-***-1234, a***@example.com (masked)</div>
        <div>Mode: {notificationMode} — idempotency key reserved</div>
        <div>Delivery: preview only — not sent</div>
      </div>
      <p className="mt-2 text-[11px] text-amber-100/70">
        Real notification sending requires explicit live mode and confirmation.
      </p>
    </div>
  );
}

function ChatWorkspace({
  selected,
  sessionId,
  chatTurns,
  chatInput,
  setChatInput,
  askAgent,
  loading,
  error,
  memoryUsed,
  triageCard,
  onResetMemory,
}: {
  selected: Investigation;
  sessionId: string;
  chatTurns: ChatTurn[];
  chatInput: string;
  setChatInput: (value: string) => void;
  askAgent: (question?: string) => void;
  loading: boolean;
  error: string | null;
  memoryUsed: boolean;
  triageCard: TriageCard | null;
  onResetMemory: () => void;
}) {
  const prompts = [
    "What should I check first?",
    "Who should I escalate this to?",
    "What changed recently?",
    "Show similar past incidents",
    "What is the business impact?",
  ];

  return (
    <div className="grid gap-5">
      <SectionHeader
        eyebrow="Session memory"
        title="Incident Chat"
        body="Follow-up questions reuse triage context and citations. Conversation history is stored per session in the browser and on the backend."
      />
      <div className="rounded-xl border border-slate-700/80 bg-slate-900/50 p-4">
        <div className="flex flex-wrap items-center justify-between gap-2">
          <div>
            <div className="font-semibold text-slate-100">{selected.alert}</div>
            <div className="text-xs text-slate-500">
              Session {sessionId} · {chatTurns.length} turns
            </div>
          </div>
          <div className="flex gap-2">
            <Pill tone={memoryUsed ? "green" : triageCard ? "cyan" : "slate"}>
              {memoryUsed ? "Memory ON" : triageCard ? "Session ready" : "Awaiting triage"}
            </Pill>
            <button
              type="button"
              onClick={onResetMemory}
              className="btn-secondary px-3 py-1.5 text-xs"
            >
              Clear history
            </button>
          </div>
        </div>
        {error ? (
          <div className="mt-3 rounded border border-red-500/30 bg-red-500/10 p-2 text-xs text-red-100">
            {error}
          </div>
        ) : null}
        <div className="mt-4 max-h-[480px] overflow-y-auto rounded-lg border border-slate-700 bg-slate-950/60 p-3">
          <ChatThread
            turns={chatTurns}
            loading={loading}
            emptyHint="Run the alert storm and Analyze Incident, then ask follow-up questions here."
          />
        </div>
        <div className="mt-3 flex flex-wrap gap-1.5">
          {prompts.map((prompt) => (
            <button
              type="button"
              key={prompt}
              onClick={() => {
                setChatInput(prompt);
                askAgent(prompt);
              }}
              className="cursor-pointer rounded-full border border-slate-700 px-2 py-1 text-[11px] text-slate-300 hover:border-cyan-300/40 hover:text-cyan-100"
            >
              {prompt}
            </button>
          ))}
        </div>
        <div className="mt-3 flex gap-2">
          <input
            value={chatInput}
            onChange={(event) => setChatInput(event.target.value)}
            onKeyDown={(event) => {
              if (event.key === "Enter") askAgent();
            }}
            className="min-w-0 flex-1 rounded-md border border-slate-700 bg-slate-950 px-3 py-2 text-sm outline-none focus:border-cyan-300/50"
            placeholder="Ask about this incident…"
          />
          <button
            type="button"
            disabled={loading}
            onClick={() => askAgent()}
            className="btn-primary px-4 py-2 text-sm disabled:opacity-60"
          >
            {loading ? "…" : "Send"}
          </button>
        </div>
      </div>
    </div>
  );
}

function ContextMemory({
  sessionId,
  lastQuestion,
  lastAnswer,
  memoryUsed,
  triageCard,
  selected,
  chatTurns,
  sessionHistory,
  onReset,
}: {
  sessionId: string;
  lastQuestion: string | null;
  lastAnswer: string | null;
  memoryUsed: boolean;
  triageCard: TriageCard | null;
  selected: Investigation;
  chatTurns: ChatTurn[];
  sessionHistory: SessionHistoryPayload | null;
  onReset: () => void;
}) {
  const savedFollowups = sessionHistory?.followups ?? [];
  return (
    <div className="grid gap-5">
      <SectionHeader
        eyebrow="Session-aware investigations"
        title="Context Memory"
        body="The system stores, summarizes, retrieves, and reuses relevant investigation context for follow-up questions. Memory is session-scoped — it does not permanently train the model."
      />
      <div className="grid grid-cols-[0.85fr_1.15fr] gap-4 max-[1000px]:grid-cols-1">
        <MemoryFlowPanel
          sessionId={sessionId}
          incidentLabel={selected.alert}
          lastQuestion={lastQuestion}
          lastAnswer={lastAnswer}
          memoryUsed={memoryUsed}
          onReset={onReset}
        />
        <Panel title="Memory logic flow" icon={Brain}>
          <div className="space-y-2 text-sm">
            {[
              { step: "1", text: "Operator runs /api/triage — session_id issued and stored" },
              { step: "2", text: "Follow-up via /api/follow-up reuses incident context + citations" },
              { step: "3", text: "memory_used=true when prior turn informs the answer" },
              { step: "4", text: "Context expires with session — no persistent model training" },
            ].map((item) => (
              <div
                key={item.step}
                className="flex gap-3 rounded-lg border border-slate-700 bg-slate-900/70 p-3"
              >
                <span className="flex size-6 shrink-0 items-center justify-center rounded-full border border-cyan-400/30 bg-cyan-400/10 text-xs font-bold text-cyan-200">
                  {item.step}
                </span>
                <span className="text-slate-300">{item.text}</span>
              </div>
            ))}
          </div>
          <div className="mt-4 rounded-lg border border-slate-700 bg-slate-950/50 p-3">
            <div className="text-xs font-semibold uppercase tracking-wider text-slate-500">
              Session transcript preview
            </div>
            <div className="mt-2 max-h-[280px] overflow-y-auto">
              <ChatThread
                turns={chatTurns}
                emptyHint="Run the alert storm workflow or ask the agent to populate memory-backed turns."
              />
            </div>
          </div>
        </Panel>
      </div>
      <Panel title="Reusable investigation history" icon={History}>
        <div className="grid gap-2">
          {[
            `Backend session: ${sessionHistory?.session_id ?? sessionId}`,
            `Priority memory: ${sessionHistory?.triage_summary.priority ?? triageCard?.priority ?? "pending"}`,
            `Matched runbook: ${sessionHistory?.triage_summary.matched_runbook ?? triageCard?.matched_runbook ?? "pending"}`,
            `Saved follow-ups: ${savedFollowups.length}`,
            "Memory rule: use incident context for follow-ups, do not store real personal contacts.",
          ].map((item) => (
            <div
              key={item}
              className="rounded-lg border border-slate-700 bg-slate-900/70 p-3 text-sm text-slate-300"
            >
              {item}
            </div>
          ))}
        </div>
      </Panel>
      <Panel title="Agent decision timeline" icon={Clock3}>
        <div className="space-y-2 text-sm text-slate-400">
          <div>T+0 — Alert storm ingested (400 deterministic alerts)</div>
          <div>T+1 — Noise suppression applied to P3/P4 repeats</div>
          <div>T+2 — P1 bet-service detected; stream paused for triage</div>
          <div>T+3 — RAG + Lambda/MCP-style tools enriched incident</div>
          <div>T+4 — Escalation preview generated (mock mode)</div>
        </div>
      </Panel>
    </div>
  );
}

function KnowledgeBase({
  citations,
  kbDocs,
  allowedTypes,
  maxUploadMb,
  onRefresh,
  onAskAboutDoc,
}: {
  citations: Citation[];
  kbDocs: KbDocumentMeta[];
  allowedTypes: string[];
  maxUploadMb: number;
  onRefresh: () => void;
  onAskAboutDoc: (title: string) => void;
}) {
  const [uploadFile, setUploadFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [uploadMsg, setUploadMsg] = useState<string | null>(null);
  const [uploadErr, setUploadErr] = useState<string | null>(null);

  const rows =
    kbDocs.length > 0
      ? kbDocs.map((doc) => ({
          name: doc.title || doc.id,
          type: doc.doc_type,
          service: doc.services,
          env: doc.environments,
          severity: doc.severity_applicable,
          status: doc.sync_status,
          score: doc.indexed ? "indexed" : "local",
          updated: doc.last_updated,
        }))
      : KB_DOCS.map((doc) => ({ ...doc, updated: "demo" }));

  async function handleUpload() {
    if (!uploadFile) {
      setUploadErr("Select a file first.");
      return;
    }
    setUploading(true);
    setUploadErr(null);
    setUploadMsg(null);
    try {
      const result = await uploadDocument(uploadFile, false);
      setUploadMsg(
        result.message ??
          "Uploaded to local/demo corpus. Automatic Bedrock KB sync only when explicitly enabled server-side.",
      );
      onRefresh();
    } catch (exc) {
      setUploadErr(exc instanceof Error ? exc.message : "Upload failed");
    } finally {
      setUploading(false);
    }
  }

  return (
    <div className="grid gap-5">
      <SectionHeader
        eyebrow="Grounded retrieval"
        title="Knowledge Base"
        body="Runbooks, environments, policies, incidents, glossary, and uploaded documents support RAG answers with visible citations."
      />
      <Panel title="Upload document" icon={Database}>
        <UploadInstructions allowedTypes={allowedTypes} maxMb={maxUploadMb} />
        <div className="flex flex-wrap items-end gap-3">
          <label className="grid gap-1 text-xs text-slate-400">
            <span className="font-medium text-slate-300">Select file</span>
            <input
              type="file"
              accept={allowedTypes.join(",")}
              onChange={(e) => setUploadFile(e.target.files?.[0] ?? null)}
              className="cursor-pointer rounded-md border border-slate-700 bg-slate-950 px-2 py-1.5 text-sm text-slate-300"
            />
          </label>
          <button
            type="button"
            disabled={uploading || !uploadFile}
            onClick={handleUpload}
            className="cursor-pointer rounded-md bg-cyan-300 px-4 py-2 text-sm font-semibold text-slate-950 disabled:opacity-50"
          >
            {uploading ? "Uploading…" : "Upload to demo corpus"}
          </button>
        </div>
        {uploadFile && (
          <p className="mt-2 text-xs text-slate-500">
            Selected: {uploadFile.name} ({Math.ceil(uploadFile.size / 1024)} KB)
          </p>
        )}
        {uploadMsg && (
          <p className="mt-2 text-xs text-emerald-300">{uploadMsg}</p>
        )}
        {uploadErr && <p className="mt-2 text-xs text-red-300">{uploadErr}</p>}
      </Panel>
      <Panel title='Inventory — "bet-service 100% error rate GIB-UKGC"' icon={Database}>
        <div className="overflow-x-auto">
          <table className="w-full min-w-[920px] text-left text-sm">
            <thead className="border-b border-slate-700 text-xs uppercase tracking-wider text-slate-500">
              <tr>
                {[
                  "Document",
                  "Type",
                  "Services",
                  "Environments",
                  "Severity",
                  "Status",
                  "Updated",
                  "Relevance",
                ].map((h) => (
                  <th key={h} className="px-3 py-2 font-medium">
                    {h}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {rows.map((doc) => (
                <tr key={doc.name} className="border-b border-slate-800">
                  <td className="px-3 py-3 text-cyan-100">{doc.name}</td>
                  <td className="px-3 py-3">
                    <DocTypeBadge type={String(doc.type)} />
                  </td>
                  <td className="px-3 py-3 text-slate-400">{doc.service}</td>
                  <td className="px-3 py-3 text-slate-400">{doc.env}</td>
                  <td className="px-3 py-3">{doc.severity}</td>
                  <td className="px-3 py-3">
                    <Pill tone="green">{doc.status}</Pill>
                  </td>
                  <td className="px-3 py-3 text-xs text-slate-500">{doc.updated}</td>
                  <td className="px-3 py-3">
                    <button
                      type="button"
                      onClick={() => onAskAboutDoc(doc.name)}
                      className="cursor-pointer font-mono text-cyan-200 hover:underline"
                    >
                      {doc.score}
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Panel>
      <CitationPreview citations={citations} />
    </div>
  );
}

function ToolsPanel({
  triageCard,
  notificationMode,
}: {
  triageCard: TriageCard | null;
  notificationMode: string;
}) {
  const enriched = Boolean(
    triageCard?.similar_incidents?.length || triageCard?.suspect_deploys?.length,
  );
  const toolMode = (name: string) =>
    name === "piter-escalation"
      ? notificationMode === "mock"
        ? "mock"
        : "preview / live-blocked"
      : triageCard
        ? "mock / preview"
        : "mock";
  return (
    <div className="grid gap-5">
      <SectionHeader
        eyebrow="Action groups and tool use"
        title="MCP / Lambda Tools"
        body="Bedrock Action Groups backed by AWS Lambda are the production tool path. MCP is represented as a standardized tool-contract layer for local/demo and future integrations — not automatically equivalent to Bedrock Action Groups."
      />
      <div className="grid grid-cols-2 gap-4 max-[980px]:grid-cols-1">
        {TOOLS.map((tool) => (
          <Panel key={tool.name} title={tool.name} icon={ServerCog}>
            <div className="space-y-3 text-sm">
              <InfoRow label="Purpose" value={tool.purpose} />
              <InfoRow label="Input schema" value={tool.input} />
              <InfoRow label="Output example" value={tool.output} />
              <InfoRow label="Status" value={tool.status} />
              <div className="flex flex-wrap gap-2">
                <Pill tone="cyan">last call {tool.latency}</Pill>
                <Pill tone={tool.used || enriched ? "green" : "amber"}>
                  {tool.used || enriched ? "used in current incident" : "idle"}
                </Pill>
                <Pill tone="purple">mode: {toolMode(tool.name)}</Pill>
              </div>
            </div>
          </Panel>
        ))}
      </div>
    </div>
  );
}

function Architecture({ data }: { data: BootstrapPayload | null | undefined }) {
  return (
    <div className="grid gap-5">
      <SectionHeader
        eyebrow="Technical walkthrough"
        title="PITER AiOps Architecture"
        body="A Flask backend serves the React console, connects to Bedrock through boto3, uses RAG citations, invokes tool-style enrichment, and falls back locally."
      />
      <div className="flex flex-wrap gap-2">
        <Pill tone="cyan">RAG: {data?.rag_backend ?? "retrieve_and_generate"}</Pill>
        <Pill tone={data?.use_bedrock ? "green" : "amber"}>
          Bedrock: {data?.use_bedrock ? "enabled" : "local fallback path"}
        </Pill>
        <Pill tone="purple">KB: {data?.kb_id ? "configured" : "local corpus"}</Pill>
        <Pill tone="amber">Lambda tools: mock/demo unless deployed</Pill>
      </div>
      <div className="grid grid-cols-4 gap-3 max-[1100px]:grid-cols-2 max-[650px]:grid-cols-1">
        {[
          ["React/Vite UI", "Recording-ready SOC console, investigation workspace, agent chat."],
          ["Flask APIs", "/ask, /api/bootstrap, /api/triage, /api/follow-up, /documents/upload."],
          [
            "Bedrock KB",
            "Grounded RAG answers with source citations and retrieve-and-generate fallback.",
          ],
          [
            "Lambda tools",
            "Four PITER tools for deploys, service context, incidents, and escalation.",
          ],
          ["Session memory", "Follow-up questions reuse incident context and session ID."],
          ["Local fallback", "If Bedrock fails, local corpus retrieval keeps the demo working."],
          ["Notification safety", "Mock by default, live-blocked unless all gates pass."],
          ["Docker", "piter-aiops:dev on localhost:8080."],
        ].map(([title, body]) => (
          <div key={title} className="rounded-lg border border-slate-700 bg-slate-900/70 p-4">
            <div className="font-semibold text-cyan-100">{title}</div>
            <p className="mt-2 text-sm leading-relaxed text-slate-400">{body}</p>
          </div>
        ))}
      </div>
    </div>
  );
}

function Settings({
  notificationMode,
  data,
}: {
  notificationMode: string;
  data: BootstrapPayload | null | undefined;
}) {
  return (
    <div className="grid gap-5">
      <SectionHeader
        eyebrow="Platform"
        title="Settings"
        body="Execution mode, guardrails, notification gates, and AWS integration status."
      />
      <div className="grid grid-cols-2 gap-4 max-[900px]:grid-cols-1">
        <Panel title="Backend / AWS status" icon={ServerCog}>
          <div className="space-y-3 text-sm">
            <InfoRow
              label="Execution mode"
              value={data?.execution_mode_hint ?? "Direct Bedrock KB / local fallback"}
            />
            <InfoRow label="RAG backend" value={data?.rag_backend ?? "retrieve_and_generate"} />
            <InfoRow label="Knowledge Base" value={data?.kb_id || "local demo corpus"} />
            <InfoRow label="Guardrails" value="configured server-side when Bedrock enabled" />
            <InfoRow label="Lambda tools" value="mock/demo — deploy blocked in presentation" />
            <InfoRow label="Memory" value="session-scoped follow-up via /api/follow-up" />
            <InfoRow label="Docker / local" value="localhost:8080 — /health returns 200" />
          </div>
        </Panel>
        <Panel title="Escalation and notification safety" icon={Lock}>
          <div className="space-y-3 text-sm">
            <InfoRow label="Default mode" value={notificationMode} />
            <InfoRow
              label="Live dispatch"
              value={
                data?.notification?.live_dispatch_enabled
                  ? "enabled (PITER_ENABLE_LIVE_DISPATCH=true)"
                  : "disabled — set PITER_ENABLE_LIVE_DISPATCH=true"
              }
            />
            <InfoRow
              label="SMS ready"
              value={
                !data?.notification?.demo_sms_configured
                  ? "set PITER_DEMO_SMS_RECIPIENT"
                  : data?.notification?.sms_delivery_ready
                    ? "AWS SMS enabled — demo recipient configured"
                    : data?.notification?.sms_delivery_message ??
                      "Enable AWS End User Messaging SMS (see console link below)"
              }
            />
            {data?.notification?.demo_sms_configured &&
              data?.notification?.sms_delivery_ready === false &&
              data?.notification?.sms_console_url ? (
              <p className="text-xs text-amber-700 dark:text-amber-300">
                SMS console:{" "}
                <a
                  href={data.notification.sms_console_url}
                  className="underline"
                  target="_blank"
                  rel="noreferrer"
                >
                  Enable End User Messaging
                </a>
              </p>
            ) : null}
            <InfoRow
              label="Email ready"
              value={
                data?.notification?.email_configured && data?.notification?.demo_email_configured
                  ? "SES sender + demo recipient configured"
                  : "set PITER_SES_SENDER_EMAIL and PITER_DEMO_EMAIL_RECIPIENT"
              }
            />
            <InfoRow
              label="Allowlist entries"
              value={String(data?.notification?.allowlist_count ?? 0)}
            />
            <InfoRow label="Confirmation required" value="yes for live dispatch" />
            <InfoRow label="Idempotency" value="one send per incident/channel key" />
            <Pill tone={data?.notification?.live_dispatch_enabled ? "amber" : "green"}>
              {data?.notification?.live_dispatch_enabled
                ? "Live SNS/SES available when mode=live and token matches"
                : "Safe defaults — preview/mock unless live gates pass"}
            </Pill>
          </div>
        </Panel>
        <Panel title="Knowledge Base upload policy" icon={Database}>
          <div className="space-y-3 text-sm">
            <InfoRow
              label="Accepted types"
              value={(data?.allowed_types ?? [".csv", ".json", ".md", ".txt", ".pdf", ".docx"]).join(", ")}
            />
            <InfoRow label="Max upload size" value={`${data?.max_upload_mb ?? 5} MB`} />
            <InfoRow label="Default indexing" value="local demo corpus + optional Bedrock KB sync" />
            <InfoRow label="CSV usage" value="tabular incident data, service owners, enrichment feeds" />
            <InfoRow label="Runbook formats" value="Markdown (.md) preferred; PDF/DOCX supported" />
          </div>
        </Panel>
        <Panel title="Implemented vs mocked vs planned" icon={Archive}>
          <div className="space-y-3 text-sm">
            <InfoRow
              label="Implemented"
              value="RAG, citations, tools, memory, local fallback, demo UI"
            />
            <InfoRow
              label="Mocked"
              value="deterministic alert storm visuals; notifications unless live gates pass"
            />
            <InfoRow
              label="Planned"
              value="real MCP server, AWS redeploy, production allowlist management"
            />
          </div>
        </Panel>
      </div>
    </div>
  );
}

function AgentPanel({
  selected,
  triageCard,
  chatInput,
  setChatInput,
  askAgent,
  loading,
  error,
  lastQuestion,
  memoryUsed,
  executionLabel,
  chatTurns,
  onResetMemory,
  allowedTypes,
  maxUploadMb,
  uploadLoading,
  onUpload,
  uploadInputRef,
  canMarkResolved,
  onMarkResolved,
  stormMarkedResolved,
  mttrMinutes,
}: {
  selected: Investigation;
  triageCard: TriageCard | null;
  chatInput: string;
  setChatInput: (value: string) => void;
  askAgent: (question?: string) => void;
  loading: boolean;
  error: string | null;
  lastQuestion: string | null;
  memoryUsed: boolean;
  executionLabel: string;
  chatTurns: ChatTurn[];
  onResetMemory: () => void;
  allowedTypes: string[];
  maxUploadMb: number;
  uploadLoading: boolean;
  onUpload: (file: File) => void;
  uploadInputRef: RefObject<HTMLInputElement | null>;
  canMarkResolved: boolean;
  onMarkResolved: () => void;
  stormMarkedResolved: boolean;
  mttrMinutes: number | null;
}) {
  const prompts = [
    "What should I check first?",
    "Who should I escalate this to?",
    "What changed recently?",
    "Show similar past incidents",
    "Create post-mortem summary",
    "What is the business impact?",
  ];

  return (
    <aside className="fixed bottom-5 right-5 top-[76px] z-30 flex w-[360px] flex-col rounded-xl border border-cyan-300/20 bg-[#07101d]/95 p-4 shadow-2xl backdrop-blur max-[1250px]:static max-[1250px]:m-5 max-[1250px]:w-auto">
      <div className="flex items-center justify-between gap-2">
        <div className="flex items-center gap-2">
          <div className="flex size-9 items-center justify-center rounded-md bg-cyan-300/15 text-cyan-200">
            <Bot className="size-5" />
          </div>
          <div>
            <div className="font-semibold">Incident Chat</div>
            <div className="text-xs text-slate-500">{selected.id}</div>
          </div>
        </div>
        <Pill tone={memoryUsed ? "green" : triageCard ? "cyan" : "slate"}>
          {memoryUsed ? "Memory ON" : triageCard ? "Session ready" : "Preview"}
        </Pill>
      </div>
      <div className="mt-2 truncate text-xs text-slate-400">{selected.alert}</div>
      {mttrMinutes ? (
        <div className="mt-2 text-[11px] text-teal-200/80">
          Similar-incident MTTR baseline: {mttrMinutes} min
        </div>
      ) : null}
      <div className="mt-3 flex-1 overflow-y-auto rounded-lg border border-slate-700 bg-slate-950/60 p-3">
        {error && (
          <div className="mb-3 rounded border border-red-500/30 bg-red-500/10 p-2 text-xs text-red-100">
            {error}
          </div>
        )}
        <ChatThread
          turns={chatTurns}
          loading={loading}
          emptyHint="Run the PITER workflow or ask a follow-up to see grounded answers with source citations."
        />
      </div>
      <div className="mt-3 grid gap-2">
        <div className="flex flex-wrap gap-1.5">
          {prompts.map((prompt) => (
            <button
              type="button"
              key={prompt}
              onClick={() => {
                setChatInput(prompt);
                askAgent(prompt);
              }}
              className="cursor-pointer rounded-full border border-slate-700 px-2 py-1 text-[11px] text-slate-300 hover:border-cyan-300/40 hover:text-cyan-100"
            >
              {prompt}
            </button>
          ))}
        </div>
        <div className="flex gap-2">
          <input
            ref={uploadInputRef}
            type="file"
            className="hidden"
            accept={allowedTypes.join(",")}
            onChange={(event) => {
              const file = event.target.files?.[0];
              if (file) onUpload(file);
              event.target.value = "";
            }}
          />
          <button
            type="button"
            disabled={loading || uploadLoading}
            onClick={() => uploadInputRef.current?.click()}
            className="cursor-pointer rounded-md border border-slate-700 px-3 py-2 text-slate-300 hover:bg-slate-800 disabled:opacity-60"
            title={`Upload to KB (${allowedTypes.join(", ")}, max ${maxUploadMb}MB)`}
          >
            <Paperclip className="size-4" />
          </button>
          <input
            value={chatInput}
            onChange={(event) => setChatInput(event.target.value)}
            onKeyDown={(event) => {
              if (event.key === "Enter") askAgent();
            }}
            className="min-w-0 flex-1 rounded-md border border-slate-700 bg-slate-950 px-3 py-2 text-sm outline-none focus:border-cyan-300/50"
            placeholder="Ask about this incident…"
          />
          <button
            type="button"
            disabled={loading}
            onClick={() => askAgent()}
            className="cursor-pointer rounded-md bg-cyan-300 px-3 py-2 text-sm font-semibold text-slate-950 disabled:opacity-60"
          >
            {loading ? "…" : "Send"}
          </button>
        </div>
        {canMarkResolved ? (
          <button
            type="button"
            onClick={onMarkResolved}
            className="cursor-pointer rounded-md bg-emerald-400 px-3 py-2 text-sm font-semibold text-slate-950 hover:bg-emerald-300"
          >
            Mark incident resolved
          </button>
        ) : stormMarkedResolved ? (
          <div className="rounded-md border border-emerald-400/30 bg-emerald-400/10 px-3 py-2 text-xs text-emerald-100">
            Incident marked resolved for {selected.id}
          </div>
        ) : null}
        <div className="rounded-lg border border-slate-800 bg-slate-950/40 px-2 py-1.5 text-[10px] text-slate-500">
          <InfoRow label="Execution" value={executionLabel} />
          <InfoRow label="Last question" value={lastQuestion ?? "—"} />
        </div>
        <button
          type="button"
          onClick={onResetMemory}
          className="cursor-pointer rounded-md border border-slate-700 px-2 py-1 text-[11px] text-slate-400 hover:bg-slate-800"
        >
          Reset memory preview
        </button>
      </div>
    </aside>
  );
}

function MetricCard({
  label,
  value,
  sub,
  icon: Icon,
  tone,
}: {
  label: string;
  value: string;
  sub: string;
  icon: React.ComponentType<{ className?: string }>;
  tone: string;
}) {
  return (
    <div className="rounded-lg border border-slate-700/80 bg-slate-900/70 p-4">
      <div className="flex items-start justify-between gap-3">
        <div>
          <div className="text-xs uppercase tracking-wider text-slate-500">{label}</div>
          <div className="mt-2 text-2xl font-semibold text-white">{value}</div>
          <div className="mt-1 text-xs text-slate-500">{sub}</div>
        </div>
        <div className={classNames("rounded-md border p-2", toneClasses(tone))}>
          <Icon className="size-4" />
        </div>
      </div>
    </div>
  );
}

function Panel({
  title,
  icon: Icon,
  children,
}: {
  title: string;
  icon: React.ComponentType<{ className?: string }>;
  children: React.ReactNode;
}) {
  return (
    <section className="rounded-xl border border-slate-700/80 bg-slate-900/60 p-4">
      <div className="mb-4 flex items-center gap-2">
        <Icon className="size-4 text-cyan-300" />
        <h3 className="font-semibold">{title}</h3>
      </div>
      {children}
    </section>
  );
}

function Pill({ children, tone = "cyan" }: { children: React.ReactNode; tone?: string }) {
  return (
    <span
      className={classNames(
        "inline-flex items-center rounded-full border px-2.5 py-1 text-xs font-medium",
        toneClasses(tone),
      )}
    >
      {children}
    </span>
  );
}

function MiniStat({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-lg border border-slate-700 bg-slate-950/50 p-3">
      <div className="text-[11px] uppercase tracking-wider text-slate-500">{label}</div>
      <div className="mt-1 truncate text-sm font-semibold text-slate-100" title={value}>
        {value}
      </div>
    </div>
  );
}

function SectionHeader({ eyebrow, title, body }: { eyebrow: string; title: string; body: string }) {
  return (
    <div>
      <div className="text-xs uppercase tracking-[0.24em] text-cyan-200/70">{eyebrow}</div>
      <h2 className="mt-2 text-2xl font-semibold tracking-tight">{title}</h2>
      <p className="mt-2 max-w-4xl text-sm leading-relaxed text-slate-400">{body}</p>
    </div>
  );
}

function ValueBar({ label, value }: { label: string; value: number }) {
  return (
    <div>
      <div className="mb-1 flex justify-between text-xs text-slate-400">
        <span>{label}</span>
        <span>{value}%</span>
      </div>
      <div className="h-2 rounded-full bg-slate-800">
        <div className="h-full rounded-full bg-emerald-300" style={{ width: `${value}%` }} />
      </div>
    </div>
  );
}

function EvidenceCard({ title, items }: { title: string; items: string[] }) {
  return (
    <div className="rounded-lg border border-slate-700 bg-slate-950/45 p-3">
      <div className="text-sm font-semibold text-cyan-100">{title}</div>
      <ul className="mt-2 space-y-1.5 text-xs leading-relaxed text-slate-400">
        {items.map((item) => (
          <li key={item} className="flex gap-2">
            <CheckCircle2 className="mt-0.5 size-3.5 shrink-0 text-emerald-300" />
            <span>{item}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}

function CitationPreview({
  citations,
  compact = false,
}: {
  citations: Citation[];
  compact?: boolean;
}) {
  const usingFallback = citations.length === 0;
  const visible = usingFallback
    ? [
        {
          source_label: "deployment_rollback.md",
          snippet:
            "Check recent deployment, dependency health, and rollback availability before restarting services.",
          source_uri: "local://knowledge_base/runbooks/deployment_rollback.md",
          index: 1,
        },
        {
          source_label: "escalation_policy.md",
          snippet:
            "P1 incidents in regulated markets require immediate escalation preview and business impact assessment.",
          source_uri: "local://knowledge_base/escalation/escalation_policy.md",
          index: 2,
        },
      ]
    : citations.slice(0, compact ? 2 : 4);
  return (
    <div className="rounded-lg border border-slate-700 bg-slate-950/45 p-3">
      <div className="flex flex-wrap items-center gap-2 text-sm font-semibold text-cyan-100">
        <FileText className="size-4" />
        RAG citations
        {usingFallback ? (
          <span className="rounded border border-amber-400/30 bg-amber-400/10 px-2 py-0.5 text-[10px] font-medium uppercase tracking-wide text-amber-100">
            Example — run Analyze Incident for live citations
          </span>
        ) : null}
      </div>
      <div className="mt-2 grid gap-2">
        {visible.map((citation) => (
          <div
            key={`${citation.index}-${citation.source_label}`}
            className="rounded border border-slate-800 bg-slate-900/70 p-2 text-xs"
          >
            <div className="font-mono text-cyan-200">{citation.source_label}</div>
            <p className="mt-1 line-clamp-2 text-slate-400">
              {citation.snippet || citation.preview || citation.source_uri}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
}

function InfoRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="grid grid-cols-[115px_minmax(0,1fr)] gap-2 border-b border-slate-800 pb-2 last:border-b-0 last:pb-0">
      <div className="text-xs uppercase tracking-wider text-slate-500">{label}</div>
      <div className="min-w-0 text-sm text-slate-300">{value}</div>
    </div>
  );
}
