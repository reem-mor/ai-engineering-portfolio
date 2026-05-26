import { useCallback, useEffect, useState } from "react";
import { indexSampleDocuments, indexUploadedDocuments, listSampleDocuments, listUploadedDocuments } from "../api";
import type { DocumentIndexResponse } from "../types/document";
import { Alert } from "../components/ui/Alert";
import { Badge } from "../components/ui/Badge";
import { Button } from "../components/ui/Button";
import { Card } from "../components/ui/Card";
import { LoadingSpinner } from "../components/ui/LoadingSpinner";
import { writeRagIndexSession } from "../utils/ragIndexSession";
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
      <header className="page-header-block">
        <h1 className="page-title">Knowledge base</h1>
        <p className="page-description">
          Build the FAISS index before using RAG Chat or Incident Analysis. Indexing creates embeddings and stores searchable vectors
          for the incident corpus.
        </p>
      </header>

      <Card
        eyebrow="Indexing"
        title="Build or refresh vectors"
        padded
        actions={
          <>
            <Button type="button" variant="primary" loading={isLoading} compact onClick={() => void runIndex("sample")}>
              Index sample documents
            </Button>
            <Button type="button" variant="secondary" loading={isLoading} compact onClick={() => void runIndex("uploaded")}>
              Index uploaded documents
            </Button>
          </>
        }
      >
        <p className="hint-text" style={{ marginTop: 0 }}>
          Each run replaces the searchable index for the corresponding corpus snapshot.
        </p>
      </Card>

      {isLoading ? <LoadingSpinner label="Talking to ingestion pipeline" /> : null}

      {error ? (
        <>
          <Alert variant="error" title="Request failed">
            {error}
          </Alert>
          {error.includes("FAISS") ? <p className="hint-text">Ensure the backend can access its data directories and rebuild the index here.</p> : null}
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
          {sampleFiles.length > 0 ? (
            <DocumentTable rows={sampleFiles} badgeVariant={badgeVariantForFile} />
          ) : null}
        </Card>

        <Card eyebrow="Corpus" title="Uploaded documents" padded>
          {uploadedFiles.length === 0 && !isLoading ? <p className="hint-text">No uploaded documents found.</p> : null}
          {uploadedFiles.length > 0 ? (
            <DocumentTable rows={uploadedFiles} badgeVariant={badgeVariantForFile} />
          ) : null}
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
