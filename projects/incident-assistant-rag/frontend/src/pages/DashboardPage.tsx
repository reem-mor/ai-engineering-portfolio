import { useCallback, useEffect, useState } from "react";
import { getHealth, listSampleDocuments, listUploadedDocuments } from "../api";
import type { HealthResponse } from "../types/health";
import { MetricCard } from "../components/ui/MetricCard";
import { Card } from "../components/ui/Card";
import { Button } from "../components/ui/Button";
import { LoadingSpinner } from "../components/ui/LoadingSpinner";
import { Alert } from "../components/ui/Alert";
import { readRagIndexSession } from "../utils/ragIndexSession";

export type DashboardPageProps = {
  onNavigate: (pageId: string) => void;
};

export function DashboardPage({ onNavigate }: DashboardPageProps) {
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [sampleCount, setSampleCount] = useState<number | null>(null);
  const [uploadedCount, setUploadedCount] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const load = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const [h, s, u] = await Promise.all([getHealth(), listSampleDocuments(), listUploadedDocuments()]);
      setHealth(h);
      setSampleCount(s.file_count);
      setUploadedCount(u.file_count);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to load dashboard data.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  const ragMeta = readRagIndexSession();

  return (
    <div className="page-stack">
      <header className="page-header-block">
        <h1 className="page-title">Operations overview</h1>
        <p className="page-description">
          Incident intelligence status for the connected backend. RAG index reflects the last successful indexing run in{" "}
          <strong>this browser session</strong>—rebuild from Knowledge Base if you rotate the environment or clear session data.
        </p>
      </header>

      {error ? (
        <Alert variant="error" title="Dashboard data partial or unavailable">
          {error}
        </Alert>
      ) : null}

      {loading ? <LoadingSpinner label="Loading telemetry" /> : null}

      {!loading ? (
        <>
          <section className="dash-metrics" aria-label="Key metrics">
            <MetricCard
              label="Backend status"
              value={health?.status === "ok" ? "OK" : health?.status ?? "—"}
              sub={health ? `${health.service} · v${health.version} · ${health.environment}` : undefined}
              badgeLabel={health?.status === "ok" ? "Live" : health ? "Check" : undefined}
              badgeVariant={health?.status === "ok" ? "success" : "warning"}
            />
            <MetricCard
              label="Sample documents"
              value={sampleCount ?? "—"}
              sub="Files on disk in the sample corpus"
            />
            <MetricCard
              label="Uploaded documents"
              value={uploadedCount ?? "—"}
              sub="User-uploaded corpus"
            />
            <MetricCard
              label="RAG index (session)"
              value={ragMeta ? `${ragMeta.indexedFileCount}` : "—"}
              sub={
                ragMeta
                  ? `Last build: ${new Date(ragMeta.indexedAt).toLocaleString()} (${ragMeta.kind})`
                  : "Not indexed in this session"
              }
              badgeLabel={ragMeta ? "Indexed" : "Idle"}
              badgeVariant={ragMeta ? "success" : "warning"}
            />
          </section>

          <Card eyebrow="Workflow" title="Quick actions" padded>
            <p className="hint-text" style={{ marginTop: 0 }}>
              Jump to common runbook steps without changing API routes.
            </p>
            <div className="dash-quick__actions">
              <Button variant="primary" onClick={() => onNavigate("knowledge")}>
                Open knowledge base
              </Button>
              <Button variant="secondary" onClick={() => onNavigate("chat")}>
                RAG assistant
              </Button>
              <Button variant="secondary" onClick={() => onNavigate("incident")}>
                Incident analysis
              </Button>
              <Button variant="secondary" onClick={() => onNavigate("upload")}>
                Upload document
              </Button>
            </div>
          </Card>

          {health ? (
            <Card eyebrow="Connectivity" title="Database capability" padded>
              <p style={{ marginTop: 0 }} className="hint-text">
                Optional persistence for chat history when enabled in the backend profile.
              </p>
              <p style={{ marginBottom: 0, fontFamily: "var(--font-mono)", fontSize: "0.9375rem", fontWeight: 600 }}>
                history DB: {health.database_enabled ? "enabled" : "disabled"}
              </p>
            </Card>
          ) : null}
        </>
      ) : null}
    </div>
  );
}
