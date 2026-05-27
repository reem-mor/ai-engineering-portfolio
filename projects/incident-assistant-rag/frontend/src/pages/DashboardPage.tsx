import { useCallback, useEffect, useState } from "react";
import { getHealth, listSampleDocuments, listUploadedDocuments } from "../api";
import { OpsStatusStrip } from "../components/dashboard/OpsStatusStrip";
import { CapabilityCard } from "../components/ui/CapabilityCard";
import { Card } from "../components/ui/Card";
import { LoadingSpinner } from "../components/ui/LoadingSpinner";
import {
  PRODUCT_CAPABILITIES,
  PRODUCT_TAGLINE,
  WORKSPACE_MODULES,
} from "../content/opsCopy";
import { readRagIndexSession } from "../utils/ragIndexSession";

const WORKSPACE_NAV: Record<string, string> = {
  chat: "chat",
  incident: "incident",
  knowledge: "knowledge",
};

export type DashboardPageProps = {
  onNavigate: (id: string) => void;
};

export function DashboardPage({ onNavigate }: DashboardPageProps) {
  const [health, setHealth] = useState<string | null>(null);
  const [sampleCount, setSampleCount] = useState<number | null>(null);
  const [uploadedCount, setUploadedCount] = useState<number | null>(null);
  const [loadError, setLoadError] = useState("");
  const [isLoading, setIsLoading] = useState(true);

  const sessionIndex = readRagIndexSession();

  const refresh = useCallback(async () => {
    setIsLoading(true);
    setLoadError("");
    try {
      const [h, samples, uploaded] = await Promise.all([
        getHealth(),
        listSampleDocuments(),
        listUploadedDocuments(),
      ]);
      setHealth(h.status);
      setSampleCount(samples.files.length);
      setUploadedCount(uploaded.files.length);
    } catch (err) {
      setLoadError(err instanceof Error ? err.message : "Failed to load dashboard data.");
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    void refresh();
  }, [refresh]);

  return (
    <div className="page-stack page-stack--dashboard">
      <header className="command-hero command-hero--panel">
        <div className="command-hero__content">
          <p className="command-hero__kicker">Operations command center</p>
          <h1 className="page-title page-title--hero">IncidentIQ</h1>
          <p className="command-hero__lead">{PRODUCT_TAGLINE}</p>
          <p className="hint-text command-hero__note">
            Amdocs AI Engineer course project — local RAG over runbooks and incident docs. Answers are tied to your
            indexed knowledge base, not general chat.
          </p>
        </div>
        <div className="command-hero__actions">
          <button type="button" className="workspace-card__link workspace-card__link--cta" onClick={() => onNavigate("knowledge")}>
            Index knowledge base
          </button>
          <button type="button" className="workspace-card__link" onClick={() => onNavigate("chat")}>
            Open RAG Chat
          </button>
        </div>
      </header>

      {isLoading ? <LoadingSpinner label="Checking API and document lists" /> : null}
      {loadError ? (
        <p className="hint-text" role="alert">
          {loadError}
        </p>
      ) : null}

      <OpsStatusStrip
        health={health}
        sampleCount={sampleCount}
        uploadedCount={uploadedCount}
        sessionIndex={sessionIndex}
        isLoading={isLoading}
      />

      <section className="capability-grid" aria-label="Product capabilities">
        {PRODUCT_CAPABILITIES.map((item) => (
          <CapabilityCard key={item.tag} item={item} />
        ))}
      </section>

      <Card eyebrow="Workspace" title="Operational modules" padded classNameExtra="workspace-modules-card">
        <div className="workspace-grid">
          {WORKSPACE_MODULES.map((mod) => (
            <article key={mod.id} className="workspace-card">
              <h3 className="workspace-card__title">{mod.title}</h3>
              <p className="workspace-card__summary">{mod.summary}</p>
              {mod.id === "trust" ? (
                <p className="hint-text workspace-card__meta">
                  See <code className="inline-code">evaluation/evaluation_results.md</code> for scripted pass/fail metrics.
                </p>
              ) : (
                <button
                  type="button"
                  className="workspace-card__link"
                  onClick={() => onNavigate(WORKSPACE_NAV[mod.id] ?? "dashboard")}
                >
                  {mod.action}
                </button>
              )}
            </article>
          ))}
        </div>
      </Card>

      <Card eyebrow="Demo path" title="Suggested grading flow" padded>
        <ol className="list-checks demo-path-list">
          <li>Knowledge Base → index sample documents.</li>
          <li>RAG Chat → ask a runbook question; confirm sources and grounded badge.</li>
          <li>Ask an irrelevant question (e.g. restaurant in Tokyo) → Context · No match.</li>
          <li>Incident Analysis → run a demo scenario; review P1–P4 and generic vs runbook labels.</li>
        </ol>
      </Card>
    </div>
  );
}
