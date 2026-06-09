import { Shield } from "lucide-react";
import { Card, CardContent } from "@/components/ui/Card";

const BLOCKED = [
  "Execute production rollback without approval",
  "Trigger failover or traffic shift autonomously",
  "Restart production services without confirmation",
  "Send live escalation notifications without token",
];

export function SafetyGuardrail({ previewOnly }: { previewOnly?: boolean }) {
  return (
    <Card className="safety-guardrail" variant="elevated">
      <CardContent>
        <h3 className="safety-guardrail-title">
          <Shield size={16} />
          Safety guardrail
        </h3>
        <p style={{ margin: "0 0 8px", fontSize: "0.8125rem", color: "var(--text-secondary)" }}>
          The agent can recommend rollback, failover, restart, and escalation. It will{" "}
          <strong>not</strong> execute production-impacting actions without human approval.
        </p>
        <ul className="piter-bullet-list" style={{ margin: 0 }}>
          {BLOCKED.map((item) => (
            <li key={item}>{item}</li>
          ))}
        </ul>
        {previewOnly ? (
          <p className="mono" style={{ marginTop: 8, fontSize: "0.75rem", color: "var(--warning)" }}>
            Escalation dispatch is preview-only in this environment.
          </p>
        ) : null}
      </CardContent>
    </Card>
  );
}
