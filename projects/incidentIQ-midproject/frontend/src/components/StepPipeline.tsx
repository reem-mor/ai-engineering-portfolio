import {
  ArrowRight,
  CheckCircle2,
  Clock,
  Loader2,
  Search,
  ShieldCheck,
  Sparkles,
} from "lucide-react";

export type PipelineStepDef = {
  key: string;
  label: string;
  icon: React.ComponentType<{ className?: string }>;
  color: string;
};

type StepPipelineProps = {
  stage: string;
  steps: PipelineStepDef[];
  /** First entry is idle; remaining keys match step keys, last is terminal (e.g. done). */
  order: readonly string[];
};

export function StepPipeline({ stage, steps, order }: StepPipelineProps) {
  const currentIdx = order.indexOf(stage);

  return (
    <div className="flex items-center gap-2 overflow-x-auto">
      {steps.map((s, i) => {
        const stepIdx = order.indexOf(s.key);
        const isTerminal = s.key === "done";
        const completed =
          stage !== "idle" &&
          (currentIdx > stepIdx || (stage === "done" && stepIdx <= currentIdx));
        const inProgress = stage === s.key && stage !== "done";
        const terminalDone = isTerminal && stage === "done";
        const Icon = s.icon;

        return (
          <div key={s.key} className="flex items-center gap-2">
            <div
              className="flex items-center gap-2 rounded-full border px-3 py-1.5 text-xs transition-all duration-300"
              style={{
                borderColor:
                  completed || terminalDone
                    ? `var(--${s.color})`
                    : "var(--border)",
                color:
                  completed || terminalDone
                    ? `var(--${s.color})`
                    : "var(--muted-foreground)",
                backgroundColor:
                  inProgress || terminalDone
                    ? `color-mix(in oklab, var(--${s.color}) 20%, transparent)`
                    : "transparent",
                boxShadow: terminalDone
                  ? `0 0 12px color-mix(in oklab, var(--${s.color}) 35%, transparent)`
                  : undefined,
              }}
            >
              {inProgress ? (
                <Loader2 className="size-3.5 animate-spin" />
              ) : terminalDone ? (
                <CheckCircle2 className="size-3.5" />
              ) : (
                <Icon className="size-3.5" />
              )}
              {s.label}
            </div>
            {i < steps.length - 1 && (
              <ArrowRight className="size-3.5 text-muted-foreground/60" />
            )}
          </div>
        );
      })}
    </div>
  );
}

export const WORKFLOW_PIPELINE_STEPS: PipelineStepDef[] = [
  { key: "triage", label: "Match KB", icon: Search, color: "rag" },
  { key: "suggest", label: "Suggest actions", icon: Sparkles, color: "interface" },
  { key: "decide", label: "Recommend", icon: ShieldCheck, color: "agent" },
  { key: "done", label: "Ready", icon: Clock, color: "resolution" },
];

export const WORKFLOW_PIPELINE_ORDER = [
  "idle",
  "triage",
  "suggest",
  "decide",
  "done",
] as const;
