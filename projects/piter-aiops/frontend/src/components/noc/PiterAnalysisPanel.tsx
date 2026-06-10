import { useState, type ReactNode } from "react";
import type { ChatResponse } from "@/types/api";
import { useChatDock } from "@/context/chat-dock";
import { postIncidentStatus } from "@/lib/api-contract";
import { Button } from "@/components/ui/Button";
import { EscalationModal } from "@/components/demo/EscalationModal";
import { normalizeStepList, parsePiterSection, stripMarkdown } from "@/lib/piter-format";
import { CorrelationChainTimeline } from "./CorrelationChainTimeline";
import { ConfidenceIndicator } from "./ConfidenceIndicator";
import { IncidentTimeline } from "./IncidentTimeline";
import { SourceChip } from "./SourceChip";
import { ToolResultPanel } from "./ToolResultPanel";
import { PriorityBadge } from "./PriorityBadge";
import { SafetyGuardrail } from "./SafetyGuardrail";
import { SourceBadge } from "@/components/ui/SourceBadge";
import { Card, CardHeader, CardContent } from "@/components/ui/Card";
import { AgentEnrichmentPipeline } from "./AgentEnrichmentPipeline";

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
  const { openWith } = useChatDock();
  const [incidentStatus, setIncidentStatus] = useState<"open" | "in_process" | "resolved">("open");
  const [showEscalation, setShowEscalation] = useState(false);
  const piter = response.piter;
  const structured = response.structured_analysis;
  const followups = response.recommended_followups || response.next_questions || [];
  const investigationLines =
    structured?.evidence?.length
      ? structured.evidence
      : parsePiterSection(piter?.investigation || response.answer);
  const escalationLines = structured?.escalation_suggestion?.summary
    ? [structured.escalation_suggestion.summary]
    : parsePiterSection(piter?.escalation);
  const resolutionLines = parsePiterSection(piter?.resolution);
  const triageSteps = structured?.recommended_actions?.length
    ? structured.recommended_actions
    : response.recommended_steps?.length
      ? normalizeStepList(response.recommended_steps)
      : parsePiterSection(piter?.triage);
  const correlationChain = structured?.correlation_chain || [];
  const similarRows = structured?.similar_incidents?.length
    ? structured.similar_incidents
    : Array.isArray(response.similar_incidents)
      ? response.similar_incidents
      : [];

  const alertService = response.alert?.service ? String(response.alert.service) : null;
  const dep = (response.suspect_deployment || null) as Record<string, unknown> | null;
  const recentDeployment = dep
    ? [dep.version ? String(dep.version) : null, dep.deployed_at ? `(${String(dep.deployed_at)})` : null]
        .filter(Boolean)
        .join(" ") || null
    : null;
  const similarFirst =
    similarRows.length > 0
      ? String(
          (similarRows[0] as Record<string, unknown>).incident_id ||
            (similarRows[0] as Record<string, unknown>).id ||
            "",
        ) || null
      : null;
  const incidentId = response.alert?.incident_candidate_id
    ? String(response.alert.incident_candidate_id)
    : response.alert?.alert_id
      ? `INC-${String(response.alert.alert_id)}`
      : "INC-001";

  const updateStatus = (status: "in_process" | "resolved") => {
    setIncidentStatus(status);
    // Persist operator action server-side.
    void postIncidentStatus(incidentId, status).catch(() => {});
  };

  return (
    <div className="grid-stack piter-response" id="piter-analysis-panel">
      {response.fallback_used ? (
        <div className="fallback-banner" role="status">
          Offline knowledge base — live Bedrock unavailable ({response.mode || "local_fallback"})
        </div>
      ) : null}

      <div className="piter-response-header">
        <div>
          <h2 className="piter-analysis-title">P1 Incident Analysis</h2>
          {response.alert?.service ? (
            <p className="piter-analysis-subtitle">
              {String(response.alert.service)} · {String(response.alert.environment || "prod")} ·{" "}
              {String(response.alert.title || response.alert.alert_id || "")}
            </p>
          ) : null}
        </div>
        <div className="piter-response-badges">
          {piter?.priority ? <PriorityBadge priority={piter.priority as "P1"} /> : null}
          <ConfidenceIndicator level={response.confidence} />
          <SourceBadge mode={response.mode} fallbackUsed={response.fallback_used} />
        </div>
      </div>

      <SafetyGuardrail previewOnly={response.escalation_policy?.safe_preview_only === true} />

      <AgentEnrichmentPipeline response={response} />

      <Card variant="elevated">
        <CardContent>
          <FieldGrid
            fields={[
              { label: "Affected service", value: alertService },
              { label: "Recommended priority", value: structured?.severity || piter?.priority || response.priority },
              { label: "Recent deployment", value: recentDeployment },
              { label: "Similar past incident", value: similarFirst },
              { label: "Matched runbook", value: response.matched_runbook },
              { label: "Confidence", value: response.confidence },
            ]}
          />
          {structured?.summary ? (
            <p style={{ marginTop: 12, fontSize: "0.875rem", color: "var(--text-secondary)" }}>
              {stripMarkdown(structured.summary)}
            </p>
          ) : null}
        </CardContent>
      </Card>

      {correlationChain.length > 0 ? (
        <Card>
          <CardHeader title="Correlation chain" />
          <CardContent>
            <CorrelationChainTimeline chain={correlationChain} />
          </CardContent>
        </Card>
      ) : null}

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
          <FieldGrid
            fields={[
              { label: "Knowledge base runbook", value: response.matched_runbook || null },
              {
                label: "Alert evidence",
                value: response.alert
                  ? `${String(response.alert.service || "—")} · ${String(response.alert.environment || "—")}`
                  : null,
              },
            ]}
          />
          {renderDeployment(response.suspect_deployment)}
          {renderSimilarIncidents(similarRows)}
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
              {
                label: "Owner team",
                value: structured?.escalation_suggestion?.owner_team || response.owner?.owner_team,
              },
              {
                label: "Primary on-call",
                value: structured?.escalation_suggestion?.primary_oncall || response.owner?.primary_oncall,
              },
              {
                label: "Escalation path",
                value: structured?.escalation_suggestion?.escalation_path || response.owner?.escalation_path,
              },
              {
                label: "Requires escalation",
                value:
                  response.requires_escalation != null
                    ? response.requires_escalation
                      ? "Yes"
                      : "No"
                    : null,
              },
              {
                label: "Escalation policy",
                value: response.escalation_policy?.summary
                  ? String(response.escalation_policy.summary)
                  : response.escalation_policy?.notify
                    ? `Notify: ${(response.escalation_policy.notify as string[]).join(" → ")}`
                    : null,
              },
              {
                label: "Safe preview",
                value: response.escalation_policy?.safe_preview_only ? "Preview only — human approval required" : null,
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

      <div className="analysis-footer-actions">
        {incidentStatus === "in_process" ? <span className="pill pill-warning">In process</span> : null}
        {incidentStatus === "resolved" ? <span className="pill pill-success">Resolved</span> : null}
        {incidentStatus === "open" ? (
          <Button variant="secondary" onClick={() => updateStatus("in_process")}>
            Mark In Process
          </Button>
        ) : null}
        <Button variant="primary" onClick={() => setShowEscalation(true)}>
          Escalate On-Call
        </Button>
        <Button
          variant="secondary"
          onClick={() => onFollowUp?.("Summarize this incident")}
        >
          Summarize
        </Button>
        <Button
          variant="secondary"
          onClick={() =>
            openWith({
              message: "What should I check next for this P1 incident?",
              sessionId: response.memory?.session_id || response.session_id,
            })
          }
        >
          Open Incident Chat
        </Button>
        {incidentStatus !== "resolved" ? (
          <Button variant="secondary" onClick={() => updateStatus("resolved")}>
            Mark Resolved
          </Button>
        ) : null}
      </div>

      {showEscalation ? (
        <EscalationModal
          incidentId={incidentId}
          service={alertService || "service"}
          severity={piter?.priority || response.priority || "P1"}
          onClose={() => setShowEscalation(false)}
        />
      ) : null}
    </div>
  );
}
