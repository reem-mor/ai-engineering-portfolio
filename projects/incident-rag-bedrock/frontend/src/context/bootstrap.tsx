import {
  createContext,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";
import { fetchBootstrap, normalizeWorkflowAlert } from "@/lib/api";
import type { BootstrapPayload, WorkflowAlert } from "@/types/rag";

type BootstrapState = {
  loading: boolean;
  error: string | null;
  data: BootstrapPayload | null;
  alerts: WorkflowAlert[];
};

const BootstrapContext = createContext<BootstrapState | null>(null);

export function BootstrapProvider({ children }: { children: ReactNode }) {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [data, setData] = useState<BootstrapPayload | null>(null);

  useEffect(() => {
    let cancelled = false;
    fetchBootstrap()
      .then((payload) => {
        if (!cancelled) {
          setData(payload);
          setError(null);
        }
      })
      .catch((err: unknown) => {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : "Failed to load app data");
        }
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, []);

  const alerts = useMemo(
    () => (data?.workflow_alerts ?? []).map((a) => normalizeWorkflowAlert(a)),
    [data],
  );

  const value = useMemo(
    () => ({ loading, error, data, alerts }),
    [loading, error, data, alerts],
  );

  return (
    <BootstrapContext.Provider value={value}>{children}</BootstrapContext.Provider>
  );
}

export function useBootstrap() {
  const ctx = useContext(BootstrapContext);
  if (!ctx) throw new Error("useBootstrap must be used within BootstrapProvider");
  return ctx;
}
