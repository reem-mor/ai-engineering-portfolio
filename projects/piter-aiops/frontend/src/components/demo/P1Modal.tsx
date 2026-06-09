import { useEffect, useState } from "react";
import { Check, Circle, Loader2 } from "lucide-react";
import { useDemo } from "@/context/demo";
import { useChatDock } from "@/context/chat-dock";
import { useSession } from "@/context/session";
import { useNavigate } from "@/context/navigation";
import { alertToTriagePayload } from "@/lib/storm-engine";
import { postTriage } from "@/lib/api-contract";
import { Button } from "@/components/ui/Button";
import { EscalationModal } from "./EscalationModal";

const ANALYZE_STEPS = [
  "Reading alert context",
  "Checking deployments",
  "Querying knowledge base",
  "Similar incidents",
  "Escalation recommendation",
  "Generating PITER response",
];

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
  const [stepIndex, setStepIndex] = useState(-1);
  const [done, setDone] = useState(false);
  const [showEscalation, setShowEscalation] = useState(false);

  useEffect(() => {
    if (!analyzing) {
      setStepIndex(-1);
      return;
    }
    setStepIndex(0);
    const timers = ANALYZE_STEPS.map((_, i) =>
      window.setTimeout(() => setStepIndex(i), i * 450),
    );
    return () => timers.forEach((t) => window.clearTimeout(t));
  }, [analyzing]);

  if (!showP1Modal || !p1Row) return null;

  const incidentId = p1Row.incident_candidate_id || `INC-${p1Row.alert_id}`;
  const escalated = escalatedIds.has(incidentId);

  const analyze = async () => {
    if (analyzing) return;
    pauseStorm();
    setAnalyzing(true);
    setDone(false);
    try {
      const data = await postTriage(alertToTriagePayload(p1Row));
      setTriageResult(data);
      const sid = data.memory?.session_id || data.session_id;
      if (sid) {
        registerSession(sid, `${p1Row.service} P1`);
        setSessionId(sid);
      }
      setStepIndex(ANALYZE_STEPS.length);
      setDone(true);
      navigate("home");
      window.setTimeout(() => dismissP1(), 600);
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
            P1 critical incident
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

          {analyzing || done ? (
            <ul className="analyze-steps" aria-live="polite">
              {ANALYZE_STEPS.map((label, i) => {
                const isDone = stepIndex > i || done;
                const isActive = analyzing && stepIndex === i;
                return (
                  <li
                    key={label}
                    className={`analyze-step${isDone ? " done" : ""}${isActive ? " active" : ""}`}
                  >
                    {isDone ? (
                      <Check size={14} />
                    ) : isActive ? (
                      <Loader2 size={14} className="btn-spinner" />
                    ) : (
                      <Circle size={14} />
                    )}
                    {label}
                  </li>
                );
              })}
            </ul>
          ) : null}

          <div className="p1-modal-actions">
            <Button variant="primary" size="lg" loading={analyzing} onClick={() => void analyze()}>
              Analyze P1 Incident
            </Button>
            <Button variant="secondary" onClick={() => setShowEscalation(true)} disabled={analyzing}>
              Escalate On-Call
            </Button>
            <Button variant="secondary" onClick={askAgent} disabled={analyzing}>
              Ask Agent
            </Button>
            <Button variant="ghost" onClick={dismissP1} disabled={analyzing}>
              Continue Live
            </Button>
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
