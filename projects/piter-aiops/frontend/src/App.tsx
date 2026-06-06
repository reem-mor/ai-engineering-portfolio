import { useMemo, useState } from "react";
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

import { askQuestion } from "@/lib/api";
import { useBootstrap } from "@/context/bootstrap";
import type { Citation, RagAnswer } from "@/types/rag";

type NavKey =
  | "dashboard"
  | "investigations"
  | "storm"
  | "memory"
  | "knowledge"
  | "tools"
  | "architecture"
  | "settings";

type Investigation = {
  id: string;
  conclusion: string;
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

type StormState = "idle" | "streaming" | "critical" | "investigating" | "resolved";

const NAV_ITEMS: {
  key: NavKey;
  label: string;
  icon: React.ComponentType<{ className?: string }>;
}[] = [
  { key: "dashboard", label: "Dashboard", icon: Gauge },
  { key: "investigations", label: "Investigations", icon: Search },
  { key: "storm", label: "Alert Storm Demo", icon: Activity },
  { key: "memory", label: "Context Memory", icon: Brain },
  { key: "knowledge", label: "Knowledge Base", icon: Database },
  { key: "tools", label: "MCP / Lambda Tools", icon: ServerCog },
  { key: "architecture", label: "Architecture", icon: Network },
  { key: "settings", label: "Settings", icon: ShieldCheck },
];

const INVESTIGATIONS: Investigation[] = [
  {
    id: "INV-2026-0610-001",
    conclusion: "Critical betting outage detected; escalation preview prepared.",
    alertTime: "10:02:55",
    alert: "bet-service 100% error rate on GIB-UKGC",
    service: "bet-service",
    environment: "GIB-UKGC",
    entities: "bet-api, postgres, kafka-settlement",
    source: "Bedrock KB + Lambda",
    status: "Escalated",
    priority: "P1",
    impact: "$9.8k/min at risk",
  },
  {
    id: "INV-2026-0610-002",
    conclusion: "Noise grouped: repeated memory warnings under threshold.",
    alertTime: "10:01:13",
    alert: "wallet-service memory utilization 78%",
    service: "wallet-service",
    environment: "NJ-DGE",
    entities: "wallet-worker-3",
    source: "Local fallback",
    status: "Noise Grouped",
    priority: "P4",
    impact: "No customer impact",
  },
  {
    id: "INV-2026-0610-003",
    conclusion: "Known pattern: replication warning correlated with previous deploy.",
    alertTime: "09:58:42",
    alert: "replication lag above 30s",
    service: "replication",
    environment: "GIB-UKGC",
    entities: "read-replica-2, wallet-service",
    source: "piter-recent-deployments",
    status: "Investigating",
    priority: "P2",
    impact: "Regulatory exposure",
  },
  {
    id: "INV-2026-0610-004",
    conclusion: "False positive: synthetic canary recovered before threshold.",
    alertTime: "09:55:07",
    alert: "auth-service canary 502 spike",
    service: "auth-service",
    environment: "MGM",
    entities: "auth-api, edge",
    source: "GuardDuty-style mock",
    status: "False Positive",
    priority: "P3",
    impact: "No sustained impact",
  },
];

const KPI_CARDS = [
  {
    label: "Alerts Processed",
    value: "399",
    sub: "deterministic storm",
    icon: Activity,
    tone: "cyan",
  },
  {
    label: "Noise Suppressed",
    value: "342",
    sub: "P3/P4 grouped",
    icon: TrendingDown,
    tone: "green",
  },
  { label: "Active Incidents", value: "3", sub: "1 critical", icon: Flame, tone: "red" },
  { label: "MTTR Reduced", value: "31 min", sub: "demo estimate", icon: Clock3, tone: "teal" },
  {
    label: "Cost Avoided",
    value: "$18.6k",
    sub: "presentation model",
    icon: Target,
    tone: "green",
  },
  { label: "Escalations", value: "1", sub: "mock preview only", icon: Bell, tone: "amber" },
  { label: "Knowledge Sources", value: "5", sub: "KB sections", icon: Database, tone: "blue" },
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
    name: "RB-001 API Gateway 5xx Spike",
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
  const [active, setActive] = useState<NavKey>("dashboard");
  const [selected, setSelected] = useState<Investigation>(INVESTIGATIONS[0]);
  const [stormState, setStormState] = useState<StormState>("idle");
  const [answer, setAnswer] = useState<RagAnswer | null>(null);
  const [chatInput, setChatInput] = useState("Who should I escalate this to?");
  const [chatLoading, setChatLoading] = useState(false);
  const [chatError, setChatError] = useState<string | null>(null);
  const [lastQuestion, setLastQuestion] = useState<string | null>(null);

  const modelLabel = data?.model_label || "Bedrock Agent / KB";
  const sessionId = answer?.session_id ?? "demo-session-preview";

  async function askAgent(question = chatInput) {
    const q = question.trim();
    if (!q) return;
    setChatLoading(true);
    setChatError(null);
    setLastQuestion(q);
    try {
      const result = await askQuestion(
        `For incident ${selected.id} (${selected.alert}), ${q}`,
        answer?.session_id ?? undefined,
      );
      setAnswer(result);
    } catch (exc) {
      setChatError(exc instanceof Error ? exc.message : "Agent request failed");
    } finally {
      setChatLoading(false);
    }
  }

  function startStorm() {
    setStormState("streaming");
    window.setTimeout(() => setStormState("critical"), 650);
  }

  async function runWorkflow() {
    setStormState("investigating");
    await askAgent("What should I check first?");
    setStormState("resolved");
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
        <Sidebar active={active} setActive={setActive} />
        <section className="min-w-0">
          <TopBar modelLabel={modelLabel} />
          <div className="mx-auto max-w-[1540px] px-5 py-5">
            {active === "dashboard" && (
              <Dashboard
                startStorm={() => {
                  setActive("storm");
                  startStorm();
                }}
              />
            )}
            {active === "investigations" && (
              <Investigations selected={selected} openInvestigation={openInvestigation} />
            )}
            {active === "storm" && (
              <AlertStorm
                stormState={stormState}
                startStorm={startStorm}
                runWorkflow={runWorkflow}
                answer={answer}
                selected={selected}
              />
            )}
            {active === "memory" && (
              <ContextMemory
                sessionId={sessionId}
                lastQuestion={lastQuestion}
                memoryUsed={Boolean(answer?.session_id)}
              />
            )}
            {active === "knowledge" && <KnowledgeBase citations={answer?.citations ?? []} />}
            {active === "tools" && <ToolsPanel />}
            {active === "architecture" && <Architecture />}
            {active === "settings" && <Settings />}
          </div>
        </section>
      </div>
      <AgentPanel
        selected={selected}
        answer={answer}
        chatInput={chatInput}
        setChatInput={setChatInput}
        askAgent={askAgent}
        loading={chatLoading}
        error={chatError}
        lastQuestion={lastQuestion}
      />
    </main>
  );
}

export default function App() {
  return <AppShell />;
}

function Sidebar({ active, setActive }: { active: NavKey; setActive: (key: NavKey) => void }) {
  return (
    <aside className="border-r border-cyan-300/10 bg-[#07101d] px-4 py-4 max-[980px]:border-b max-[980px]:border-r-0">
      <div className="flex items-center gap-3 rounded-lg border border-cyan-300/20 bg-cyan-300/10 px-3 py-3">
        <div className="flex size-10 items-center justify-center rounded-md bg-cyan-300 text-slate-950">
          <Zap className="size-5" />
        </div>
        <div>
          <div className="text-sm font-semibold tracking-wide">PITER AiOps</div>
          <div className="text-[11px] uppercase tracking-[0.2em] text-cyan-200/70">
            Autonomous Incident Ops
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
                ? "bg-cyan-300/15 text-cyan-100 shadow-[inset_0_0_0_1px_rgba(103,232,249,0.2)]"
                : "text-slate-400 hover:bg-slate-800/70 hover:text-slate-100",
            )}
          >
            <item.icon className="size-4 shrink-0" />
            <span className="truncate">{item.label}</span>
          </button>
        ))}
      </nav>
      <div className="mt-5 rounded-lg border border-slate-700/70 bg-slate-900/70 p-3 text-xs text-slate-300">
        <div className="flex items-center gap-2 text-cyan-200">
          <ShieldCheck className="size-4" />
          Presentation Mode
        </div>
        <p className="mt-2 leading-relaxed text-slate-400">
          Deterministic data, visible agent decisions, safe mock notifications, and no live
          dispatch.
        </p>
      </div>
    </aside>
  );
}

function TopBar({ modelLabel }: { modelLabel: string }) {
  return (
    <header className="sticky top-0 z-20 border-b border-cyan-300/10 bg-[#08111f]/95 px-5 py-3 backdrop-blur">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <div className="text-xs uppercase tracking-[0.25em] text-cyan-200/70">
            Priority / Investigation / Triage / Escalation / Resolution
          </div>
          <h1 className="text-xl font-semibold">PITER AiOps Operations Console</h1>
        </div>
        <div className="flex flex-wrap items-center gap-2 text-xs">
          <Pill tone="green">Health 200</Pill>
          <Pill tone="cyan">{modelLabel}</Pill>
          <Pill tone="amber">Notifications: mock</Pill>
        </div>
      </div>
    </header>
  );
}

function Dashboard({ startStorm }: { startStorm: () => void }) {
  return (
    <div className="grid gap-5">
      <HeroCard startStorm={startStorm} />
      <div className="grid grid-cols-3 gap-3 max-[1100px]:grid-cols-2 max-[680px]:grid-cols-1">
        {KPI_CARDS.map((card) => (
          <MetricCard key={card.label} {...card} />
        ))}
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

function HeroCard({ startStorm }: { startStorm: () => void }) {
  return (
    <section className="overflow-hidden rounded-xl border border-cyan-300/15 bg-[linear-gradient(135deg,rgba(15,23,42,0.96),rgba(8,47,73,0.55))] p-5">
      <div className="grid grid-cols-[1.3fr_0.7fr] gap-5 max-[900px]:grid-cols-1">
        <div>
          <Pill tone="cyan">Recording-ready demo</Pill>
          <h2 className="mt-4 max-w-4xl text-3xl font-semibold tracking-tight text-white">
            Autonomous AI incident operations from alert storm to resolution.
          </h2>
          <p className="mt-3 max-w-3xl text-sm leading-relaxed text-slate-300">
            PITER AiOps reduces MTTR by suppressing noise, enriching incidents with RAG and tools,
            remembering investigation history, previewing escalation, and guiding engineers through
            Priority, Investigation, Triage, Escalation, and Resolution.
          </p>
          <div className="mt-5 flex flex-wrap gap-3">
            <button
              type="button"
              onClick={startStorm}
              className="inline-flex items-center gap-2 rounded-md bg-cyan-300 px-4 py-2 text-sm font-semibold text-slate-950 hover:bg-cyan-200"
            >
              <Play className="size-4" />
              Start Demo
            </button>
            <a
              href="/console"
              className="inline-flex items-center gap-2 rounded-md border border-slate-600 bg-slate-900/70 px-4 py-2 text-sm text-slate-100 hover:bg-slate-800"
            >
              Keep legacy console available
              <ChevronRight className="size-4" />
            </a>
          </div>
        </div>
        <div className="rounded-lg border border-cyan-300/15 bg-slate-950/50 p-4">
          <div className="text-xs uppercase tracking-[0.22em] text-slate-400">
            Critical scenario
          </div>
          <div className="mt-3 rounded-lg border border-red-500/30 bg-red-500/10 p-3">
            <div className="flex items-center gap-2 text-sm font-semibold text-red-100">
              <AlertTriangle className="size-4" />
              P1 detected on bet-service
            </div>
            <p className="mt-2 text-xs leading-relaxed text-red-100/75">
              100% error rate in GIB-UKGC after warning signals. Escalation preview is safe and
              masked.
            </p>
          </div>
          <div className="mt-3 grid grid-cols-2 gap-2 text-xs">
            <MiniStat label="Warnings" value="4" />
            <MiniStat label="Alerts" value="399" />
            <MiniStat label="Suppressed" value="342" />
            <MiniStat label="Session" value="memory on" />
          </div>
        </div>
      </div>
    </section>
  );
}

function Investigations({
  selected,
  openInvestigation,
}: {
  selected: Investigation;
  openInvestigation: (inv: Investigation) => void;
}) {
  return (
    <div className="grid gap-5">
      <SectionHeader
        eyebrow="Autonomous investigations"
        title="Investigation queue"
        body="Noise grouping, priority classification, RAG evidence, and tool enrichment in one operator table."
      />
      <Panel title="Investigation table" icon={Search}>
        <div className="overflow-x-auto">
          <table className="w-full min-w-[1120px] text-left text-sm">
            <thead className="border-b border-slate-700 text-xs uppercase tracking-wider text-slate-500">
              <tr>
                {[
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
                  <th key={h} className="px-3 py-2 font-medium">
                    {h}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {INVESTIGATIONS.map((inv) => (
                <tr
                  key={inv.id}
                  className={classNames(
                    "border-b border-slate-800",
                    selected.id === inv.id && "bg-cyan-300/5",
                  )}
                >
                  <td className="max-w-[250px] px-3 py-3 text-slate-200">{inv.conclusion}</td>
                  <td className="px-3 py-3 font-mono text-xs text-slate-400">{inv.alertTime}</td>
                  <td className="px-3 py-3 font-mono text-xs text-cyan-200">{inv.id}</td>
                  <td className="px-3 py-3">{inv.alert}</td>
                  <td className="px-3 py-3">{inv.service}</td>
                  <td className="px-3 py-3">{inv.environment}</td>
                  <td className="px-3 py-3 text-slate-400">{inv.entities}</td>
                  <td className="px-3 py-3 text-slate-300">{inv.source}</td>
                  <td className="px-3 py-3">
                    <Pill
                      tone={
                        inv.status === "Escalated"
                          ? "red"
                          : inv.status === "Noise Grouped"
                            ? "green"
                            : "cyan"
                      }
                    >
                      {inv.status}
                    </Pill>
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
                    <button
                      type="button"
                      onClick={() => openInvestigation(inv)}
                      className="rounded-md border border-cyan-300/30 px-3 py-1.5 text-xs text-cyan-100 hover:bg-cyan-300/10"
                    >
                      Open Investigation
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Panel>
      <InvestigationDetail selected={selected} answer={null} />
    </div>
  );
}

function AlertStorm({
  stormState,
  startStorm,
  runWorkflow,
  answer,
  selected,
}: {
  stormState: StormState;
  startStorm: () => void;
  runWorkflow: () => void;
  answer: RagAnswer | null;
  selected: Investigation;
}) {
  const progress =
    stormState === "idle"
      ? 0
      : stormState === "streaming"
        ? 62
        : stormState === "critical"
          ? 74
          : stormState === "investigating"
            ? 88
            : 100;
  return (
    <div className="grid gap-5">
      <SectionHeader
        eyebrow="Main recording flow"
        title="Alert Storm Demo"
        body="A deterministic storm processes around 400 alerts, suppresses P3/P4 noise, detects a P1 on bet-service, and runs the full PITER workflow."
      />
      <div className="grid grid-cols-[0.9fr_1.1fr] gap-4 max-[1100px]:grid-cols-1">
        <Panel title="Storm controls" icon={Activity}>
          <div className="flex flex-wrap gap-3">
            <button
              type="button"
              onClick={startStorm}
              className="rounded-md bg-cyan-300 px-4 py-2 text-sm font-semibold text-slate-950 hover:bg-cyan-200"
            >
              Start alert storm
            </button>
            <button
              type="button"
              onClick={runWorkflow}
              className="rounded-md border border-red-400/40 bg-red-500/10 px-4 py-2 text-sm font-semibold text-red-100 hover:bg-red-500/20"
            >
              Run PITER workflow
            </button>
          </div>
          <div className="mt-5">
            <div className="mb-2 flex justify-between text-xs text-slate-400">
              <span>Storm progress</span>
              <span>{progress}%</span>
            </div>
            <div className="h-2 rounded-full bg-slate-800">
              <div
                className="h-full rounded-full bg-cyan-300 transition-all"
                style={{ width: `${progress}%` }}
              />
            </div>
          </div>
          <div className="mt-5 grid grid-cols-2 gap-2">
            <MiniStat label="Processed" value={stormState === "idle" ? "0" : "399"} />
            <MiniStat label="Noise suppressed" value={stormState === "idle" ? "0" : "342"} />
            <MiniStat label="Warning signals" value={stormState === "idle" ? "0" : "4"} />
            <MiniStat
              label="P1 state"
              value={
                stormState === "critical" ||
                stormState === "investigating" ||
                stormState === "resolved"
                  ? "active"
                  : "waiting"
              }
            />
          </div>
        </Panel>
        <Panel title="Live alert stream" icon={TerminalSquare}>
          <div className="space-y-2">
            {WARNING_ALERTS.map((alert, index) => {
              const visible = stormState !== "idle" && (stormState !== "streaming" || index < 4);
              const critical = index === WARNING_ALERTS.length - 1;
              return (
                <div
                  key={alert}
                  className={classNames(
                    "rounded-lg border px-3 py-2 text-sm transition",
                    visible ? "opacity-100" : "opacity-30",
                    critical
                      ? "border-red-500/40 bg-red-500/10 text-red-100"
                      : "border-slate-700 bg-slate-900/70 text-slate-300",
                  )}
                >
                  {alert}
                </div>
              );
            })}
          </div>
        </Panel>
      </div>
      <Panel title="PITER workflow result" icon={GitBranch}>
        <div className="grid grid-cols-5 gap-2 max-[900px]:grid-cols-1">
          {PIPELINE.map((step, index) => (
            <div
              key={step.label}
              className="rounded-lg border border-cyan-300/15 bg-slate-900/70 p-3"
            >
              <div className="flex items-center justify-between">
                <span className="font-semibold text-cyan-100">{step.label}</span>
                {stormState === "resolved" || index < 3 ? (
                  <CheckCircle2 className="size-4 text-emerald-300" />
                ) : (
                  <Clock3 className="size-4 text-slate-500" />
                )}
              </div>
              <p className="mt-2 text-xs leading-relaxed text-slate-400">{step.body}</p>
            </div>
          ))}
        </div>
      </Panel>
      <InvestigationDetail selected={selected} answer={answer} />
    </div>
  );
}

function InvestigationDetail({
  selected,
  answer,
}: {
  selected: Investigation;
  answer: RagAnswer | null;
}) {
  return (
    <div className="grid grid-cols-[1.15fr_0.85fr] gap-4 max-[1100px]:grid-cols-1">
      <Panel title="Investigation workspace" icon={FileText}>
        <div className="grid gap-4">
          <div className="rounded-lg border border-red-500/30 bg-red-500/10 p-4">
            <div className="flex flex-wrap items-center justify-between gap-3">
              <div>
                <div className="text-xs uppercase tracking-wider text-red-100/70">
                  Incident summary
                </div>
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
          <div className="grid grid-cols-2 gap-3 max-[760px]:grid-cols-1">
            <EvidenceCard
              title="Investigation findings"
              items={[
                "Four warning signals preceded the P1.",
                "Recent deployment correlation is available.",
                "Similar incidents show rollback reduced MTTR.",
              ]}
            />
            <EvidenceCard
              title="Triage steps"
              items={[
                "Check bet-service health and circuit breaker state.",
                "Compare deploy timestamp with first warning shot.",
                "Validate database and Kafka dependency health.",
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
            <EvidenceCard
              title="Post-mortem draft"
              items={[
                "Root-cause hypothesis: bad deploy or dependency saturation.",
                "Impact: GIB-UKGC betting unavailable.",
                "Follow-up: add pre-P1 warning detector.",
              ]}
            />
          </div>
        </div>
      </Panel>
      <Panel title="Evidence, tools, and impact" icon={Layers}>
        <div className="grid gap-3">
          <MiniStat label="Business impact" value={selected.impact} />
          <MiniStat label="Regulatory exposure" value="UKGC / GIB" />
          <MiniStat label="Recent deployment" value="DEP-2026-06-06-014" />
          <MiniStat label="Previous MTTR" value="41 min" />
          <CitationPreview citations={answer?.citations ?? []} />
          <div className="rounded-lg border border-amber-400/25 bg-amber-400/10 p-3 text-sm text-amber-100">
            <div className="font-semibold">Escalation preview</div>
            <div className="mt-1 text-xs leading-relaxed text-amber-100/80">
              Owner: Betting Core. Recipient: a***@example.com. Mode: mock. Live dispatch: blocked
              until explicit confirmation and allowlist gates pass.
            </div>
          </div>
        </div>
      </Panel>
    </div>
  );
}

function ContextMemory({
  sessionId,
  lastQuestion,
  memoryUsed,
}: {
  sessionId: string;
  lastQuestion: string | null;
  memoryUsed: boolean;
}) {
  return (
    <div className="grid gap-5">
      <SectionHeader
        eyebrow="Session-aware investigations"
        title="Context Memory"
        body="The system stores, summarizes, retrieves, and reuses relevant investigation context. It does not permanently train itself."
      />
      <div className="grid grid-cols-[0.8fr_1.2fr] gap-4 max-[1000px]:grid-cols-1">
        <Panel title="Active memory context" icon={Brain}>
          <div className="space-y-3 text-sm">
            <MiniStat label="Current incident" value="INV-2026-0610-001" />
            <MiniStat label="Session ID" value={sessionId} />
            <MiniStat label="Memory used" value={memoryUsed ? "true" : "preview"} />
            <MiniStat label="Last user question" value={lastQuestion ?? "No follow-up asked yet"} />
          </div>
        </Panel>
        <Panel title="Reusable investigation history" icon={History}>
          <div className="grid gap-2">
            {[
              "Same pattern detected today: warning shots before P1 outage.",
              "Similar incident from history: connection pool exhaustion caused bet-service errors.",
              "Past resolution reused: rollback plus dependency health validation reduced MTTR.",
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
      </div>
    </div>
  );
}

function KnowledgeBase({ citations }: { citations: Citation[] }) {
  return (
    <div className="grid gap-5">
      <SectionHeader
        eyebrow="Grounded retrieval"
        title="Knowledge Base"
        body="Organized runbooks, environments, policies, incidents, and glossary documents support RAG answers with visible citations."
      />
      <Panel title='Retrieval tester: "bet-service 100% error rate GIB-UKGC"' icon={Database}>
        <div className="overflow-x-auto">
          <table className="w-full min-w-[820px] text-left text-sm">
            <thead className="border-b border-slate-700 text-xs uppercase tracking-wider text-slate-500">
              <tr>
                {[
                  "Document",
                  "Type",
                  "Services",
                  "Environments",
                  "Severity",
                  "Status",
                  "Relevance",
                ].map((h) => (
                  <th key={h} className="px-3 py-2 font-medium">
                    {h}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {KB_DOCS.map((doc) => (
                <tr key={doc.name} className="border-b border-slate-800">
                  <td className="px-3 py-3 text-cyan-100">{doc.name}</td>
                  <td className="px-3 py-3">{doc.type}</td>
                  <td className="px-3 py-3 text-slate-400">{doc.service}</td>
                  <td className="px-3 py-3 text-slate-400">{doc.env}</td>
                  <td className="px-3 py-3">{doc.severity}</td>
                  <td className="px-3 py-3">
                    <Pill tone="green">{doc.status}</Pill>
                  </td>
                  <td className="px-3 py-3 font-mono text-cyan-200">{doc.score}</td>
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

function ToolsPanel() {
  return (
    <div className="grid gap-5">
      <SectionHeader
        eyebrow="Action groups and tool use"
        title="MCP / Lambda Tools"
        body="Bedrock action groups backed by AWS Lambda demonstrate the MCP/tools concept. A real MCP server is optional future work."
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
                <Pill tone={tool.used ? "green" : "amber"}>
                  {tool.used ? "used in current incident" : "idle"}
                </Pill>
              </div>
            </div>
          </Panel>
        ))}
      </div>
    </div>
  );
}

function Architecture() {
  return (
    <div className="grid gap-5">
      <SectionHeader
        eyebrow="Technical walkthrough"
        title="PITER AiOps Architecture"
        body="A Flask backend serves the React console, connects to Bedrock through boto3, uses RAG citations, invokes tool-style enrichment, and falls back locally."
      />
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

function Settings() {
  return (
    <div className="grid gap-5">
      <SectionHeader
        eyebrow="Safety and readiness"
        title="Settings"
        body="Presentation-safe defaults for notification mode, AWS boundaries, and live-demo controls."
      />
      <div className="grid grid-cols-2 gap-4 max-[900px]:grid-cols-1">
        <Panel title="Escalation and notification safety" icon={Lock}>
          <div className="space-y-3 text-sm">
            <InfoRow label="Default mode" value="mock" />
            <InfoRow label="Preview mode" value="safe escalation policy preview" />
            <InfoRow
              label="Live mode"
              value="blocked unless all environment and confirmation gates pass"
            />
            <InfoRow label="Masked recipients" value="+972-**-***-1234, a***@example.com" />
            <Pill tone="green">No real SNS or SES messages are sent by this UI</Pill>
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
              value="notification dispatch and deterministic alert storm visuals"
            />
            <InfoRow
              label="Planned"
              value="real MCP server, AWS redeploy, live notifications after approval"
            />
          </div>
        </Panel>
      </div>
    </div>
  );
}

function AgentPanel({
  selected,
  answer,
  chatInput,
  setChatInput,
  askAgent,
  loading,
  error,
  lastQuestion,
}: {
  selected: Investigation;
  answer: RagAnswer | null;
  chatInput: string;
  setChatInput: (value: string) => void;
  askAgent: (question?: string) => void;
  loading: boolean;
  error: string | null;
  lastQuestion: string | null;
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
      <div className="flex items-center gap-2">
        <div className="flex size-9 items-center justify-center rounded-md bg-cyan-300/15 text-cyan-200">
          <Bot className="size-5" />
        </div>
        <div>
          <div className="font-semibold">AI Analyst</div>
          <div className="text-xs text-slate-500">Right-side agent panel</div>
        </div>
      </div>
      <div className="mt-4 rounded-lg border border-slate-700 bg-slate-900/70 p-3 text-xs">
        <InfoRow label="Incident" value={selected.id} />
        <InfoRow label="Session ID" value={answer?.session_id ?? "created after first follow-up"} />
        <InfoRow label="Memory used" value={answer?.session_id ? "true" : "preview"} />
        <InfoRow label="Last question" value={lastQuestion ?? "none"} />
      </div>
      <div className="mt-4 flex-1 overflow-y-auto rounded-lg border border-slate-700 bg-slate-950/60 p-3">
        <div className="text-sm font-semibold text-cyan-100">Agent answer</div>
        {error && (
          <div className="mt-3 rounded border border-red-500/30 bg-red-500/10 p-2 text-xs text-red-100">
            {error}
          </div>
        )}
        {answer ? (
          <div className="mt-3 space-y-3 text-sm text-slate-300">
            <p className="leading-relaxed">{answer.answer}</p>
            <CitationPreview citations={answer.citations} compact />
          </div>
        ) : (
          <p className="mt-3 text-sm leading-relaxed text-slate-500">
            Ask a follow-up to prove memory and retrieve a grounded answer with citations.
          </p>
        )}
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
              className="rounded-full border border-slate-700 px-2 py-1 text-[11px] text-slate-300 hover:border-cyan-300/40 hover:text-cyan-100"
            >
              {prompt}
            </button>
          ))}
        </div>
        <div className="flex gap-2">
          <input
            value={chatInput}
            onChange={(event) => setChatInput(event.target.value)}
            onKeyDown={(event) => {
              if (event.key === "Enter") askAgent();
            }}
            className="min-w-0 flex-1 rounded-md border border-slate-700 bg-slate-950 px-3 py-2 text-sm outline-none focus:border-cyan-300/50"
            placeholder="Ask about this incident"
          />
          <button
            type="button"
            disabled={loading}
            onClick={() => askAgent()}
            className="rounded-md bg-cyan-300 px-3 py-2 text-sm font-semibold text-slate-950 disabled:opacity-60"
          >
            {loading ? "..." : "Ask"}
          </button>
        </div>
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
  const visible = citations.length
    ? citations.slice(0, compact ? 2 : 4)
    : [
        {
          source_label: "runbook_bet_service_critical.md",
          snippet:
            "Check recent deployment, dependency health, and rollback availability before restarting services.",
          source_uri: "local://knowledge_base/runbooks/runbook_bet_service_critical.md",
          index: 1,
        },
        {
          source_label: "severity-and-escalation-policy.md",
          snippet:
            "P1 incidents in regulated markets require immediate escalation preview and business impact assessment.",
          source_uri: "local://knowledge_base/policies/severity-and-escalation-policy.md",
          index: 2,
        },
      ];
  return (
    <div className="rounded-lg border border-slate-700 bg-slate-950/45 p-3">
      <div className="flex items-center gap-2 text-sm font-semibold text-cyan-100">
        <FileText className="size-4" />
        RAG citations
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
