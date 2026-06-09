import { useCallback, useEffect, useState } from "react";
import { fetchHealth } from "@/lib/api-contract";
import { useDemo } from "@/context/demo";
import { useNavigate } from "@/context/navigation";
import type { HealthResponse } from "@/types/api";

function healthDotClass(status: string | undefined): string {
  if (status === "ok") return "ok";
  if (status === "degraded") return "degraded";
  return "down";
}

export function TopBar() {
  const navigate = useNavigate();
  const { demoMode, startStorm, resetDemo, bootstrap } = useDemo();
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [utc, setUtc] = useState(() => new Date().toISOString().slice(11, 19));

  const loadHealth = useCallback(async () => {
    try {
      setHealth(await fetchHealth(true));
    } catch {
      setHealth({ status: "degraded" });
    }
  }, []);

  useEffect(() => {
    void loadHealth();
    const h = setInterval(() => void loadHealth(), 20_000);
    const c = setInterval(() => setUtc(new Date().toISOString().slice(11, 19)), 1000);
    return () => {
      clearInterval(h);
      clearInterval(c);
    };
  }, [loadHealth]);

  const env = bootstrap?.alert_stream?.label?.includes("GIB")
    ? "GIB-UKGC"
    : "production";

  return (
    <header className="top-bar">
      <button type="button" className="top-bar-brand" onClick={() => navigate("home")}>
        <span className="top-bar-logo" aria-hidden>
          ◆
        </span>
        <span>PITER</span>
        <span className="top-bar-sub">AiOps</span>
      </button>

      <div className="top-bar-center">
        {demoMode ? <span className="demo-tag">DEMO</span> : null}
        <span className="mono">ENV {env}</span>
        <span className="mono">UTC {utc}</span>
        <span className="top-bar-health" title={`Infrastructure: ${health?.status ?? "unknown"}`}>
          <span className={`health-dot ${healthDotClass(health?.status)}`} />
          Infra
        </span>
      </div>

      <div className="top-bar-actions">
        {demoMode ? (
          <button type="button" className="btn" onClick={resetDemo}>
            Reset Demo
          </button>
        ) : null}
        {!demoMode ? (
          <button type="button" className="btn btn-primary" onClick={startStorm}>
            Start Alert Stream
          </button>
        ) : null}
        <span className="top-bar-avatar" title="Operator">
          OP
        </span>
      </div>
    </header>
  );
}
