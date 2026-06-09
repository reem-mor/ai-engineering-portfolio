import type { ReactNode } from "react";
import { Badge } from "./Badge";
import { cn } from "@/lib/utils";

export function MetricCard({
  label,
  value,
  mono,
  demo,
  hint,
  className,
}: {
  label: string;
  value: string | number;
  mono?: boolean;
  demo?: boolean;
  hint?: ReactNode;
  className?: string;
}) {
  return (
    <div className={cn("panel kpi-card", demo && "kpi-demo", className)}>
      <div className="kpi-label">
        {label}
        {demo ? <Badge variant="demo">DEMO ESTIMATE</Badge> : null}
      </div>
      <div className={mono ? "mono kpi-value" : "kpi-value"}>{value}</div>
      {hint ? <div className="kpi-hint">{hint}</div> : null}
    </div>
  );
}
