export function classNames(...items: Array<string | false | null | undefined>) {
  return items.filter(Boolean).join(" ");
}

export function toneClasses(tone: string) {
  const map: Record<string, string> = {
    red: "border-red-500/30 bg-red-500/10 text-red-200",
    amber: "border-amber-400/30 bg-amber-400/10 text-amber-100",
    green: "border-emerald-400/30 bg-emerald-400/10 text-emerald-100",
    teal: "border-teal-400/30 bg-teal-400/10 text-teal-100",
    cyan: "border-cyan-400/30 bg-cyan-400/10 text-cyan-100",
    blue: "border-blue-400/30 bg-blue-400/10 text-blue-100",
    purple: "border-violet-400/30 bg-violet-400/10 text-violet-100",
    slate: "border-slate-500/30 bg-slate-500/10 text-slate-200",
  };
  return map[tone] ?? map.cyan;
}

export function priorityClasses(priority: string) {
  if (priority === "P1") return "border-red-500/40 bg-red-500/15 text-red-100";
  if (priority === "P2") return "border-amber-400/40 bg-amber-400/15 text-amber-100";
  if (priority === "P3") return "border-blue-400/40 bg-blue-400/15 text-blue-100";
  return "border-slate-500/40 bg-slate-500/15 text-slate-100";
}

export function conclusionTone(conclusion: string): string {
  const map: Record<string, string> = {
    Critical: "red",
    Malicious: "red",
    Suspicious: "amber",
    Inconclusive: "blue",
    Benign: "green",
    Noise: "slate",
  };
  return map[conclusion] ?? "cyan";
}

export function statusTone(status: string): string {
  if (status === "Escalated") return "red";
  if (status === "Noise Grouped" || status === "Resolved" || status === "False Positive")
    return "green";
  if (status === "Investigating" || status === "In Process") return "cyan";
  return "amber";
}

export function stormPhaseLabel(state: string): string {
  const map: Record<string, string> = {
    idle: "Ready",
    streaming: "Streaming alerts",
    paused: "Paused",
    critical: "P1 detected — auto-paused",
    investigating: "Running PITER triage",
    resolved: "Demo complete",
  };
  return map[state] ?? state;
}
