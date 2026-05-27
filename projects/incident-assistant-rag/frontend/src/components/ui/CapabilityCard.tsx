import type { CapabilityItem } from "../../content/opsCopy";
import { Badge } from "./Badge";

export type CapabilityCardProps = {
  item: CapabilityItem;
};

export function CapabilityCard({ item }: CapabilityCardProps) {
  return (
    <article className="capability-card">
      <Badge variant="info">{item.tag}</Badge>
      <h3 className="capability-card__title">{item.title}</h3>
      <p className="capability-card__desc">{item.description}</p>
    </article>
  );
}
