import { useState, type FormEvent } from "react";
import { askChat } from "../api";
import type { ChatResponse } from "../types/chat";
import { Alert } from "../components/ui/Alert";
import { Badge } from "../components/ui/Badge";
import { Button } from "../components/ui/Button";
import { Card } from "../components/ui/Card";
import { LoadingSpinner } from "../components/ui/LoadingSpinner";
import { SourceCard } from "../components/ui/SourceCard";
import { clampTopK } from "../utils/clampTopK";
import { confidenceBadgeClass } from "../utils/badgeStyles";

export function ChatPage() {
  const [question, setQuestion] = useState("");
  const [topK, setTopK] = useState(5);
  const [result, setResult] = useState<ChatResponse | null>(null);
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    if (!question.trim()) {
      setError("Please enter a question.");
      return;
    }
    setIsLoading(true);
    setError("");
    setResult(null);
    try {
      setResult(await askChat({ question, top_k: topK }));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to ask question.");
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <div className="page-stack">
      <header className="page-header-block">
        <h1 className="page-title">RAG assistant</h1>
        <p className="page-description">Ask operational questions grounded in the indexed incident knowledge base.</p>
      </header>

      <div className="two-col-chat">
        <Card eyebrow="Input" title="Question" padded>
          <form className="form-grid" onSubmit={handleSubmit}>
            <div>
              <label className="lbl" htmlFor="chat-q">
                Question
              </label>
              <textarea
                id="chat-q"
                className="textarea"
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                placeholder="What should I check when users cannot log in after deployment?"
              />
            </div>
            <div>
              <label className="lbl" htmlFor="chat-k">
                Top K results
              </label>
              <input
                id="chat-k"
                className="input"
                type="number"
                min={1}
                max={10}
                value={topK}
                onChange={(e) => setTopK(clampTopK(e.target.value))}
              />
            </div>
            <Button type="submit" variant="primary" loading={isLoading}>
              Send to model
            </Button>
          </form>
        </Card>

        <div>
          {isLoading ? <LoadingSpinner label="Retrieving context" /> : null}

          {error ? (
            <>
              <Alert variant="error" title="Assistant unavailable">{error}</Alert>
              {error.includes("FAISS index") ? <p className="hint-text">Open Knowledge Base and index documents first.</p> : null}
            </>
          ) : null}

          {result ? (
            <section className="card assistant-pane" aria-label="Assistant response">
              <div className="assistant-banner">
                <span>Grounded answer</span>
                <span style={{ display: "flex", flexWrap: "wrap", gap: 8, justifyContent: "flex-end" }}>
                  <Badge paletteClass={confidenceBadgeClass(result.confidence)}>Confidence · {result.confidence}</Badge>
                  <Badge variant={result.used_context ? "success" : "warning"}>
                    Context · {result.used_context ? "Grounded" : "No match"}
                  </Badge>
                </span>
              </div>
              <div className="card__body">
                <p style={{ marginTop: 0, whiteSpace: "pre-wrap", lineHeight: 1.6 }}>{result.answer}</p>

                {result.sources.length > 0 ? (
                  <div>
                    <p className="card__eyebrow" style={{ marginBottom: 8 }}>
                      Source files
                    </p>
                    <div className="meta-row-wrap">
                      {result.sources.map((s) => (
                        <span key={s} className="chip-muted">
                          {s}
                        </span>
                      ))}
                    </div>
                  </div>
                ) : null}

                <h3 className="card__title" style={{ marginTop: 20 }}>
                  Retrieved context
                </h3>
                {result.retrieved_chunks.length === 0 ? (
                  <p className="hint-text">No relevant chunks were retrieved.</p>
                ) : (
                  <div className="page-stack">
                    {result.retrieved_chunks.map((source) => (
                      <SourceCard key={source.chunk_id} source={source} />
                    ))}
                  </div>
                )}
              </div>
            </section>
          ) : null}
        </div>
      </div>
    </div>
  );
}
