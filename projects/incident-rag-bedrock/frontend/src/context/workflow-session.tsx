import {
  createContext,
  useCallback,
  useContext,
  useMemo,
  useState,
  type ReactNode,
} from "react";
import { useBootstrap } from "@/context/bootstrap";
import { sessionImpactTotals } from "@/lib/workflow-utils";

type WorkflowSessionValue = {
  triagedIds: Set<string>;
  resolved: Set<string>;
  triageCount: number;
  lastTriageAt: string | null;
  recordTriageComplete: (alertId: string) => void;
  markResolved: (alertId: string) => void;
  countedIds: Set<string>;
  sessionTotals: { dollars: number; minutes: number };
};

const WorkflowSessionContext = createContext<WorkflowSessionValue | null>(null);

export function WorkflowSessionProvider({ children }: { children: ReactNode }) {
  const { alerts } = useBootstrap();
  const [triagedIds, setTriagedIds] = useState<Set<string>>(() => new Set());
  const [resolved, setResolved] = useState<Set<string>>(() => new Set());
  const [triageCount, setTriageCount] = useState(0);
  const [lastTriageAt, setLastTriageAt] = useState<string | null>(null);

  const countedIds = useMemo(() => {
    const ids = new Set<string>();
    triagedIds.forEach((id) => ids.add(id));
    resolved.forEach((id) => ids.add(id));
    return ids;
  }, [triagedIds, resolved]);

  const sessionTotals = useMemo(
    () => sessionImpactTotals(alerts, countedIds),
    [alerts, countedIds],
  );

  const recordTriageComplete = useCallback((alertId: string) => {
    setTriagedIds((prev) => new Set(prev).add(alertId));
    setTriageCount((n) => n + 1);
    setLastTriageAt(
      new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
    );
  }, []);

  const markResolved = useCallback((alertId: string) => {
    setResolved((prev) => new Set(prev).add(alertId));
  }, []);

  const value = useMemo(
    () => ({
      triagedIds,
      resolved,
      triageCount,
      lastTriageAt,
      recordTriageComplete,
      markResolved,
      countedIds,
      sessionTotals,
    }),
    [
      triagedIds,
      resolved,
      triageCount,
      lastTriageAt,
      recordTriageComplete,
      markResolved,
      countedIds,
      sessionTotals,
    ],
  );

  return (
    <WorkflowSessionContext.Provider value={value}>
      {children}
    </WorkflowSessionContext.Provider>
  );
}

export function useWorkflowSession() {
  const ctx = useContext(WorkflowSessionContext);
  if (!ctx) {
    throw new Error("useWorkflowSession must be used within WorkflowSessionProvider");
  }
  return ctx;
}
