import { useId, useState, type FormEvent } from "react";
import { uploadDocument } from "../api";
import type { UploadResponse } from "../types/document";
import { Alert } from "../components/ui/Alert";
import { Button } from "../components/ui/Button";
import { Card } from "../components/ui/Card";

const MAX_FILE_SIZE_MB = 10;
const MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024;

export function UploadPage() {
  const inputId = useId();
  const [file, setFile] = useState<File | null>(null);
  const [result, setResult] = useState<UploadResponse | null>(null);
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  async function handleUpload(event: FormEvent) {
    event.preventDefault();
    if (!file) {
      setError("Please choose a file first.");
      return;
    }
    if (file.size === 0) {
      setError("File is empty.");
      return;
    }
    if (file.size > MAX_FILE_SIZE_BYTES) {
      setError(`File is too large. Maximum size is ${MAX_FILE_SIZE_MB} MB.`);
      return;
    }
    setIsLoading(true);
    setError("");
    setResult(null);
    try {
      setResult(await uploadDocument(file));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Upload failed.");
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <div className="page-stack">
      <header className="page-header-block">
        <h1 className="page-title">Document upload</h1>
        <p className="page-description">
          Add artifacts to the upload corpus before indexing them alongside internal runbooks. Allowed types: MD · TXT · CSV · PDF · DOCX (max{" "}
          {MAX_FILE_SIZE_MB} MB).
        </p>
      </header>

      <Card eyebrow="Ingestion" title="Secure upload lane" padded>
        <form onSubmit={handleUpload}>
          <label htmlFor={inputId} className="upload-drop">
            <input
              id={inputId}
              className="upload-inline-input"
              type="file"
              accept=".md,.txt,.csv,.pdf,.docx"
              onChange={(e) => setFile(e.target.files?.[0] ?? null)}
            />
            <div>
              <strong>{file ? file.name : "Choose a file"}</strong>
              <p className="upload-drop__hint">
                Browse or tap to attach. Accepted: <strong>MD</strong>, <strong>TXT</strong>, <strong>CSV</strong>,{" "}
                <strong>PDF</strong>, <strong>DOCX</strong>.
              </p>
            </div>
          </label>

          <div className="inline-actions">
            <Button type="submit" variant="primary" loading={isLoading}>
              Upload to backend
            </Button>
          </div>
        </form>
      </Card>

      {result ? (
        <Alert variant="success" title="Upload received">
          <p style={{ margin: "0 0 8px" }}>
            Stored as <strong>{result.saved_as}</strong> ({result.size_bytes.toLocaleString()} bytes).
          </p>
          <p style={{ margin: 0 }} className="hint-text">
            Original filename: {result.filename} · Pipeline status: {result.status}
            {result.content_type ? <> · MIME: {result.content_type}</> : null}
          </p>
        </Alert>
      ) : null}

      {error ? (
        <Alert variant="error" title="Upload failed">
          {error}
        </Alert>
      ) : null}
    </div>
  );
}
