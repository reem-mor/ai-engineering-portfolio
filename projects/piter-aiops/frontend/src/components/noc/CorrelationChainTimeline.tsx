import type { CorrelationChainStep } from "@/types/api";

const STEP_LABELS: Record<string, string> = {
  deployment: "Deployment",
  alert: "Alert",
  similar_incident: "Similar incident",
};

export function CorrelationChainTimeline({ chain }: { chain: CorrelationChainStep[] }) {
  if (!chain.length) return null;

  return (
    <ol className="correlation-chain" style={{ margin: 0, padding: 0, listStyle: "none" }}>
      {chain.map((item, index) => (
        <li
          key={`${item.step}-${item.label}-${index}`}
          className="correlation-chain-item"
          style={{
            display: "grid",
            gridTemplateColumns: "120px 1fr",
            gap: "12px",
            padding: "10px 0",
            borderBottom: index < chain.length - 1 ? "1px solid var(--border-subtle)" : undefined,
          }}
        >
          <div>
            <div className="piter-field-label">{STEP_LABELS[item.step] || item.step}</div>
            {item.timestamp ? (
              <div className="mono" style={{ fontSize: "0.75rem", color: "var(--text-muted)" }}>
                {item.timestamp}
              </div>
            ) : null}
          </div>
          <div>
            <div style={{ fontWeight: 600, fontSize: "0.875rem" }}>{item.label}</div>
            {item.detail ? (
              <div style={{ fontSize: "0.8125rem", color: "var(--text-secondary)", marginTop: 4 }}>
                {item.detail}
              </div>
            ) : null}
          </div>
        </li>
      ))}
    </ol>
  );
}
