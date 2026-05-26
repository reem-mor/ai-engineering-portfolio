import { useMemo, useState } from "react";
import type { SearchResult } from "../../types/common";
import { Badge } from "./Badge";

const SNIPPET = 380;

export type SourceCardProps = { source: SearchResult };

export function SourceCard({ source }: SourceCardProps) {
  const [expanded, setExpanded] = useState(false);

  const long = source.text.length > SNIPPET;
  const excerpt = useMemo(() => (expanded ? source.text : `${source.text.slice(0, SNIPPET)}${long ? "…" : ""}`), [expanded, long, source.text]);

  return (
    <article className="source-card">
      <div className="source-card__top">
        <h3 className="source-card__file" title={source.source_file}>
          {source.source_file}
        </h3>
        <div className="source-card__score-wrap">
          <Badge variant="info">Score {source.score.toFixed(3)}</Badge>
        </div>
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
