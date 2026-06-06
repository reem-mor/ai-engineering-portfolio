import { motion } from "framer-motion";
import { LayoutDashboard, Pause, Play, SkipForward } from "lucide-react";
import {
  useDemoTour,
  type DemoNodeId,
  DEMO_NODE_TO_BLOCK,
} from "@/context/demo-tour";
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
    id: "replay",
    label: "REPLAY",
    sub: "S3 JSON · controlled rate",
    color: "ingest",
    tooltip: "Demo mode: replay alert batches from S3 (presentation only).",
  },
  {
    id: "ctrl",
    label: "CTRL",
    sub: "play · pause · speed",
    color: "tools",
    tooltip: "Tour controls for the demo dashboard (client-side).",
  },
  {
    id: "bus",
    label: "BUS",
    sub: "SQS · WebSocket",
    color: "rag",
    tooltip: "Alert bus fans out to feed and KPI tiles (illustrative).",
  },
  {
    id: "feed",
    label: "FEED",
    sub: "click → triage view",
    color: "interface",
    tooltip: "Live alert feed links to the MVP triage workspace.",
  },
  {
    id: "kpi",
    label: "KPI",
    sub: "resolved · enriched · noise",
    color: "agent",
    tooltip: "Session KPIs: MTTR avoided and business impact saved.",
  },
  {
    id: "onc",
    label: "ONC",
    sub: "L1 · L2 schedule",
    color: "destructive",
    tooltip: "On-call panel for escalation paths.",
  },
  {
    id: "drill",
    label: "DRILL",
    sub: "agent trace · sources",
    color: "resolution",
    tooltip: "Drill-down shows KB citations and triage result.",
  },
];

export function DemoDashboard() {
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

  function selectNode(node: DemoNode) {
    setActiveDemoNode(node.id);
    const block = DEMO_NODE_TO_BLOCK[node.id];
    if (block) setArchitectureBlock(block);
  }

  return (
    <section id="demo-dashboard" className="border-b border-border">
      <div className="mx-auto max-w-6xl px-6 py-16">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 text-xs uppercase tracking-wider text-[var(--tools)]">
              <LayoutDashboard className="size-3.5" />
              Demo &amp; Dashboard
            </div>
            <h2 className="mt-2 text-2xl md:text-3xl font-semibold tracking-tight">
              Replay alerts → triage → KPIs
            </h2>
            <p className="mt-2 text-muted-foreground max-w-2xl">
              Presentation-only demo mode (no live SQS). Use Play tour to highlight how
              documents, the Knowledge Base, Flask, and the triage UI connect — then
              jump to the interactive architecture below.
            </p>
          </div>
          <div className="flex flex-wrap gap-2">
            <button
              type="button"
              onClick={startDemoTour}
              className="inline-flex items-center gap-2 rounded-md bg-primary px-3.5 py-2 text-sm font-medium text-primary-foreground hover:opacity-90"
            >
              <Play className="size-4" />
              Play tour
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

        <div className="mt-10 glass rounded-2xl p-6 md:p-8">
          <div className="text-right text-[10px] uppercase tracking-wider text-muted-foreground mb-4">
            diagram.demo.live · hover nodes for detail
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
