import { useCallback, useEffect, useMemo, useState } from "react";
import { fetchAlertStream, fetchInvestigations } from "@/lib/api-contract";
import { useChatDock } from "@/context/chat-dock";
import type { AlertRow, Investigation } from "@/types/api";
import { PriorityBadge } from "@/components/noc/PriorityBadge";
import { ErrorState } from "@/components/noc/ErrorState";
import { LoadingSkeleton } from "@/components/noc/LoadingSkeleton";

type View = "alerts" | "incidents";

export function HistoryInvestigationsPage() {
  const [view, setView] = useState<View>("alerts");
  const [alerts, setAlerts] = useState<AlertRow[]>([]);
  const [incidents, setIncidents] = useState<Investigation[]>([]);
  const [q, setQ] = useState("");
  const [sev, setSev] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const { openWith } = useChatDock();
  const [expanded, setExpanded] = useState<string | null>(null);

  const load = useCallback(async () => {
    setError(null);
    try {
      const [stream, inv] = await Promise.all([
        fetchAlertStream(true),
        fetchInvestigations(100),
      ]);
      setAlerts(stream.rows || []);
      setIncidents(inv.investigations || []);
    } catch {
      setError("Failed to load history data");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  const filteredAlerts = useMemo(() => {
    return alerts.filter((r) => {
      if (sev && r.severity !== sev) return false;
      if (!q) return true;
      const hay = `${r.service} ${r.environment} ${r.title} ${r.timestamp}`.toLowerCase();
      return hay.includes(q.toLowerCase());
    });
  }, [alerts, q, sev]);

  const filteredIncidents = useMemo(() => {
    return incidents.filter((i) => {
      if (sev && i.priority !== sev) return false;
      if (!q) return true;
      const hay = `${i.service} ${i.environment} ${i.alert} ${i.conclusion}`.toLowerCase();
      return hay.includes(q.toLowerCase());
    });
  }, [incidents, q, sev]);

  if (loading) {
    return (
      <div className="grid-stack">
        <h1 style={{ margin: 0, fontSize: "1.125rem" }}>History & Investigations</h1>
        <LoadingSkeleton lines={6} />
      </div>
    );
  }

  if (error) return <ErrorState message={error} onRetry={load} />;

  return (
    <div className="grid-stack">
      <h1 style={{ margin: 0, fontSize: "1.125rem" }}>History & Investigations</h1>

      <div className="history-toolbar">
        <div className="toggle-group">
          <button
            type="button"
            className={`btn${view === "alerts" ? " active" : ""}`}
            onClick={() => setView("alerts")}
          >
            Alerts
          </button>
          <button
            type="button"
            className={`btn${view === "incidents" ? " active" : ""}`}
            onClick={() => setView("incidents")}
          >
            Incidents
          </button>
        </div>
        <input
          className="input"
          placeholder="Search service, symptom…"
          value={q}
          onChange={(e) => setQ(e.target.value)}
        />
        <select className="select" value={sev} onChange={(e) => setSev(e.target.value)}>
          <option value="">All severities</option>
          <option value="P1">P1</option>
          <option value="P2">P2</option>
          <option value="P3">P3</option>
          <option value="P4">P4</option>
        </select>
      </div>

      {view === "alerts" ? (
        <div className="table-wrap panel">
          <table className="data-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Time</th>
                <th>Service</th>
                <th>Sev</th>
                <th>Title</th>
                <th />
              </tr>
            </thead>
            <tbody>
              {filteredAlerts.slice(0, 80).map((r) => (
                <tr key={r.alert_id}>
                  <td className="mono">{r.alert_id}</td>
                  <td className="mono">{r.timestamp}</td>
                  <td>{r.service}</td>
                  <td>
                    <PriorityBadge priority={(r.severity as "P1") || "P4"} />
                  </td>
                  <td>{r.title}</td>
                  <td>
                    <button
                      type="button"
                      className="btn btn-sm"
                      onClick={() =>
                        openWith({
                          message: `Review alert ${r.alert_id}: ${r.title}`,
                          alert: r,
                        })
                      }
                    >
                      Ask agent
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <div className="grid-stack">
          {filteredIncidents.map((i) => (
            <article key={i.id} className="panel">
              <button
                type="button"
                className="btn"
                style={{ width: "100%", justifyContent: "space-between" }}
                onClick={() => setExpanded(expanded === i.id ? null : i.id)}
              >
                <span>
                  <PriorityBadge priority={i.priority} /> {i.service} — {i.alert.slice(0, 48)}
                </span>
                <span className="mono">{i.alertTime}</span>
              </button>
              {expanded === i.id ? (
                <div style={{ marginTop: 12, fontSize: "0.875rem" }}>
                  <p>
                    <strong>Conclusion:</strong> {i.conclusion}
                  </p>
                  <p>{i.conclusionDetail}</p>
                  <p className="mono">Impact: {i.impact}</p>
                  <button
                    type="button"
                    className="btn btn-sm"
                    onClick={() =>
                      openWith({ message: `Investigation ${i.id}: ${i.conclusionDetail}` })
                    }
                  >
                    Ask agent
                  </button>
                </div>
              ) : null}
            </article>
          ))}
        </div>
      )}
    </div>
  );
}
