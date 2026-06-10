import { Check, Circle, Loader2 } from "lucide-react";
import type { ChatResponse } from "@/types/api";

const PIPELINE_STAGES = [
  { key: "alert", label: "Alert context" },
  { key: "deploy", label: "Deployments" },
  { key: "kb", label: "Knowledge base" },
  { key: "similar", label: "Similar incidents" },
  { key: "owner", label: "Service ownership" },
  { key: "actions", label: "Action groups" },
  { key: "escalation", label: "Escalation policy" },
  { key: "piter", label: "PITER synthesis" },
] as const;

function stageComplete(response: ChatResponse, key: (typeof PIPELINE_STAGES)[number]["key"]): boolean {
  switch (key) {
    case "alert":
      return Boolean(response.alert || response.piter?.investigation);
    case "deploy":
      return Boolean(response.suspect_deployment);
    case "kb":
      return Boolean(response.matched_runbook || response.sources?.length);
    case "similar":
      return Array.isArray(response.similar_incidents) && response.similar_incidents.length > 0;
    case "owner":
      return Boolean(response.owner?.owner_team || response.owner?.primary_oncall);
    case "actions":
      return Boolean(response.tool_results?.length);
    case "escalation":
      return Boolean(response.escalation_policy || response.owner?.escalation_path);
    case "piter":
      return Boolean(response.piter?.priority && response.piter?.investigation);
    default:
      return false;
  }
}

export function AgentEnrichmentPipeline({
  response,
  analyzing,
  stepIndex = -1,
}: {
  response?: ChatResponse | null;
  analyzing?: boolean;
  stepIndex?: number;
}) {
  return (
    <section className="enrichment-pipeline" aria-label="Agent enrichment pipeline">
      <div className="enrichment-pipeline-header">
        <h3 className="enrichment-pipeline-title">Agent Enrichment Pipeline</h3>
        <span className="enrichment-pipeline-sub">
          {analyzing ? "Investigating…" : response ? "Enrichment complete" : "Awaiting analysis"}
        </span>
      </div>
      <div className="enrichment-pipeline-grid">
        {PIPELINE_STAGES.map((stage, i) => {
          const done = response ? stageComplete(response, stage.key) : false;
          const active = analyzing && stepIndex === i;
          const pending = analyzing && stepIndex < i && !done;
          return (
            <div
              key={stage.key}
              className={`enrichment-stage${done ? " done" : ""}${active ? " active" : ""}${pending ? " pending" : ""}`}
            >
              {done ? (
                <Check size={14} aria-hidden />
              ) : active ? (
                <Loader2 size={14} className="btn-spinner" aria-hidden />
              ) : (
                <Circle size={14} aria-hidden />
              )}
              <span>{stage.label}</span>
            </div>
          );
        })}
      </div>
    </section>
  );
}
