import type { WorkflowAlert } from "@/types/rag";

export function alertImpactDollars(alert: WorkflowAlert): number {
  return Math.max(0, alert.baselineMin - alert.assistedMin) * alert.impactPerMin;
}

export function alertSavedMinutes(alert: WorkflowAlert): number {
  return Math.max(0, alert.baselineMin - alert.assistedMin);
}

export function sessionImpactTotals(
  alerts: WorkflowAlert[],
  countedIds: Set<string>,
): { dollars: number; minutes: number } {
  let dollars = 0;
  let minutes = 0;
  for (const a of alerts) {
    if (!countedIds.has(a.id)) continue;
    minutes += alertSavedMinutes(a);
    dollars += alertImpactDollars(a);
  }
  return { dollars, minutes };
}

export function rankSimilarAlerts(
  alerts: WorkflowAlert[],
  active: WorkflowAlert,
  limit = 2,
): WorkflowAlert[] {
  const activeService = active.service.split("/")[0]?.trim().toLowerCase() ?? "";
  const activeRunbook = (active.matchedRunbook ?? "").toLowerCase();

  return alerts
    .filter((a) => a.id !== active.id)
    .map((a) => {
      let score = 0;
      if (a.severity === active.severity) score += 2;
      const svc = a.service.split("/")[0]?.trim().toLowerCase() ?? "";
      if (activeService && svc && (svc.includes(activeService) || activeService.includes(svc))) {
        score += 1;
      }
      const rb = (a.matchedRunbook ?? "").toLowerCase();
      if (activeRunbook && rb && (rb.includes(activeRunbook) || activeRunbook.includes(rb))) {
        score += 1;
      }
      return { alert: a, score };
    })
    .filter((x) => x.score > 0)
    .sort((x, y) => y.score - x.score)
    .slice(0, limit)
    .map((x) => x.alert);
}

export function scrollToSection(id: string) {
  document.getElementById(id)?.scrollIntoView({ behavior: "smooth", block: "start" });
}

export function delay(ms: number) {
  return new Promise<void>((resolve) => setTimeout(resolve, ms));
}
