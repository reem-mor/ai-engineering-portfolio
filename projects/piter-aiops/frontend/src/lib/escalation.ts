import type { AlertStreamSummary, TriageCard } from "@/types/rag";

export interface EscalationContext {
  incident_id: string;
  severity: string;
  service: string;
  environment?: string;
  incident_title: string;
  on_call_name?: string;
  owner_team?: string;
  slack_channel?: string;
  war_room_channel?: string;
  business_impact?: string;
  support_complaints?: string;
  top_error?: string;
  recent_deployment?: string;
  runbook_count?: number;
  runbook_name?: string;
  recommended_actions?: string[];
}

type InvestigationLike = {
  id: string;
  service: string;
  environment?: string;
  alert: string;
  impact: string;
  priority: string;
};

function formatDeploy(raw: Record<string, unknown> | undefined): string | undefined {
  if (!raw || !Object.keys(raw).length) return undefined;
  const version = raw.version ?? raw.change ?? raw.deploy_id;
  const when = raw.deployed_at ?? raw.timestamp;
  const by = raw.deployed_by;
  const parts: string[] = [];
  if (version) parts.push(String(version));
  if (when) parts.push(String(when));
  if (by) parts.push(`by ${String(by)}`);
  return parts.length ? parts.join(" · ") : undefined;
}

function inferTopError(service: string, title: string): string {
  const lower = `${service} ${title}`.toLowerCase();
  if (lower.includes("auth") || lower.includes("login") || lower.includes("jwt")) {
    return "jwt_validation_failed +280% vs 1h baseline";
  }
  if (lower.includes("100%") || lower.includes("unresponsive")) {
    return "HTTP 5xx / connection errors — 100% error rate on active market";
  }
  if (lower.includes("replication") || lower.includes("lag")) {
    return "replication_lag_seconds above threshold";
  }
  return "Dominant error signature in logs — see PITER console for correlated traces";
}

function inferSupportLine(
  impact: Record<string, unknown>,
  streamSummary?: AlertStreamSummary,
): string {
  const pct = impact.player_impact_pct;
  if (typeof pct === "number" && pct > 0) {
    return `Support queue elevated; ~${pct}% player impact vs baseline. CS and social channels monitoring.`;
  }
  if (streamSummary?.p1_count) {
    return "Customer support reports login/checkout complaints increasing; NOC validating ticket spike.";
  }
  return "Support ticket volume above baseline; monitor CSAT and status-page subscribers.";
}

export function buildEscalationContext(
  triageCard: TriageCard | null,
  selected: InvestigationLike,
  streamSummary?: AlertStreamSummary,
): EscalationContext {
  const owner = (triageCard?.owner ?? {}) as Record<string, unknown>;
  const impact = (triageCard?.impact ?? {}) as Record<string, unknown>;
  const alert = (triageCard?.alert ?? {}) as Record<string, unknown>;
  const deployRaw =
    (triageCard?.suspect_deployment as Record<string, unknown> | undefined) ??
    (triageCard?.suspect_deploys?.[0] as Record<string, unknown> | undefined);

  const service = String(alert.service ?? selected.service);
  const environment = String(alert.environment ?? selected.environment ?? "GIB-UKGC");
  const incidentTitle = String(
    alert.title ?? alert.symptom ?? selected.alert,
  );

  return {
    incident_id: String(alert.alert_id ?? selected.id),
    severity: String(triageCard?.priority ?? selected.priority),
    service,
    environment,
    incident_title: incidentTitle,
    on_call_name: String(owner.primary_on_call ?? "Primary on-call engineer"),
    owner_team: String(owner.owner_team ?? "Platform SRE"),
    slack_channel: String(owner.slack_channel ?? "#incidents"),
    war_room_channel: "#war-room",
    business_impact: String(
      impact.business_explanation ?? impact.business_impact ?? selected.impact,
    ),
    support_complaints: inferSupportLine(impact, streamSummary),
    top_error: inferTopError(service, incidentTitle),
    recent_deployment:
      formatDeploy(deployRaw) ??
      (service.includes("auth")
        ? "v2.4.1 deployed 27m ago (auth-api rollout)"
        : "Recent deploy correlated via piter-recent-deployments"),
    runbook_count: triageCard?.citations?.length ?? 5,
    runbook_name: triageCard?.matched_runbook ?? undefined,
    recommended_actions:
      triageCard?.recommended_steps?.length
        ? triageCard.recommended_steps
        : [
            "Acknowledge incident and join #war-room.",
            "Validate service health and rollback gates.",
            "Review top error signature and recent deployment.",
          ],
  };
}
