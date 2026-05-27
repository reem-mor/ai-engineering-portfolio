/** CSS class fragments applied with `badge` base (see index.css .conf-* / .severity-*). */

export function confidenceBadgeClass(confidence: string): string {
  const c = confidence.toLowerCase().trim();
  if (c === "high") return "conf-high";
  if (c === "medium") return "conf-medium";
  if (c === "low") return "conf-low";
  if (c === "none") return "conf-none";
  return "severity-unknown";
}

/** Maps incident severity strings to tinted badge classes */
export function severityBadgeClass(raw: string): string {
  const s = raw.toLowerCase().trim();
  if (s === "critical") return "severity-critical";
  if (s === "high") return "severity-high";
  if (s === "medium") return "severity-medium";
  if (s === "low") return "severity-low";
  return "severity-unknown";
}

/** P1–P4 operational priority badge classes */
export function priorityBadgeClass(priority: string): string {
  const p = priority.toUpperCase().trim();
  if (p === "P1") return "priority-p1";
  if (p === "P2") return "priority-p2";
  if (p === "P3") return "priority-p3";
  if (p === "P4") return "priority-p4";
  return "severity-unknown";
}
