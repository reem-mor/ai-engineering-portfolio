import {
  AlertTriangle,
  ArrowUpRight,
  Clock,
  GitBranch,
  Users,
} from "lucide-react";
import type {
  ExternalStatus,
  OwnerContext,
  SimilarIncident,
  TriageEnrichment,
} from "@/types/rag";

function normalizeOwner(
  enrichment: TriageEnrichment | null | undefined,
  ownerTeam: string | OwnerContext | null | undefined,
): OwnerContext | null {
  if (ownerTeam && typeof ownerTeam === "object") {
    return ownerTeam;
  }
  if (typeof ownerTeam === "string" && ownerTeam.trim()) {
    return { owner_team: ownerTeam };
  }
  const raw = enrichment?.owner_team;
  if (raw && typeof raw === "object") return raw as OwnerContext;
  if (typeof raw === "string" && raw.trim()) return { owner_team: raw };
  if (enrichment?.escalation_path || enrichment?.pagerduty_service) {
    return {
      owner_team: typeof enrichment.owner_team === "string" ? enrichment.owner_team : undefined,
      escalation_path: enrichment.escalation_path,
      pagerduty_service: enrichment.pagerduty_service,
    };
  }
  const tools = enrichment?.tools;
  if (Array.isArray(tools)) {
    for (const t of tools) {
      if (t && typeof t === "object" && ("owner_team" in t || "escalation_path" in t)) {
        return t as OwnerContext;
      }
    }
  }
  return null;
}

function similarList(
  enrichment: TriageEnrichment | null | undefined,
  topLevel: SimilarIncident[] | null | undefined,
): SimilarIncident[] {
  const fromEnrichment = enrichment?.similar_incidents;
  if (Array.isArray(fromEnrichment) && fromEnrichment.length > 0) {
    return fromEnrichment.slice(0, 3);
  }
  if (Array.isArray(topLevel) && topLevel.length > 0) {
    return topLevel.slice(0, 3);
  }
  return [];
}

export function EnrichmentPanel({
  enrichment,
  ownerTeam,
  similarIncidents,
  externalStatus,
}: {
  enrichment?: TriageEnrichment | null;
  ownerTeam?: string | OwnerContext | null;
  similarIncidents?: SimilarIncident[] | null;
  externalStatus?: ExternalStatus | null;
}) {
  const owner = normalizeOwner(enrichment, ownerTeam);
  const deploys = enrichment?.deployments ?? [];
  const likely = enrichment?.likely_deploy_correlation ?? deploys.length > 0;
  const similar = similarList(enrichment, similarIncidents);
  const revenuePerHour = enrichment?.revenue_impact_usd_per_hour;
  const escalationMin = enrichment?.escalation_minutes;
  const regulatory = enrichment?.regulatory_flag;

  const hasDeploy = likely && deploys.length > 0;
  const hasOwner = Boolean(
    owner?.owner_team || owner?.escalation_path || owner?.pagerduty_service,
  );
  const hasImpact = revenuePerHour != null && revenuePerHour > 0;
  const hasSimilar = similar.length > 0;
  const hasExternal = Boolean(
    externalStatus?.provider || externalStatus?.status || externalStatus?.summary,
  );

  if (!hasDeploy && !hasOwner && !hasImpact && !hasSimilar && !hasExternal) {
    return null;
  }

  return (
    <div className="mt-4 space-y-3" data-enrichment-panel>
      {hasDeploy && (
        <div
          className="rounded-lg border px-3 py-2.5 text-sm"
          style={{
            borderColor: "color-mix(in oklab, var(--ingest) 45%, transparent)",
            backgroundColor: "color-mix(in oklab, var(--ingest) 10%, transparent)",
          }}
        >
          <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-[var(--ingest)]">
            <GitBranch className="size-3.5" />
            Likely cause — recent deploy
          </div>
          {enrichment?.dependency_hop && (
            <p className="mt-1 text-[11px] text-muted-foreground">
              Dependency hop: upstream{" "}
              {(enrichment.dependency_hop.depends_on ?? []).join(", ") || "—"} · downstream{" "}
              {(enrichment.dependency_hop.depended_by ?? []).join(", ") || "—"}
            </p>
          )}
          <ul className="mt-2 space-y-2">
            {deploys.slice(0, 3).map((d, i) => (
              <li
                key={`${d.service}-${d.deployed_at}-${i}`}
                className="rounded border border-border bg-card/50 px-2.5 py-2"
              >
                <div className="font-medium">
                  {d.service}
                  {d.hop ? (
                    <span className="ml-1.5 text-[10px] uppercase text-muted-foreground">
                      ({d.hop})
                    </span>
                  ) : null}
                </div>
                <div className="mt-0.5 text-xs text-muted-foreground">
                  {d.change ?? "deploy"} · {d.deployed_by ?? "unknown"} · {d.deployed_at ?? "—"}
                </div>
              </li>
            ))}
          </ul>
        </div>
      )}

      {hasOwner && owner && (
        <div className="rounded-lg border border-border bg-card/50 px-3 py-2.5 text-sm">
          <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-muted-foreground">
            <Users className="size-3.5 text-[var(--interface)]" />
            Owner & escalation
          </div>
          {owner.owner_team && (
            <div className="mt-2">
              <span className="text-muted-foreground">Team: </span>
              <span className="font-medium">{owner.owner_team}</span>
            </div>
          )}
          {owner.pagerduty_service && (
            <div className="mt-1 text-xs">
              <span className="text-muted-foreground">PagerDuty: </span>
              <span className="font-mono">{owner.pagerduty_service}</span>
            </div>
          )}
          {owner.escalation_path && (
            <div className="mt-2 flex items-start gap-1.5 text-xs">
              <ArrowUpRight className="mt-0.5 size-3 shrink-0 text-[var(--interface)]" />
              <span>
                <span className="text-muted-foreground">Escalation: </span>
                {owner.escalation_path}
              </span>
            </div>
          )}
          {owner.warning && (
            <p className="mt-2 text-xs text-[var(--ingest)]">{owner.warning}</p>
          )}
        </div>
      )}

      {hasImpact && (
        <div
          className="rounded-lg border px-3 py-2.5 text-sm"
          style={{
            borderColor: "color-mix(in oklab, var(--ingest) 40%, transparent)",
            backgroundColor: "color-mix(in oklab, var(--ingest) 8%, transparent)",
          }}
        >
          <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-[var(--ingest)]">
            <AlertTriangle className="size-3.5" />
            Business impact
          </div>
          <p className="mt-2 font-semibold text-[var(--ingest)]">
            ~${revenuePerHour!.toLocaleString()} / hour
            {escalationMin != null ? (
              <span className="ml-2 font-normal text-muted-foreground">
                · escalate within {escalationMin} min
              </span>
            ) : null}
          </p>
          {enrichment?.player_impact_pct != null && (
            <p className="mt-1 text-xs text-muted-foreground">
              Player impact: {enrichment.player_impact_pct}%
            </p>
          )}
          {regulatory && (
            <p className="mt-1 text-xs text-[var(--ingest)]">
              Regulatory reporting may apply for this tier.
            </p>
          )}
        </div>
      )}

      {hasSimilar && (
        <div>
          <div className="text-xs uppercase tracking-wider text-muted-foreground">
            Similar past incidents
          </div>
          <ul className="mt-2 space-y-2">
            {similar.map((inc) => (
              <li
                key={inc.incident_id ?? inc.date}
                className="rounded-lg border border-border bg-card/60 px-3 py-2 text-sm"
              >
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <span className="font-mono text-xs font-medium">
                    {inc.incident_id ?? "INC-?"}
                  </span>
                  {inc.mttr_minutes != null && (
                    <span
                      className="inline-flex items-center gap-1 rounded px-1.5 py-0.5 text-[10px] font-semibold"
                      style={{
                        backgroundColor:
                          "color-mix(in oklab, var(--tools) 18%, transparent)",
                        color: "var(--tools)",
                      }}
                    >
                      <Clock className="size-3" />
                      MTTR {inc.mttr_minutes}m
                    </span>
                  )}
                </div>
                {inc.root_cause && (
                  <p className="mt-1 text-xs text-muted-foreground leading-relaxed">
                    {inc.root_cause}
                  </p>
                )}
                {(inc.resolution || inc.customer_impact) && (
                  <p className="mt-1 text-[11px] text-foreground/80">
                    {inc.resolution ?? inc.customer_impact}
                  </p>
                )}
              </li>
            ))}
          </ul>
        </div>
      )}

      {hasExternal && externalStatus && (
        <div
          className="rounded-lg border border-border px-3 py-2 text-xs"
          data-external-status
        >
          <span className="font-semibold">
            {externalStatus.status === "ok" || externalStatus.status === "operational"
              ? "No related provider outage"
              : "Possible upstream outage"}
          </span>
          {externalStatus.provider && (
            <span className="text-muted-foreground"> · {externalStatus.provider}</span>
          )}
          {externalStatus.summary && (
            <p className="mt-1 text-muted-foreground">{externalStatus.summary}</p>
          )}
          {externalStatus.url && (
            <a
              href={externalStatus.url}
              target="_blank"
              rel="noopener noreferrer"
              className="mt-1 inline-block text-[var(--interface)] hover:underline"
            >
              Status page
            </a>
          )}
        </div>
      )}
    </div>
  );
}
