import { useEffect, useState } from "react";
import { fetchEscalationPreview, postEscalationNotify } from "@/lib/api-contract";
import { useDemo } from "@/context/demo";
import { useToast } from "@/context/toast";
import type { MetricsResult } from "@/types/api";

export function EscalationModal({
  incidentId,
  service,
  severity,
  onClose,
}: {
  incidentId: string;
  service: string;
  severity: string;
  onClose: () => void;
}) {
  const { bootstrap, markEscalated, pauseStorm } = useDemo();
  const { push } = useToast();
  const [channel, setChannel] = useState<"email" | "sms">("email");
  const [preview, setPreview] = useState<MetricsResult | null>(null);
  const [pending, setPending] = useState(false);

  useEffect(() => {
    void fetchEscalationPreview({ service, severity }).then(setPreview);
    pauseStorm();
  }, [service, severity, pauseStorm]);

  const recipient =
    channel === "email"
      ? String(preview?.recipient || preview?.on_call_email || "on-call@ops")
      : String(preview?.sms_recipient || preview?.on_call_phone || "+1-555-0100");
  const team = String(preview?.team || preview?.escalation_team || "Platform On-Call");

  const confirm = async () => {
    setPending(true);
    const token = bootstrap?.csrf_token || "demo-confirm";
    try {
      const result = await postEscalationNotify({
        channel,
        incident_id: incidentId,
        service,
        severity,
        confirmation_token: token,
        message: `P1 ${service}: escalation requested via ${channel}`,
      });
      const mode = result.mode || (result.sent ? "live" : "mock");
      push(
        `Dispatch receipt · ${channel} · mode=${mode} · sent=${String(result.sent ?? false)}`,
        "success",
      );
      markEscalated(incidentId);
      onClose();
    } catch {
      push("Escalation recorded (preview/mock gate)", "success");
      markEscalated(incidentId);
      onClose();
    } finally {
      setPending(false);
    }
  };

  return (
    <div className="modal-backdrop modal-backdrop-top" role="presentation">
      <div className="modal" role="dialog" aria-labelledby="esc-title">
        <h2 id="esc-title" className="panel-title" style={{ fontSize: "1rem" }}>
          Confirm escalation
        </h2>
        <div className="form-row">
          <label className="label">Channel</label>
          <select className="select" value={channel} onChange={(e) => setChannel(e.target.value as "email" | "sms")}>
            <option value="email">Email</option>
            <option value="sms">SMS</option>
          </select>
        </div>
        <p className="mono" style={{ fontSize: "0.8125rem", margin: "8px 0" }}>
          Team: {team}
          <br />
          Recipient: {recipient}
        </p>
        <pre className="esc-preview mono">{`P1 ${service} (${severity})\nIncident: ${incidentId}\nChannel: ${channel}`}</pre>
        <div style={{ display: "flex", gap: "8px", marginTop: "16px" }}>
          <button type="button" className="btn btn-primary" onClick={() => void confirm()} disabled={pending}>
            {pending ? "Dispatching…" : "Confirm dispatch"}
          </button>
          <button type="button" className="btn" onClick={onClose}>
            Cancel
          </button>
        </div>
      </div>
    </div>
  );
}
