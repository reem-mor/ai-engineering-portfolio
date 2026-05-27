import { useCallback, useEffect, useState } from "react";
import { indexSampleDocuments, indexUploadedDocuments, listSampleDocuments, listUploadedDocuments } from "../api";
import type { DocumentIndexResponse } from "../types/document";
import { Alert } from "../components/ui/Alert";
import { Badge } from "../components/ui/Badge";
import { Button } from "../components/ui/Button";
import { Card } from "../components/ui/Card";
import { LoadingSpinner } from "../components/ui/LoadingSpinner";
import { PipelineSteps } from "../components/ui/PipelineSteps";
import { SUPPORTED_FILE_TYPES } from "../content/opsCopy";
import { readRagIndexSession, writeRagIndexSession } from "../utils/ragIndexSession";
import { fileTypeLabel } from "../utils/fileTypeLabel";

function badgeVariantForFile(filename: string): "info" | "neutral" | "warning" {
  const t = fileTypeLabel(filename);
  if (t === "CSV") return "warning";
  if (t === "PDF" || t === "DOCX") return "neutral";
  return "info";
}

export function KnowledgeBasePage() {
  const [sampleFiles, setSampleFiles] = useState<string[]>([]);
  const [uploadedFiles, setUploadedFiles] = useState<string[]>([]);
  const [indexResult, setIndexResult] = useState<DocumentIndexResponse | null>(null);
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const sessionIndex = readRagIndexSession();

  const loadFiles = useCallback(async () => {
    setIsLoading(true);
    setError("");
    try {
      const [samples, uploaded] = await Promise.all([listSampleDocuments(), listUploadedDocuments()]);
      setSampleFiles(samples.files);
      setUploadedFiles(uploaded.files);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load documents.");
    } finally {
      setIsLoading(false);
    }
  }, []);

  async function runIndex(kind: "sample" | "uploaded") {
    setIsLoading(true);
    setError("");
    setIndexResult(null);
    try {
      const response = kind === "sample" ? await indexSampleDocuments() : await indexUploadedDocuments();
      setIndexResult(response);
      writeRagIndexSession({
        indexedAt: new Date().toISOString(),
        indexedFileCount: response.indexed_file_count,
        kind,
        message: response.message,
      });
      await loadFiles();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to index documents.");
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    void loadFiles();
  }, [loadFiles]);

  return (
    <div className="page-stack">
      <header className="page-header-block page-header-block--module">
        <p className="page-module-tag">Knowledge pipeline</p>
        <h1 className="page-title">Knowledge base</h1>
        <p className="page-description">
          Source of truth for IncidentIQ. Ingest runbooks, SOPs, and incident artifacts before RAG Chat or Incident
          Analysis can return grounded answers.
        </p>
      </header>

      <Alert variant="info" title="Index before chat">
        Complete indexing here first. Until FAISS is built, chat and incident routes return a FAISS-not-found error from
        the API.
      </Alert>

      <section className="kb-pipeline-panel">
        <Card eyebrow="Pipeline" title="How documents become searchable" padded classNameExtra="kb-pipeline-card">
          <PipelineSteps />
          <p className="hint-text">
            Indexed vectors are stored under <code className="inline-code">data/faiss_index/</code> on the backend host.
          </p>
        </Card>

        <Card eyebrow="Indexing" title="Build or refresh vectors" padded classNameExtra="kb-index-card">
          <div className="kb-index-panel">
            <div className="kb-index-panel__copy">
              <p className="hint-text meta-row-wrap--flush">
                Each run replaces the searchable index for the selected corpus. Re-index after adding new uploads on the
                Upload page.
              </p>
              <div className="meta-row-wrap meta-row-wrap--flush">
                {SUPPORTED_FILE_TYPES.map((t) => (
                  <Badge key={t} variant="info">
                    {t}
                  </Badge>
                ))}
              </div>
              {sessionIndex ? (
                <p className="hint-text kb-index-panel__session">
                  Last index in this browser session: <strong>{sessionIndex.indexedFileCount}</strong> files (
                  {sessionIndex.kind}) at {new Date(sessionIndex.indexedAt).toLocaleString()}.
                </p>
              ) : (
                <p className="hint-text kb-index-panel__session">No index recorded in this session yet.</p>
              )}
            </div>
            <div className="kb-index-panel__actions">
              <Button type="button" variant="primary" loading={isLoading} compact onClick={() => void runIndex("sample")}>
                Index sample documents
              </Button>
              <Button type="button" variant="secondary" loading={isLoading} compact onClick={() => void runIndex("uploaded")}>
                Index uploaded documents
              </Button>
            </div>
          </div>
        </Card>
      </section>

      {isLoading ? <LoadingSpinner label="Talking to ingestion pipeline" /> : null}

      {error ? (
        <>
          <Alert variant="error" title="Request failed">
            {error}
          </Alert>
          {error.includes("FAISS") ? (
            <p className="hint-text">Ensure the backend can access its data directories and rebuild the index here.</p>
          ) : null}
        </>
      ) : null}

      {indexResult && !error ? (
        <Alert variant="success" title="Indexing complete">
          {indexResult.message} FAISS now tracks <strong>{indexResult.indexed_file_count}</strong> files.
        </Alert>
      ) : null}

      <div className="kb-two-col">
        <Card eyebrow="Corpus" title="Sample documents" padded>
          {sampleFiles.length === 0 && !isLoading ? <p className="hint-text">No sample documents found.</p> : null}
          {sampleFiles.length > 0 ? <DocumentTable rows={sampleFiles} badgeVariant={badgeVariantForFile} /> : null}
        </Card>

        <Card eyebrow="Corpus" title="Uploaded documents" padded>
          {uploadedFiles.length === 0 && !isLoading ? (
            <p className="hint-text">No uploaded documents yet. Use Upload to add files, then index uploaded documents.</p>
          ) : null}
          {uploadedFiles.length > 0 ? <DocumentTable rows={uploadedFiles} badgeVariant={badgeVariantForFile} /> : null}
        </Card>
      </div>
    </div>
  );
}

function DocumentTable({
  rows,
  badgeVariant,
}: {
  rows: string[];
  badgeVariant: (filename: string) => "info" | "neutral" | "warning";
}) {
  return (
    <div className="table-wrap">
      <table className="file-table">
        <thead>
          <tr>
            <th>Type</th>
            <th>Filename</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((file) => (
            <tr key={file}>
              <td data-label="Type">
                <Badge variant={badgeVariant(file)}>{fileTypeLabel(file)}</Badge>
              </td>
              <td data-label="File" className="file-table__name">
                {file}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
