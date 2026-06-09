import { useState } from "react";
import { AlertBanner } from "@/components/ui/AlertBanner";
import { Button } from "@/components/ui/Button";
import { useDemo } from "@/context/demo";
import { useChatDock } from "@/context/chat-dock";
import { useSession } from "@/context/session";
import { useNavigate } from "@/context/navigation";
import { alertToTriagePayload } from "@/lib/storm-engine";
import { postTriage } from "@/lib/api-contract";
import { formatCurrencyUsd, formatNumber } from "@/lib/piter-format";
import { EscalationModal } from "./EscalationModal";

export function CriticalIncidentBanner() {
  const {
    demoMode,
    p1Row,
    p1Shown,
    triageResult,
    showP1Modal,
    pauseStorm,
    setTriageResult,
    demoImpact,
    bootstrap,
  } = useDemo();
  const { openWith, registerSession } = useChatDock();
  const { setSessionId } = useSession();
  const navigate = useNavigate();
  const [analyzing, setAnalyzing] = useState(false);
  const [showEscalation, setShowEscalation] = useState(false);

  if (!demoMode || !p1Row || showP1Modal) return null;
  if (!p1Shown && !triageResult) return null;

  const incidentId = p1Row.incident_candidate_id || `INC-${p1Row.alert_id}`;
  const impact = triageResult?.impact;
  const users =
    impact?.users_affected != null
      ? formatNumber(Number(impact.users_affected))
      : demoImpact?.users_affected != null
        ? formatNumber(Number(demoImpact.users_affected))
        : null;
  const revenue =
    impact?.revenue_impact_usd_per_hour != null
      ? formatCurrencyUsd(Number(impact.revenue_impact_usd_per_hour))
      : demoImpact?.revenue_impact_usd_per_hour != null
        ? formatCurrencyUsd(Number(demoImpact.revenue_impact_usd_per_hour))
        : null;

  const analyze = async () => {
    if (analyzing || triageResult) return;
    pauseStorm();
    setAnalyzing(true);
    try {
      const data = await postTriage(alertToTriagePayload(p1Row));
      setTriageResult(data);
      const sid = data.memory?.session_id || data.session_id;
      if (sid) {
        registerSession(sid, `${p1Row.service} P1`);
        setSessionId(sid);
      }
      navigate("home");
    } finally {
      setAnalyzing(false);
    }
  };

  return (
    <>
      <AlertBanner title="P1 Critical Incident Detected">
        <p>
          <strong>{p1Row.service}</strong> · {p1Row.environment} — {p1Row.title}
        </p>
        {triageResult?.business_impact ? (
          <p style={{ marginTop: 8 }}>{triageResult.business_impact}</p>
        ) : bootstrap?.alert_stream?.p1_trigger ? (
          <p style={{ marginTop: 8, color: "var(--text-muted)" }}>
            Trigger alert in stream — analyze for full PITER assessment.
          </p>
        ) : null}
        {(users || revenue) && (
          <p className="mono" style={{ marginTop: 8, fontSize: "0.8125rem" }}>
            {users ? `Users affected: ~${users}` : null}
            {users && revenue ? " · " : null}
            {revenue ? `Revenue at risk: ${revenue}/hr` : null}
          </p>
        )}
        <div className="alert-banner-actions">
          {!triageResult ? (
            <Button variant="primary" loading={analyzing} onClick={() => void analyze()}>
              Analyze P1 Incident
            </Button>
          ) : null}
          <Button variant="secondary" onClick={() => setShowEscalation(true)}>
            Escalate to On-Call
          </Button>
          <Button
            variant="ghost"
            onClick={() =>
              openWith({
                message: "What should I check next for this P1 incident?",
                sessionId: triageResult?.memory?.session_id || triageResult?.session_id,
                alert: p1Row,
              })
            }
          >
            Ask Agent
          </Button>
        </div>
      </AlertBanner>
      {showEscalation ? (
        <EscalationModal
          incidentId={incidentId}
          service={p1Row.service}
          severity={p1Row.severity}
          onClose={() => setShowEscalation(false)}
        />
      ) : null}
    </>
  );
}
