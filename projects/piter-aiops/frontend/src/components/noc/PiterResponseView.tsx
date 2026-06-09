import type { ReactNode } from "react";
import type { ChatResponse } from "@/types/api";
import { ConfidenceIndicator } from "./ConfidenceIndicator";
import { IncidentTimeline } from "./IncidentTimeline";
import { SourceChip } from "./SourceChip";
import { ToolResultPanel } from "./ToolResultPanel";
import { PriorityBadge } from "./PriorityBadge";

function Section({ title, children }: { title: string; children: ReactNode }) {
  if (!children) return null;
  return (
    <section className="panel">
      <h3 className="panel-title">{title}</h3>
      <div style={{ fontSize: "0.875rem", lineHeight: 1.6, whiteSpace: "pre-wrap" }}>{children}</div>
    </section>
  );
}

export function PiterResponseView({ response }: { response: ChatResponse }) {
  const piter = response.piter;

  return (
    <div className="grid-stack" style={{ marginTop: "var(--space-4)" }}>
      <div style={{ display: "flex", flexWrap: "wrap", gap: "var(--space-3)", alignItems: "center" }}>
        {piter?.priority ? <PriorityBadge priority={piter.priority as "P1"} /> : null}
        <ConfidenceIndicator level={response.confidence} />
        {response.mode ? (
          <span className="mono" style={{ color: "var(--text-muted)", fontSize: "0.75rem" }}>
            mode: {response.mode}
            {response.fallback_used ? " (fallback)" : ""}
          </span>
        ) : null}
      </div>

      <Section title="Priority">{piter?.priority}</Section>
      <Section title="Investigation findings">{piter?.investigation}</Section>
      <section className="panel">
        <h3 className="panel-title">Triage plan</h3>
        {piter?.triage ? <IncidentTimeline triage={piter.triage} /> : null}
      </section>
      <Section title="Escalation recommendation">{piter?.escalation}</Section>
      <Section title="Resolution plan">{piter?.resolution}</Section>
      <Section title="Business impact">{response.business_impact}</Section>

      {response.sources && response.sources.length > 0 ? (
        <section>
          <h3 className="panel-title">Sources</h3>
          <div className="grid-stack">
            {response.sources.map((s, i) => (
              <SourceChip key={i} source={s} index={i} />
            ))}
          </div>
        </section>
      ) : null}

      {response.tool_results && response.tool_results.length > 0 ? (
        <section>
          <h3 className="panel-title">Tool results</h3>
          {response.tool_results.map((t, i) => (
            <ToolResultPanel key={i} data={t.result} title={t.name} />
          ))}
        </section>
      ) : null}
    </div>
  );
}
