import { useState, type FormEvent } from "react";
import { askChat } from "../api";
import type { ChatResponse } from "../types/chat";
import { ChatResultPanel } from "../components/chat/ChatResultPanel";
import { Alert } from "../components/ui/Alert";
import { Button } from "../components/ui/Button";
import { Card } from "../components/ui/Card";
import { EmptyStatePanel } from "../components/ui/EmptyStatePanel";
import { GroupedExampleQuestions } from "../components/ui/GroupedExampleQuestions";
import { LoadingSpinner } from "../components/ui/LoadingSpinner";
import { CHAT_QUESTION_GROUPS } from "../content/opsCopy";
import { clampTopK } from "../utils/clampTopK";

const EMPTY_STEPS = [
  "Index sample or uploaded documents on the Knowledge Base page.",
  "Ask operational questions about triage, escalation, ownership, or runbooks.",
  "Answers use only retrieved context—weak matches show as No match with guidance to re-index.",
] as const;

export function ChatPage() {
  const [question, setQuestion] = useState("");
  const [topK, setTopK] = useState(5);
  const [result, setResult] = useState<ChatResponse | null>(null);
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  async function submitQuestion(q: string) {
    if (!q.trim()) {
      setError("Please enter a question.");
      return;
    }
    setIsLoading(true);
    setError("");
    setResult(null);
    try {
      setResult(await askChat({ question: q, top_k: topK }));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to send question.");
    } finally {
      setIsLoading(false);
    }
  }

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    await submitQuestion(question);
  }

  const showEmpty = !result && !isLoading && !error;

  return (
    <div className="page-stack">
      <header className="page-header-block page-header-block--module">
        <p className="page-module-tag">RAG workspace</p>
        <h1 className="page-title">RAG Chat</h1>
        <p className="page-description">
          Grounded operational Q&A for NOC and DevOps: triage, escalation paths, runbooks, and service ownership. Answers
          cite indexed evidence—or refuse when nothing reliable matches.
        </p>
      </header>

      <div className="two-col-chat">
        <div className="chat-query-pane">
          <Card eyebrow="Query" title="Ask the knowledge base" padded>
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
              <GroupedExampleQuestions
                groups={CHAT_QUESTION_GROUPS}
                disabled={isLoading}
                onSelect={(text) => {
                  setQuestion(text);
                  void submitQuestion(text);
                }}
              />
              <Button type="submit" variant="primary" loading={isLoading}>
                Ask with RAG
              </Button>
            </form>
          </Card>
        </div>

        <div className="chat-results-pane">
          {showEmpty ? (
            <EmptyStatePanel
              title="Start with an indexed knowledge base"
              description="IncidentIQ does not answer from general knowledge. Build the FAISS index first, then ask operational questions grounded in your runbooks and SOPs."
              steps={EMPTY_STEPS}
            />
          ) : null}

          {isLoading ? <LoadingSpinner label="Retrieving context and generating answer" /> : null}

          {error ? (
            <Alert variant="error" title="Request failed">
              {error}
            </Alert>
          ) : null}

          {result ? <ChatResultPanel result={result} /> : null}
        </div>
      </div>
    </div>
  );
}
