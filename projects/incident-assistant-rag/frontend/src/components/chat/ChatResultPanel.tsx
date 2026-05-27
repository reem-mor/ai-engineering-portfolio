import type { ChatResponse } from "../../types/chat";
import { ContextTrustBanner } from "../ui/ContextTrustBanner";
import { ResponseStatusBar } from "../ui/ResponseStatusBar";
import { SourceCard } from "../ui/SourceCard";
import { isLowConfidence } from "../../utils/ragDisplay";

export type ChatResultPanelProps = {
  result: ChatResponse;
};

export function ChatResultPanel({ result }: ChatResultPanelProps) {
  const lowConf = isLowConfidence(result.confidence);

  return (
    <section className="card assistant-pane evidence-panel" aria-label="Assistant response">
      <ResponseStatusBar usedContext={result.used_context} confidence={result.confidence} />

      <div className="card__body">
        <ContextTrustBanner usedContext={result.used_context} confidence={result.confidence} />

        <div className="answer-block">
          <p className="card__eyebrow">Answer</p>
          <p className="answer-body flush">{result.answer}</p>
        </div>

        {result.sources.length > 0 ? (
          <div className="source-files-block">
            <p className="card__eyebrow source-section-label">Referenced files</p>
            <div className="meta-row-wrap">
              {result.sources.map((s) => (
                <span key={s} className="chip-muted chip-muted--file">
                  {s}
                </span>
              ))}
            </div>
          </div>
        ) : null}

        <div className="evidence-block">
          <h3 className="card__title source-section-title">Retrieved evidence</h3>
          {result.retrieved_chunks.length === 0 ? (
            <p className="hint-text">No chunks passed the similarity threshold—nothing is shown as proof.</p>
          ) : (
            <>
              {lowConf ? (
                <p className="hint-text source-low-hint">
                  Low-confidence matches only. These excerpts are not authoritative—validate before acting.
                </p>
              ) : null}
              <div className="page-stack evidence-list">
                {result.retrieved_chunks.map((source, index) => (
                  <SourceCard key={source.chunk_id} source={source} lowConfidence={lowConf} rank={index + 1} />
                ))}
              </div>
            </>
          )}
        </div>
      </div>
    </section>
  );
}
