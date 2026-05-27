import { useState, type FormEvent } from "react";
import { analyzeIncident } from "../api";
import type { IncidentAnalysisResponse } from "../types/incident";
import { IncidentReportView } from "../components/incident/IncidentReportView";
import { Alert } from "../components/ui/Alert";
import { Button } from "../components/ui/Button";
import { Card } from "../components/ui/Card";
import { ExampleQuestionChips } from "../components/ui/ExampleQuestionChips";
import { LoadingSpinner } from "../components/ui/LoadingSpinner";
import { DEMO_INCIDENT_SCENARIOS } from "../content/opsCopy";
import { clampTopK } from "../utils/clampTopK";

export function IncidentAnalyzePage() {
  const [description, setDescription] = useState("");
  const [affectedService, setAffectedService] = useState("");
  const [environment, setEnvironment] = useState("production");
  const [topK, setTopK] = useState(5);
  const [result, setResult] = useState<IncidentAnalysisResponse | null>(null);
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  async function runAnalysis(desc: string) {
    if (desc.trim().length < 10) {
      setError("Please enter a useful incident description (at least 10 characters).");
      return;
    }
    setIsLoading(true);
    setError("");
    setResult(null);
    try {
      setResult(
        await analyzeIncident({
          description: desc,
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

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    await runAnalysis(description);
  }

  return (
    <div className="page-stack">
      <header className="page-header-block page-header-block--module">
        <p className="page-module-tag">Triage workspace</p>
        <h1 className="page-title">Incident analysis</h1>
        <p className="page-description">
          Structured triage report for on-call and NOC: severity with P1–P4 mapping, checks, escalation, and evidence.
          Runbook-backed sections are labeled; heuristic sections appear as generic triage when retrieval does not match.
        </p>
      </header>

      <div className="incident-workspace">
        <Card eyebrow="Intake" title="Incident parameters" padded classNameExtra="incident-intake-card">
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
            <ExampleQuestionChips
              label="Demo scenarios"
              questions={DEMO_INCIDENT_SCENARIOS}
              disabled={isLoading}
              onSelect={(text) => {
                setDescription(text);
                void runAnalysis(text);
              }}
            />
            <div className="form-grid form-grid--inline">
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
                <input
                  id="inc-env"
                  className="input"
                  value={environment}
                  onChange={(e) => setEnvironment(e.target.value)}
                  placeholder="production"
                />
              </div>
              <div>
                <label className="lbl" htmlFor="inc-k">
                  Top K results
                </label>
                <input
                  id="inc-k"
                  className="input"
                  type="number"
                  min={1}
                  max={10}
                  value={topK}
                  onChange={(e) => setTopK(clampTopK(e.target.value))}
                />
              </div>
            </div>
            <Button type="submit" variant="primary" loading={isLoading}>
              Generate incident report
            </Button>
          </form>
        </Card>

        <div className="incident-report-pane">
          {isLoading ? <LoadingSpinner label="Correlating runbooks and generating triage report" /> : null}

          {error ? (
            <Alert variant="error" title="Analysis failed">
              {error}
            </Alert>
          ) : null}

          {result ? <IncidentReportView response={result} /> : null}

          {!result && !isLoading && !error ? (
            <section className="empty-state empty-state--compact" aria-label="Awaiting incident intake">
              <h2 className="empty-state__title">No triage report yet</h2>
              <p className="empty-state__desc">
                Submit an incident description or pick a demo scenario. The report will show P1–P4 priority, confidence,
                and runbook evidence when retrieval succeeds.
              </p>
            </section>
          ) : null}
        </div>
      </div>
    </div>
  );
}
