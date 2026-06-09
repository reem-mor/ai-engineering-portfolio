import type { ReactNode } from "react";
import type { ChatResponse } from "@/types/api";
import { parsePiterSection } from "@/lib/piter-format";
import { ConfidenceIndicator } from "./ConfidenceIndicator";
import { IncidentTimeline } from "./IncidentTimeline";
import { SourceChip } from "./SourceChip";
import { ToolResultPanel } from "./ToolResultPanel";
import { PriorityBadge } from "./PriorityBadge";
import { SafetyGuardrail } from "./SafetyGuardrail";
import { SourceBadge } from "@/components/ui/SourceBadge";
import { Card, CardHeader, CardContent } from "@/components/ui/Card";

function BulletList({ items }: { items: string[] }) {
  if (!items.length) return null;
  return (
    <ul className="piter-bullet-list">
      {items.map((item) => (
        <li key={item}>{item}</li>
      ))}
    </ul>
  );
}

function FieldGrid({ fields }: { fields: Array<{ label: string; value: ReactNode }> }) {
  const visible = fields.filter((f) => f.value);
  if (!visible.length) return null;
  return (
    <div className="piter-field-grid">
      {visible.map((f) => (
        <div key={f.label} className="piter-field">
          <div className="piter-field-label">{f.label}</div>
          <div className="piter-field-value">{f.value}</div>
        </div>
      ))}
    </div>
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
  const items = [
    d.deployment_id ? `Deployment: ${String(d.deployment_id)}` : null,
    d.version ? `Version: ${String(d.version)}` : null,
    d.deployed_at ? `Deployed: ${String(d.deployed_at)}` : null,
    d.change_summary ? String(d.change_summary) : null,
  ].filter(Boolean) as string[];
  return <BulletList items={items} />;
}

export function PiterAnalysisPanel({
  response,
  onFollowUp,
}: {
  response: ChatResponse;
  onFollowUp?: (question: string) => void;
}) {
  const piter = response.piter;
  const followups = response.recommended_followups || response.next_questions || [];
  const investigationLines = parsePiterSection(piter?.investigation || response.answer);
  const escalationLines = parsePiterSection(piter?.escalation);
  const resolutionLines = parsePiterSection(piter?.resolution);
  const triageSteps = response.recommended_steps?.length
    ? response.recommended_steps
    : parsePiterSection(piter?.triage);

  return (
    <div className="grid-stack piter-response" id="piter-analysis-panel">
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
          <SourceBadge mode={response.mode} fallbackUsed={response.fallback_used} />
        </div>
      </div>

      <SafetyGuardrail previewOnly={response.escalation_policy?.safe_preview_only === true} />

      <Card>
        <CardHeader title="Priority" />
        <CardContent>
          <FieldGrid
            fields={[
              { label: "Severity", value: piter?.priority || response.priority },
              { label: "Business impact", value: response.business_impact },
              {
                label: "Users affected",
                value: response.impact?.users_affected?.toLocaleString(),
              },
              {
                label: "Revenue risk / hr",
                value: response.impact?.revenue_impact_usd_per_hour
                  ? `$${response.impact.revenue_impact_usd_per_hour.toLocaleString()}`
                  : null,
              },
              { label: "SLA risk", value: response.impact?.sla_risk },
            ]}
          />
        </CardContent>
      </Card>

      <Card>
        <CardHeader title="Investigation" />
        <CardContent>
          <BulletList items={investigationLines} />
          {renderDeployment(response.suspect_deployment)}
          {renderSimilarIncidents(response.similar_incidents)}
        </CardContent>
      </Card>

      <Card>
        <CardHeader title="Triage" />
        <CardContent>
          {piter?.triage ? <IncidentTimeline triage={piter.triage} /> : null}
          <BulletList items={triageSteps} />
        </CardContent>
      </Card>

      <Card>
        <CardHeader title="Escalation" />
        <CardContent>
          <BulletList items={escalationLines} />
          <FieldGrid
            fields={[
              { label: "Owner team", value: response.owner?.owner_team },
              { label: "Primary on-call", value: response.owner?.primary_oncall },
              { label: "Escalation path", value: response.owner?.escalation_path },
              {
                label: "Requires escalation",
                value:
                  response.requires_escalation != null
                    ? response.requires_escalation
                      ? "Yes"
                      : "No"
                    : null,
              },
            ]}
          />
        </CardContent>
      </Card>

      <Card>
        <CardHeader title="Resolution" />
        <CardContent>
          <BulletList items={resolutionLines} />
        </CardContent>
      </Card>

      <Card>
        <CardHeader title="Confidence & sources" />
        <CardContent>
          <FieldGrid fields={[{ label: "Confidence", value: response.confidence }]} />
          {response.sources && response.sources.length > 0 ? (
            <div className="grid-stack" style={{ marginTop: "var(--space-3)" }}>
              {response.sources.map((s, i) => (
                <SourceChip key={i} source={s} index={i} />
              ))}
            </div>
          ) : null}
          {followups.length > 0 ? (
            <div style={{ marginTop: "var(--space-3)" }}>
              <div className="piter-subsection-label">Recommended follow-ups</div>
              <div className="follow-up-chips">
                {followups.slice(0, 6).map((q) => (
                  <button
                    key={q}
                    type="button"
                    className="follow-up-chip"
                    onClick={() => onFollowUp?.(q)}
                  >
                    {q}
                  </button>
                ))}
              </div>
            </div>
          ) : null}
        </CardContent>
      </Card>

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
