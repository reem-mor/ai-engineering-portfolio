import { useState, type FormEvent } from "react";
import { analyzeIncident } from "../api";
import type { IncidentAnalysisResponse } from "../types/incident";
import { Alert } from "../components/ui/Alert";
import { Badge } from "../components/ui/Badge";
import { Button } from "../components/ui/Button";
import { Card } from "../components/ui/Card";
import { LoadingSpinner } from "../components/ui/LoadingSpinner";
import { SourceCard } from "../components/ui/SourceCard";
import { clampTopK } from "../utils/clampTopK";
import { confidenceBadgeClass, severityBadgeClass } from "../utils/badgeStyles";

export function IncidentAnalyzePage() {
  const [description, setDescription] = useState("");
  const [affectedService, setAffectedService] = useState("");
  const [environment, setEnvironment] = useState("production");
  const [topK, setTopK] = useState(5);
  const [result, setResult] = useState<IncidentAnalysisResponse | null>(null);
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    if (description.trim().length < 10) {
      setError("Please enter a useful incident description.");
      return;
    }
    setIsLoading(true);
    setError("");
    setResult(null);
    try {
      setResult(
        await analyzeIncident({
          description,
          affected_service: affectedService || undefined,
          environment: environment || undefined,
          top_k: topK,
        }),
      );
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to analyze incident.");
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <div className="page-stack">
      <header className="page-header-block">
        <h1 className="page-title">Incident analysis</h1>
        <p className="page-description">
          Generate a structured operational report with severity classification, evidence-seeking checks, and escalation guidance grounded
          in the knowledge base.
        </p>
      </header>

      <Card eyebrow="Intake" title="Incident parameters" padded>
        <form className="form-grid" onSubmit={handleSubmit}>
          <div>
            <label className="lbl" htmlFor="inc-desc">
              Incident description
            </label>
            <textarea
              id="inc-desc"
              className="textarea"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Many users cannot log in after the latest production deployment."
            />
          </div>
          <div>
            <label className="lbl" htmlFor="inc-svc">
              Affected service
            </label>
            <input
              id="inc-svc"
              className="input"
              value={affectedService}
              onChange={(e) => setAffectedService(e.target.value)}
              placeholder="auth-service"
            />
          </div>
          <div>
            <label className="lbl" htmlFor="inc-env">
              Environment
            </label>
            <input id="inc-env" className="input" value={environment} onChange={(e) => setEnvironment(e.target.value)} placeholder="production" />
          </div>
          <div>
            <label className="lbl" htmlFor="inc-k">
              Top K results
            </label>
            <input id="inc-k" className="input" type="number" min={1} max={10} value={topK} onChange={(e) => setTopK(clampTopK(e.target.value))} />
          </div>
          <Button type="submit" variant="primary" loading={isLoading}>
            Generate incident report
          </Button>
        </form>
      </Card>

      {isLoading ? <LoadingSpinner label="Correlating telemetry and runbooks" /> : null}

      {error ? <Alert variant="error" title="Analysis failed">{error}</Alert> : null}

      {result ? <IncidentReport response={result} /> : null}
    </div>
  );
}

function IncidentReport({ response }: { response: IncidentAnalysisResponse }) {
  return (
    <div className="report-section">
      <Card
        eyebrow="Executive readout"
        title="Incident summary"
        padded
        actions={
          <div style={{ display: "flex", flexWrap: "wrap", gap: 8, justifyContent: "flex-end" }}>
            <Badge paletteClass={severityBadgeClass(response.severity)}>Severity · {response.severity}</Badge>
            <Badge paletteClass={confidenceBadgeClass(response.confidence)}>Confidence · {response.confidence}</Badge>
            <Badge variant={response.used_context ? "success" : "warning"}>Context · {response.used_context ? "Grounded" : "No match"}</Badge>
          </div>
        }
      >
        <p style={{ marginTop: 0, whiteSpace: "pre-wrap", lineHeight: 1.65, fontSize: "1.02rem" }}>{response.incident_summary}</p>

        {response.sources.length > 0 ? (
          <div>
            <p className="card__eyebrow" style={{ marginBottom: 8 }}>
              Referenced filenames
            </p>
            <div className="meta-row-wrap">
              {response.sources.map((s) => (
                <span key={s} className="chip-muted">
                  {s}
                </span>
              ))}
            </div>
          </div>
        ) : null}
      </Card>

      <Card eyebrow="Diagnostics" title="Likely causes" padded>
        <ul className="list-checks">{response.likely_causes.map((item) => (
          <li key={item}>{item}</li>
        ))}</ul>
      </Card>

      <Card eyebrow="Procedure" title="Recommended checks" padded>
        <ul className="list-checks">{response.recommended_checks.map((item) => (
          <li key={item}>{item}</li>
        ))}</ul>
      </Card>

      <Card eyebrow="Gaps" title="Missing information" padded>
        <ul className="list-checks">{response.missing_information.map((item) => (
          <li key={item}>{item}</li>
        ))}</ul>
      </Card>

      <Card eyebrow="Action" title="Next best action" padded>
        <p style={{ margin: 0, whiteSpace: "pre-wrap", lineHeight: 1.6 }}>{response.next_best_action}</p>
      </Card>

      <Card eyebrow="Routing" title="Escalation recommendation" padded>
        <p style={{ margin: 0, whiteSpace: "pre-wrap", lineHeight: 1.6 }}>{response.escalation_recommendation}</p>
      </Card>

      <Card eyebrow="Evidence" title="Retrieved sources" padded>
        {response.retrieved_chunks.length === 0 ? (
          <p className="hint-text">No relevant sources were retrieved.</p>
        ) : (
          <div className="page-stack">
            {response.retrieved_chunks.map((source) => (
              <SourceCard key={source.chunk_id} source={source} />
            ))}
          </div>
        )}
      </Card>
    </div>
  );
}
