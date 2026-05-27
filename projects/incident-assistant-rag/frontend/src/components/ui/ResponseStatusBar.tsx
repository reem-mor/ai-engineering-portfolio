import type { ReactNode } from "react";
import { confidenceBadgeClass } from "../../utils/badgeStyles";
import { Badge } from "./Badge";
import { Card } from "./Card";
import { PriorityBadge } from "./PriorityBadge";

export type ResponseStatusBarProps = {
  usedContext: boolean;
  confidence: string;
  severity?: string;
  answerLabel?: string;
};

export function ResponseStatusBar({ usedContext, confidence, severity, answerLabel }: ResponseStatusBarProps) {
  return (
    <div className="assistant-banner">
      <span className="assistant-banner__label">{answerLabel ?? (usedContext ? "Grounded answer" : "Knowledge base refusal")}</span>
      <span className="assistant-banner__badges">
        {severity ? <PriorityBadge severity={severity} showSeverity /> : null}
        <Badge paletteClass={confidenceBadgeClass(confidence)}>Confidence · {confidence}</Badge>
        <Badge variant={usedContext ? "success" : "warning"}>Context · {usedContext ? "Grounded" : "No match"}</Badge>
      </span>
    </div>
  );
}

export type ReportSectionProps = {
  eyebrow: string;
  title: string;
  children: ReactNode;
  generic?: boolean;
  grounded?: boolean;
  highlight?: boolean;
};

/** Incident report section with optional generic/runbook label. */
export function ReportSection({ eyebrow, title, children, generic, grounded, highlight }: ReportSectionProps) {
  const label =
    generic === true ? (
      <Badge variant="warning">Generic triage</Badge>
    ) : grounded === true ? (
      <Badge variant="success">From runbooks</Badge>
    ) : null;

  return (
    <Card
      eyebrow={eyebrow}
      title={title}
      padded
      classNameExtra={highlight ? "report-section-card--highlight" : undefined}
      actions={label ? <div className="assistant-banner__badges">{label}</div> : undefined}
    >
      {children}
    </Card>
  );
}
