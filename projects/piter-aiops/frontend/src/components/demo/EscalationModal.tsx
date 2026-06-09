import { useEffect, useState } from "react";
import { fetchEscalationPreview, postEscalationNotify } from "@/lib/api-contract";
import { useDemo } from "@/context/demo";
import { useToast } from "@/context/toast";
import { isLiveDispatchReady, notificationModeLabel } from "@/lib/notification-ui";
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
  const [confirmationToken, setConfirmationToken] = useState("");
  const notification = bootstrap?.notification;
  const liveReady = isLiveDispatchReady(notification);
  const modeLabel = notificationModeLabel(notification);

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
    const token = confirmationToken.trim();
    if (notification?.require_confirmation !== false && !token) {
      push("Enter the dispatch confirmation token configured on the server.", "error");
      return;
    }
    setPending(true);
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
    } catch (err) {
      const message = err instanceof Error ? err.message : "Dispatch failed";
      push(liveReady ? message : "Escalation recorded (preview/mock gate)", liveReady ? "error" : "success");
      if (!liveReady) {
        markEscalated(incidentId);
        onClose();
      }
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
        <div className={liveReady ? "live-banner" : "preview-banner"}>
          {liveReady
            ? "LIVE DISPATCH — notifications will be sent after confirmation"
            : `PREVIEW ONLY (${modeLabel}) — no notifications sent`}
        </div>
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
        {notification?.require_confirmation !== false ? (
          <div className="form-row" style={{ marginTop: "12px" }}>
            <label className="label" htmlFor="esc-confirm-token">
              Confirmation token
            </label>
            <input
              id="esc-confirm-token"
              className="input"
              type="password"
              autoComplete="off"
              placeholder="Server-configured dispatch token"
              value={confirmationToken}
              onChange={(e) => setConfirmationToken(e.target.value)}
            />
          </div>
        ) : null}
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
