import { useCallback, useEffect, useState } from "react";
import { fetchBootstrap } from "@/lib/api-contract";
import type { BootstrapResponse } from "@/types/api";
import { DocumentUploadPanel } from "@/components/shell/DocumentUploadPanel";
import { PageHeader } from "@/components/ui/PageHeader";
import { LoadingSkeleton } from "@/components/noc/LoadingSkeleton";
import { ErrorState } from "@/components/noc/ErrorState";

export function KnowledgeBasePage() {
  const [bootstrap, setBootstrap] = useState<BootstrapResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  const load = useCallback(async () => {
    setError(null);
    try {
      setBootstrap(await fetchBootstrap());
    } catch {
      setError("Failed to load knowledge base configuration");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  if (loading) {
    return (
      <div className="grid-stack">
        <PageHeader title="Knowledge Base" subtitle="Runbooks and Bedrock retrieval sources" />
        <LoadingSkeleton lines={4} />
      </div>
    );
  }

  if (error) return <ErrorState message={error} onRetry={load} />;

  return (
    <div className="grid-stack">
      <PageHeader
        title="Knowledge Base"
        subtitle="Documents indexed for RAG — uploads go to S3 with optional Bedrock ingestion"
      />

      <section className="panel">
        <h2 className="panel-title">Configuration</h2>
        <dl className="config-dl">
          <dt>KB ID</dt>
          <dd className="mono">{bootstrap?.kb_id || "— (local fallback)"}</dd>
          <dt>S3 bucket</dt>
          <dd className="mono">{bootstrap?.s3_bucket || "—"}</dd>
          <dt>S3 prefix</dt>
          <dd className="mono">{bootstrap?.s3_prefix || "—"}</dd>
          <dt>RAG backend</dt>
          <dd className="mono">{(bootstrap as BootstrapResponse & { rag_backend?: string })?.rag_backend || "—"}</dd>
          <dt>Max upload</dt>
          <dd>{bootstrap?.max_upload_mb ?? 5} MB</dd>
        </dl>
      </section>

      <section className="panel">
        <h2 className="panel-title">Upload runbook</h2>
        <DocumentUploadPanel />
      </section>
    </div>
  );
}
