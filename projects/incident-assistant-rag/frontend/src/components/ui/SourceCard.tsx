import { useMemo, useState } from "react";
import type { SearchResult } from "../../types/common";
import { Badge } from "./Badge";

const SNIPPET = 380;

export type SourceCardProps = {
  source: SearchResult;
  lowConfidence?: boolean;
  rank?: number;
};

export function SourceCard({ source, lowConfidence = false, rank }: SourceCardProps) {
  const [expanded, setExpanded] = useState(false);

  const long = source.text.length > SNIPPET;
  const excerpt = useMemo(
    () => (expanded ? source.text : `${source.text.slice(0, SNIPPET)}${long ? "…" : ""}`),
    [expanded, long, source.text],
  );
  const scorePct = Math.min(100, Math.max(0, Math.round(source.score * 100)));

  return (
    <article className={`source-card${lowConfidence ? " source-card--low" : ""}`}>
      <div className="source-card__top">
        <div className="source-card__meta">
          {rank !== undefined ? (
            <span className="source-card__rank" aria-label={`Evidence rank ${rank}`}>
              #{rank}
            </span>
          ) : null}
          <h3 className="source-card__file" title={source.source_file}>
            {source.source_file}
          </h3>
        </div>
        <div className="source-card__score-wrap">
          {lowConfidence ? <Badge variant="warning">Low match</Badge> : null}
          <Badge variant={lowConfidence ? "warning" : "info"}>Score {source.score.toFixed(3)}</Badge>
        </div>
      </div>
      <div className="source-card__meter" aria-hidden>
        <span className="source-card__meter-fill" style={{ width: `${scorePct}%` }} />
      </div>
      <div className="source-card__body">
        <p className={`source-card__text${expanded ? " source-card__text--expanded" : ""}`}>{excerpt}</p>
        {long ? (
          <button type="button" className="source-card__toggle" onClick={() => setExpanded((x) => !x)}>
            {expanded ? "Show less" : "Show full excerpt"}
          </button>
        ) : null}
      </div>
    </article>
  );
}
