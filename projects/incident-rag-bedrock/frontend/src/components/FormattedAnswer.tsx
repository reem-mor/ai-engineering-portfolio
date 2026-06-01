import { useState } from "react";
import { ChevronDown } from "lucide-react";
import type { AnswerSections, Citation } from "@/types/rag";

export function FormattedAnswer({
  answer,
  sections,
  grounded = true,
}: {
  answer: string;
  sections?: AnswerSections;
  grounded?: boolean;
}) {
  const s = sections ?? {
    summary: answer.split("\n\n")[0] ?? answer,
    steps: [],
    escalation: [],
    why: "",
  };

  // On a refusal / low-confidence answer, only show the message — no derived
  // steps, escalation, or "why" boilerplate.
  if (!grounded) {
    return (
      <div className="space-y-4 text-sm leading-relaxed">
        <div>
          <div className="text-xs uppercase tracking-wider text-muted-foreground">Answer</div>
          <p className="mt-2 text-foreground/95">{s.summary || answer}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-4 text-sm leading-relaxed">
      <div>
        <div className="text-xs uppercase tracking-wider text-muted-foreground">Answer</div>
        <p className="mt-2 text-foreground/95">{s.summary || answer}</p>
      </div>

      {(s.steps.length > 0 || answer) && (
        <div>
          <div className="text-xs uppercase tracking-wider text-muted-foreground">
            Recommended steps
          </div>
          {s.steps.length > 0 ? (
            <ol className="mt-2 list-decimal space-y-1.5 pl-5">
              {s.steps.map((step, i) => (
                <li key={i}>{step}</li>
              ))}
            </ol>
          ) : (
            <p className="mt-2 whitespace-pre-wrap text-foreground/90">{answer}</p>
          )}
        </div>
      )}

      {s.escalation.length > 0 && (
        <div>
          <div className="text-xs uppercase tracking-wider text-muted-foreground">Escalation</div>
          <ul className="mt-2 list-disc space-y-1 pl-5">
            {s.escalation.map((item, i) => (
              <li key={i}>{item}</li>
            ))}
          </ul>
        </div>
      )}

      {s.why && (
        <div>
          <div className="text-xs uppercase tracking-wider text-muted-foreground">
            Why this answer
          </div>
          <p className="mt-2 text-muted-foreground">{s.why}</p>
        </div>
      )}
    </div>
  );
}

function splitSnippetSteps(snippet: string): string[] {
  const text = (snippet || "").trim();
  if (!text) return [];

  const lines = text.split(/\r?\n/).map((l) => l.trim()).filter(Boolean);
  const fromLines: string[] = [];

  for (const line of lines) {
    const numberedParts = line.split(/(?<=\s)(?=\d+\.\s)/);
    if (numberedParts.length > 1) {
      for (const part of numberedParts) {
        const stripped = part.trim();
        const match = stripped.match(/^\d+[.)]\s+(.+)$/);
        fromLines.push(match ? match[1].trim() : stripped);
      }
      continue;
    }
    const bullet = line.match(/^[-*•]\s+(.+)$/);
    if (bullet) {
      fromLines.push(bullet[1].trim());
      continue;
    }
    const numbered = line.match(/^\d+[.)]\s+(.+)$/);
    if (numbered) {
      fromLines.push(numbered[1].trim());
      continue;
    }
    fromLines.push(line);
  }

  if (fromLines.length >= 2) return fromLines;

  const sentences = text
    .split(/(?<=[.!?])\s+/)
    .map((s) => s.trim())
    .filter((s) => s.length > 12);
  if (sentences.length >= 2) return sentences;

  return fromLines.length ? fromLines : [text];
}

export function CitationCard({ citation }: { citation: Citation }) {
  const [expanded, setExpanded] = useState(false);
  const chunk =
    citation.chunk_index != null ? ` · chunk ${citation.chunk_index}` : "";
  const score =
    citation.score != null ? (
      <span className="text-muted-foreground">Score: {citation.score.toFixed(2)}</span>
    ) : null;

  const fullSnippet = citation.snippet?.trim() ?? "";
  const preview = citation.preview ?? citation.snippet;
  const hasMore = fullSnippet.length > 0 && fullSnippet !== preview;
  const expandedSteps = splitSnippetSteps(fullSnippet);

  return (
    <div className="rounded-lg border border-border bg-card/60 p-3">
      <button
        type="button"
        className="flex w-full items-start justify-between gap-2 text-left"
        onClick={() => setExpanded((v) => !v)}
        aria-expanded={expanded}
        disabled={!hasMore && expandedSteps.length <= 1}
      >
        <div className="min-w-0 flex-1">
          <div className="text-xs font-medium">
            [{citation.index}] {citation.source_label}
            {chunk}
          </div>
          {score && <div className="mt-1 text-[11px]">{score}</div>}
        </div>
        {(hasMore || expandedSteps.length > 1) && (
          <ChevronDown
            className={`size-4 shrink-0 text-muted-foreground transition-transform ${
              expanded ? "rotate-180" : ""
            }`}
            aria-hidden
          />
        )}
      </button>

      {!expanded && (
        <p className="mt-2 text-xs text-muted-foreground leading-relaxed">{preview}</p>
      )}

      {expanded && expandedSteps.length > 0 && (
        <ol className="mt-2 list-decimal space-y-1.5 pl-5 text-xs text-muted-foreground leading-relaxed">
          {expandedSteps.map((step, i) => (
            <li key={i}>{step}</li>
          ))}
        </ol>
      )}

      {expanded && expandedSteps.length === 0 && (
        <p className="mt-2 whitespace-pre-wrap text-xs text-muted-foreground leading-relaxed">
          {fullSnippet || preview}
        </p>
      )}
    </div>
  );
}

export function CitationList({ citations, title = "Retrieved citations" }: { citations: Citation[]; title?: string }) {
  if (!citations.length) return null;
  return (
    <div>
      <div className="text-xs uppercase tracking-wider text-muted-foreground mb-2">{title}</div>
      <div className="grid gap-3 sm:grid-cols-2">
        {citations.map((c) => (
          <CitationCard key={c.index} citation={c} />
        ))}
      </div>
    </div>
  );
}
