import type { IncidentAnalysisResponse } from "../../types/incident";
import { Alert } from "../ui/Alert";
import { Card } from "../ui/Card";
import { ContextTrustBanner } from "../ui/ContextTrustBanner";
import { PriorityBadge } from "../ui/PriorityBadge";
import { ReportSection, ResponseStatusBar } from "../ui/ResponseStatusBar";
import { SourceCard } from "../ui/SourceCard";
import { confidenceBadgeClass } from "../../utils/badgeStyles";
import { isLowConfidence } from "../../utils/ragDisplay";
import { Badge } from "../ui/Badge";

export type IncidentReportViewProps = {
  response: IncidentAnalysisResponse;
};

export function IncidentReportView({ response }: IncidentReportViewProps) {
  const lowConf = isLowConfidence(response.confidence);
  const grounded = response.used_context;

  return (
    <div className="report-section">
      <section className="incident-hero">
        <div className="incident-hero__badges">
          <PriorityBadge severity={response.severity} showSeverity />
          <Badge paletteClass={confidenceBadgeClass(response.confidence)}>Confidence · {response.confidence}</Badge>
          <Badge variant={grounded ? "success" : "warning"}>Context · {grounded ? "Grounded" : "No match"}</Badge>
        </div>
        <h2 className="incident-hero__title">Incident triage summary</h2>
        <p className="incident-hero__summary">{response.incident_summary}</p>
        <ContextTrustBanner usedContext={grounded} confidence={response.confidence} />
      </section>

      {!grounded ? (
        <Alert variant="warning" title="No runbook-backed context found">
          Sections marked <strong>Generic triage</strong> are heuristic prompts from the intake form—not retrieved runbook
          evidence. Index relevant SOPs before production decisions.
        </Alert>
      ) : null}

      <div className="report-grid">
        <ReportSection eyebrow="Diagnostics" title="Likely causes" generic={!grounded} grounded={grounded}>
          <ul className="list-checks">
            {response.likely_causes.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </ReportSection>

        <ReportSection eyebrow="Procedure" title="Recommended checks" generic={!grounded} grounded={grounded}>
          <ul className="list-checks">
            {response.recommended_checks.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </ReportSection>

        <ReportSection eyebrow="Gaps" title="Missing information">
          <ul className="list-checks">
            {response.missing_information.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </ReportSection>

        {response.sources.length > 0 ? (
          <Card eyebrow="References" title="Source filenames" padded classNameExtra="report-section-card--span">
            <div className="meta-row-wrap meta-row-wrap--flush">
              {response.sources.map((s) => (
                <span key={s} className="chip-muted chip-muted--file">
                  {s}
                </span>
              ))}
            </div>
          </Card>
        ) : null}
      </div>

      <ReportSection eyebrow="Action" title="Next best action" generic={!grounded} grounded={grounded} highlight>
        <p className="answer-body flush action-callout">{response.next_best_action}</p>
      </ReportSection>

      <ReportSection eyebrow="Routing" title="Escalation recommendation" generic={!grounded} grounded={grounded} highlight>
        <p className="answer-body flush">{response.escalation_recommendation}</p>
      </ReportSection>

      <ReportSection eyebrow="Evidence" title="Retrieved sources" grounded={grounded}>
        {response.retrieved_chunks.length === 0 ? (
          <p className="hint-text">No chunks met the similarity threshold—no runbook evidence attached.</p>
        ) : (
          <>
            {lowConf ? (
              <p className="hint-text source-low-hint">
                Weak similarity matches—treat excerpts as hints, not confirmed root cause.
              </p>
            ) : null}
            <div className="page-stack evidence-list">
              {response.retrieved_chunks.map((source, index) => (
                <SourceCard key={source.chunk_id} source={source} lowConfidence={lowConf} rank={index + 1} />
              ))}
            </div>
          </>
        )}
      </ReportSection>
    </div>
  );
}
