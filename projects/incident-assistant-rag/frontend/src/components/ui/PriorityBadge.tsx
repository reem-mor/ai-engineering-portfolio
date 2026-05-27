import { Badge } from "./Badge";
import { priorityBadgeClass } from "../../utils/badgeStyles";
import { severityPriorityLabel } from "../../utils/ragDisplay";

export type PriorityBadgeProps = {
  severity: string;
  /** When true, appends severity text after the P-level (e.g. "P1 · critical"). */
  showSeverity?: boolean;
};

export function PriorityBadge({ severity, showSeverity = false }: PriorityBadgeProps) {
  const priority = severityPriorityLabel(severity);
  if (!priority) return null;

  return (
    <Badge paletteClass={priorityBadgeClass(priority)} classNameExtra="priority-badge">
      {priority}
      {showSeverity ? ` · ${severity}` : null}
    </Badge>
  );
}
