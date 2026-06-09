import type { ReactNode } from "react";
import type { ChatResponse } from "@/types/api";
import { ConfidenceIndicator } from "./ConfidenceIndicator";
import { IncidentTimeline } from "./IncidentTimeline";
import { SourceChip } from "./SourceChip";
import { ToolResultPanel } from "./ToolResultPanel";
import { PriorityBadge } from "./PriorityBadge";

function SubSection({ label, children }: { label: string; children: ReactNode }) {
  if (!children) return null;
  return (
    <div className="piter-subsection">
      <div className="piter-subsection-label">{label}</div>
      <div className="piter-subsection-body">{children}</div>
    </div>
  );
}

function Section({ title, children }: { title: string; children: ReactNode }) {
  if (!children) return null;
  return (
    <section className="panel piter-section">
      <h3 className="panel-title">{title}</h3>
      <div className="piter-section-body">{children}</div>
    </section>
  );
}

function renderSimilarIncidents(items: unknown): ReactNode {
  if (!Array.isArray(items) || items.length === 0) return null;
  return (
    <table className="data-table data-table-compact">
      <thead>
        <tr>
          <th>ID</th>
          <th>Service</th>
          <th>Summary</th>
        </tr>
      </thead>
      <tbody>
        {items.slice(0, 5).map((row, i) => {
          const r = row as Record<string, unknown>;
          return (
            <tr key={String(r.incident_id || r.id || i)}>
              <td className="mono">{String(r.incident_id || r.id || "—")}</td>
              <td>{String(r.service || "—")}</td>
              <td>{String(r.summary || r.symptom || r.title || "—")}</td>
            </tr>
          );
        })}
      </tbody>
    </table>
  );
}

function renderDeployment(dep: unknown): ReactNode {
  if (!dep || typeof dep !== "object") return null;
  const d = dep as Record<string, unknown>;
  const suspect = d.suspect_deployment || d.deployment_id || d.version;
  if (!suspect && !d.deployed_at) return null;
  return (
    <ul className="piter-bullet-list">
      {d.deployment_id ? <li>Deployment: {String(d.deployment_id)}</li> : null}
      {d.version ? <li>Version: {String(d.version)}</li> : null}
      {d.deployed_at ? <li>Deployed: {String(d.deployed_at)}</li> : null}
      {d.change_summary ? <li>{String(d.change_summary)}</li> : null}
      {suspect && !d.deployment_id ? <li>{String(suspect)}</li> : null}
    </ul>
  );
}

function renderEscalationPolicy(policy: Record<string, unknown> | undefined): ReactNode {
  if (!policy || !Object.keys(policy).length) return null;
  return (
    <ul className="piter-bullet-list">
      {policy.owner_team ? <li>Team: {String(policy.owner_team)}</li> : null}
      {policy.primary_oncall ? <li>Primary: {String(policy.primary_oncall)}</li> : null}
      {policy.escalation_path ? <li>Path: {String(policy.escalation_path)}</li> : null}
      {policy.safe_message_preview ? (
        <li className="mono escalation-preview">{String(policy.safe_message_preview)}</li>
      ) : null}
    </ul>
  );
}

export function PiterResponseView({ response }: { response: ChatResponse }) {
  const piter = response.piter;
  const followups =
    (response as ChatResponse & { recommended_followups?: string[] }).recommended_followups ||
    (response as ChatResponse & { next_questions?: string[] }).next_questions ||
    [];

  return (
    <div className="grid-stack piter-response">
      {response.fallback_used ? (
        <div className="fallback-banner" role="status">
          Offline knowledge base — live Bedrock unavailable ({response.mode || "local_fallback"})
        </div>
      ) : null}

      <div className="piter-response-header">
        <h2 className="piter-analysis-title">PITER Incident Analysis</h2>
        <div className="piter-response-badges">
          {piter?.priority ? <PriorityBadge priority={piter.priority as "P1"} /> : null}
          <ConfidenceIndicator level={response.confidence} />
          {response.mode ? (
            <span className="mono mode-tag">
              {response.mode}
              {response.fallback_used ? " · fallback" : ""}
            </span>
          ) : null}
        </div>
      </div>

      <Section title="Priority">
        <SubSection label="Severity">{piter?.priority || response.priority}</SubSection>
        <SubSection label="Business impact">{response.business_impact}</SubSection>
      </Section>

      <Section title="Investigation">
        <div style={{ whiteSpace: "pre-wrap", fontSize: "0.875rem", lineHeight: 1.6 }}>
          {piter?.investigation || response.answer}
        </div>
        {renderDeployment(response.suspect_deployment)}
        {renderSimilarIncidents(response.similar_incidents)}
      </Section>

      <section className="panel piter-section">
        <h3 className="panel-title">Triage</h3>
        {piter?.triage ? <IncidentTimeline triage={piter.triage} /> : null}
      </section>

      <Section title="Escalation">
        {piter?.escalation ? (
          <div style={{ whiteSpace: "pre-wrap", fontSize: "0.875rem" }}>{piter.escalation}</div>
        ) : null}
        {renderEscalationPolicy(response.escalation_policy)}
      </Section>

      <Section title="Resolution">
        <div style={{ whiteSpace: "pre-wrap", fontSize: "0.875rem", lineHeight: 1.6 }}>
          {piter?.resolution}
        </div>
      </Section>

      <Section title="Confidence">
        <SubSection label="Confidence level">{response.confidence}</SubSection>
        {response.sources && response.sources.length > 0 ? (
          <div className="grid-stack" style={{ marginTop: "var(--space-3)" }}>
            <div className="piter-subsection-label">Sources</div>
            {response.sources.map((s, i) => (
              <SourceChip key={i} source={s} index={i} />
            ))}
          </div>
        ) : null}
        {followups.length > 0 ? (
          <div style={{ marginTop: "var(--space-3)" }}>
            <div className="piter-subsection-label">Recommended follow-up questions</div>
            <ul className="piter-bullet-list">
              {followups.slice(0, 6).map((q) => (
                <li key={q}>{q}</li>
              ))}
            </ul>
          </div>
        ) : null}
      </Section>

      {response.tool_results && response.tool_results.length > 0 ? (
        <section>
          <h3 className="panel-title">Enrichment tools</h3>
          {response.tool_results.map((t, i) => (
            <ToolResultPanel key={i} data={t.result} title={t.name} />
          ))}
        </section>
      ) : null}
    </div>
  );
}
