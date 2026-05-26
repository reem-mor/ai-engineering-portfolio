import { Badge } from "./Badge";
import type { BadgeVariant } from "./Badge";

export type MetricCardProps = {
  label: string;
  value: string | number;
  sub?: string;
  badgeLabel?: string;
  badgeVariant?: BadgeVariant;
};

export function MetricCard({ label, value, sub, badgeLabel, badgeVariant = "neutral" }: MetricCardProps) {
  return (
    <div className="metric-card">
      <div className="metric-card__top">
        <p className="metric-card__label">{label}</p>
        {badgeLabel ? <Badge variant={badgeVariant}>{badgeLabel}</Badge> : null}
      </div>
      <p className="metric-card__value">{value}</p>
      {sub ? <p className="metric-card__sub">{sub}</p> : null}
    </div>
  );
}
