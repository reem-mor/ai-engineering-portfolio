import { useDemo } from "@/context/demo";
import { useChatDock } from "@/context/chat-dock";
import { useSession } from "@/context/session";
import { useNavigate } from "@/context/navigation";
import { alertToTriagePayload } from "@/lib/storm-engine";
import { postTriage } from "@/lib/api-contract";
import { useState } from "react";
import { EscalationModal } from "./EscalationModal";

export function P1Modal() {
  const {
    showP1Modal,
    p1Row,
    dismissP1,
    pauseStorm,
    setTriageResult,
    triageResult,
    escalatedIds,
  } = useDemo();
  const { openWith, registerSession } = useChatDock();
  const { setSessionId } = useSession();
  const navigate = useNavigate();
  const [analyzing, setAnalyzing] = useState(false);
  const [showEscalation, setShowEscalation] = useState(false);

  if (!showP1Modal || !p1Row) return null;

  const incidentId = p1Row.incident_candidate_id || `INC-${p1Row.alert_id}`;
  const escalated = escalatedIds.has(incidentId);

  const analyze = async () => {
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
      dismissP1();
    } finally {
      setAnalyzing(false);
    }
  };

  const askAgent = () => {
    pauseStorm();
    const sid = triageResult?.memory?.session_id || triageResult?.session_id;
    const msg = sid
      ? "What should I check next for this P1 incident?"
      : `Context: ${p1Row.service} @ ${p1Row.environment}, severity ${p1Row.severity}, alert at ${p1Row.timestamp}. Symptom: ${p1Row.title}. What should I check next?`;
    openWith({ message: msg, sessionId: sid, alert: p1Row });
    dismissP1();
  };

  return (
    <>
      <div className="modal-backdrop" role="presentation">
        <div className="modal p1-modal" role="dialog" aria-labelledby="p1-title">
          <h2 id="p1-title" className="p1-modal-title">
            P1 INCIDENT CANDIDATE
          </h2>
          <p className="mono" style={{ margin: "0 0 8px", color: "var(--sev-p1)" }}>
            {p1Row.service} · {p1Row.environment} · {p1Row.severity}
          </p>
          <p style={{ margin: "0 0 16px", fontSize: "0.9375rem" }}>{p1Row.title}</p>
          {escalated ? (
            <p className="mono" style={{ color: "var(--success)", marginBottom: "12px" }}>
              Escalated
            </p>
          ) : null}
          <div className="p1-modal-actions">
            <button type="button" className="btn btn-primary" onClick={() => void analyze()} disabled={analyzing}>
              {analyzing ? "Analyzing…" : "Analyze Incident"}
            </button>
            <button type="button" className="btn" onClick={() => setShowEscalation(true)}>
              Escalate On-Call
            </button>
            <button type="button" className="btn" onClick={askAgent}>
              Ask Agent
            </button>
            <button type="button" className="btn" onClick={dismissP1}>
              Continue Live
            </button>
          </div>
        </div>
      </div>
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
