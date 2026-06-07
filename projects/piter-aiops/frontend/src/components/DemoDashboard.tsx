import { motion } from "framer-motion";
import { LayoutDashboard, Pause, Play, SkipForward } from "lucide-react";
import { useBootstrap } from "@/context/bootstrap";
import {
  useDemoTour,
  type DemoNodeId,
  DEMO_NODE_TO_BLOCK,
  PITER_TOUR_SECTIONS,
} from "@/context/demo-tour";
import { useWorkflowSession } from "@/context/workflow-session";
import { scrollToSection } from "@/lib/workflow-utils";

type DemoNode = {
  id: DemoNodeId;
  label: string;
  sub: string;
  color: string;
  tooltip: string;
};

const NODES: DemoNode[] = [
  {
    id: "priority",
    label: "PRIORITY",
    sub: "P1–P4 classification",
    color: "destructive",
    tooltip: "Priority Center: classify incoming alerts and suppress P4 noise.",
  },
  {
    id: "investigation",
    label: "INVESTIGATE",
    sub: "enrichment · KB match",
    color: "rag",
    tooltip: "Investigation Workspace: correlate deploys, logs, and similar incidents.",
  },
  {
    id: "triage",
    label: "TRIAGE",
    sub: "runbook steps",
    color: "interface",
    tooltip: "Triage Plan: ordered troubleshooting from grounded runbooks.",
  },
  {
    id: "escalation",
    label: "ESCALATE",
    sub: "on-call · policy",
    color: "agent",
    tooltip: "Escalation Hub: route P1–P3 to the right owner when Tier-1 cannot resolve.",
  },
  {
    id: "resolution",
    label: "RESOLVE",
    sub: "close · history",
    color: "resolution",
    tooltip: "Resolution Tracker: mark resolved and persist session memory.",
  },
  {
    id: "analytics",
    label: "ANALYTICS",
    sub: "MTTR · cost · confidence",
    color: "tools",
    tooltip: "Agent Analytics: session KPIs for the live demo story.",
  },
  {
    id: "kb",
    label: "KB",
    sub: "citations · sync",
    color: "ingest",
    tooltip: "Knowledge Base: grounded answers with source citations.",
  },
  {
    id: "history",
    label: "HISTORY",
    sub: "similar incidents",
    color: "destructive",
    tooltip: "Incident History: repeat patterns and prior resolutions.",
  },
];

type KpiTile = { label: string; value: string; hint: string };

export function DemoDashboard() {
  const { alerts } = useBootstrap();
  const { triageCount, resolved, sessionTotals } = useWorkflowSession();
  const {
    activeDemoNode,
    setActiveDemoNode,
    setArchitectureBlock,
    tourRunning,
    tourPaused,
    startDemoTour,
    pauseDemoTour,
    stepDemoTour,
  } = useDemoTour();

  const p1p3 = alerts.filter((a) => ["P1", "P2", "P3"].includes(a.severity)).length;
  const p4Noise = alerts.filter((a) => a.severity === "P4").length;
  const escalations = alerts.filter((a) => a.decision === "escalate").length;

  const kpis: KpiTile[] = [
    { label: "Alerts processed", value: String(alerts.length), hint: "Incoming batch" },
    { label: "Noise suppressed", value: String(p4Noise), hint: "P4 auto-resolve candidates" },
    { label: "P1–P3 detected", value: String(p1p3), hint: "Actionable incidents" },
    { label: "Incidents resolved", value: String(resolved.size), hint: "Closed this session" },
    {
      label: "MTTR reduced (avg)",
      value: triageCount > 0 ? `${Math.round(sessionTotals.minutes / triageCount)} min` : "—",
      hint: "Per triaged incident",
    },
    {
      label: "Cost avoided",
      value: `$${sessionTotals.dollars.toLocaleString()}`,
      hint: "Estimated business impact",
    },
    {
      label: "Escalations automated",
      value: String(escalations),
      hint: "Pre-built escalation paths",
    },
    {
      label: "Engineer time saved",
      value: `${sessionTotals.minutes} min`,
      hint: "Session total",
    },
    {
      label: "Resolution confidence",
      value: triageCount > 0 ? "High" : "—",
      hint: "Grounded KB citations",
    },
    {
      label: "Repeat incident rate",
      value: triageCount > 0 ? "< 12%" : "—",
      hint: "Similar-alert clustering",
    },
  ];

  function selectNode(node: DemoNode) {
    setActiveDemoNode(node.id);
    const block = DEMO_NODE_TO_BLOCK[node.id];
    if (block) setArchitectureBlock(block);
    const section = PITER_TOUR_SECTIONS.find((s) => s.node === node.id);
    if (section) scrollToSection(section.id);
  }

  return (
    <section id="agent-analytics" className="border-b border-border">
      <div className="mx-auto max-w-6xl px-6 py-16">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 text-xs uppercase tracking-wider text-[var(--tools)]">
              <LayoutDashboard className="size-3.5" />
              Agent Analytics
            </div>
            <h2 className="mt-2 text-2xl md:text-3xl font-semibold tracking-tight">
              PITER demo KPIs — Priority through Resolution
            </h2>
            <p className="mt-2 text-muted-foreground max-w-2xl">
              Play tour to walk P → I → T → E → R across the live console, then jump to
              architecture. KPI tiles update as you triage and resolve incidents.
            </p>
          </div>
          <div className="flex flex-wrap gap-2">
            <button
              type="button"
              onClick={startDemoTour}
              className="inline-flex items-center gap-2 rounded-md bg-primary px-3.5 py-2 text-sm font-medium text-primary-foreground hover:opacity-90"
            >
              <Play className="size-4" />
              Play PITER tour
            </button>
            <button
              type="button"
              onClick={pauseDemoTour}
              disabled={!tourRunning}
              className="inline-flex items-center gap-2 rounded-md border border-border bg-card/60 px-3.5 py-2 text-sm disabled:opacity-50"
            >
              <Pause className="size-4" />
              {tourPaused ? "Resume" : "Pause"}
            </button>
            <button
              type="button"
              onClick={stepDemoTour}
              className="inline-flex items-center gap-2 rounded-md border border-border bg-card/60 px-3.5 py-2 text-sm"
            >
              <SkipForward className="size-4" />
              Step
            </button>
            <button
              type="button"
              onClick={() => scrollToSection("architecture")}
              className="inline-flex items-center gap-2 rounded-md border border-border bg-card/60 px-3.5 py-2 text-sm"
            >
              Live architecture
            </button>
          </div>
        </div>

        <div className="mt-8 grid gap-3 sm:grid-cols-2 lg:grid-cols-5">
          {kpis.map((kpi) => (
            <div
              key={kpi.label}
              className="rounded-xl border border-border bg-card/60 p-4"
              title={kpi.hint}
            >
              <div className="text-[10px] uppercase tracking-wider text-muted-foreground">
                {kpi.label}
              </div>
              <div className="mt-1 text-xl font-semibold tabular-nums">{kpi.value}</div>
              <div className="mt-1 text-xs text-muted-foreground">{kpi.hint}</div>
            </div>
          ))}
        </div>

        <div className="mt-10 glass rounded-2xl p-6 md:p-8">
          <div className="text-right text-[10px] uppercase tracking-wider text-muted-foreground mb-4">
            PITER stages · click or play tour
          </div>
          <div className="flex flex-wrap items-stretch justify-center gap-4 md:gap-6">
            {NODES.map((node) => {
              const active = activeDemoNode === node.id;
              return (
                <motion.button
                  key={node.id}
                  type="button"
                  title={node.tooltip}
                  onClick={() => selectNode(node)}
                  whileHover={{ y: -2 }}
                  className="min-w-[120px] flex-1 max-w-[180px] rounded-xl border border-border bg-card/60 p-4 text-left cursor-pointer transition-colors"
                  style={{
                    boxShadow: active
                      ? `0 0 0 2px var(--${node.color}), 0 12px 36px -14px var(--${node.color})`
                      : undefined,
                    opacity: active ? 1 : 0.88,
                  }}
                >
                  <div
                    className="text-[10px] font-bold uppercase tracking-wider"
                    style={{ color: `var(--${node.color})` }}
                  >
                    {node.label}
                  </div>
                  <div className="mt-1 text-xs text-muted-foreground">{node.sub}</div>
                </motion.button>
              );
            })}
          </div>
          {activeDemoNode && (
            <p className="mt-4 text-sm text-muted-foreground">
              {NODES.find((n) => n.id === activeDemoNode)?.tooltip}
            </p>
          )}
        </div>
      </div>
    </section>
  );
}
