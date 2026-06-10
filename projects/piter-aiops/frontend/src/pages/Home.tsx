import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { fetchInvestigations } from "@/lib/api-contract";
import { useDemo } from "@/context/demo";
import { useChatDock } from "@/context/chat-dock";
import { countSeverities } from "@/lib/storm-engine";
import type { AlertRow, Investigation, InvestigationsResponse, Priority } from "@/types/api";
import { PriorityBadge } from "@/components/noc/PriorityBadge";
import { PiterResponseView } from "@/components/noc/PiterResponseView";
import { LoadingSkeleton } from "@/components/noc/LoadingSkeleton";
import { CriticalIncidentBanner } from "@/components/demo/CriticalIncidentBanner";
import { MTTRPanel } from "@/components/noc/MTTRPanel";
import { MetricCard } from "@/components/ui/MetricCard";
import { PageHeader } from "@/components/ui/PageHeader";

function noiseCount(rows: AlertRow[]): number {
  return rows.filter((r) => r.is_noise_candidate === "true").length;
}

export function HomePage() {
  const {
    demoMode,
    visible,
    decisions,
    stormComplete,
    demoImpact,
    bootstrap,
    triageResult,
    escalatedIds,
    p1Row,
    wallSec,
  } = useDemo();
  const { openWith, send } = useChatDock();
  const [inv, setInv] = useState<InvestigationsResponse | null>(null);
  const seenAlerts = useRef<Set<string>>(new Set());

  const loadInv = useCallback(async () => {
    try {
      setInv(await fetchInvestigations(50));
    } catch {
      setInv(null);
    }
  }, []);

  useEffect(() => {
    void loadInv();
  }, [loadInv, stormComplete]);

  const alertRows = demoMode ? visible : [];
  const sev = countSeverities(alertRows);
  const totalReceived = demoMode ? alertRows.length : (bootstrap?.alert_stream?.total ?? 0);
  const suppressed = demoMode ? noiseCount(alertRows) : (bootstrap?.alert_stream?.noise_suppressed ?? 0);
  const activeIncidents = demoMode
    ? alertRows.filter((r) => r.incident_candidate_id).length
    : (inv?.summary?.active_count ?? 0);

  const demoKpis = useMemo(() => {
    if (!demoMode || !demoImpact) return null;
    const mttr = demoImpact.escalation_minutes ?? demoImpact.mttr_reduction_minutes;
    const cost = demoImpact.estimated_total_cost ?? demoImpact.cost_avoided_usd;
    return { mttr, cost };
  }, [demoMode, demoImpact]);

  const askAlert = (row: AlertRow) => {
    openWith({
      message: `Alert ${row.alert_id}: ${row.service} @ ${row.environment}, ${row.severity} at ${row.timestamp}. ${row.title}. Summarize impact and next checks.`,
      alert: row,
    });
  };

  const scrollToAnalysis = () => {
    document.getElementById("piter-analysis-panel")?.scrollIntoView({ behavior: "smooth" });
  };

  return (
    <div className="grid-stack home-page">
      <PageHeader
        title="Operations Dashboard"
        subtitle="Live production operations state — alert stream, incident queue, and AI copilot"
      />

      <CriticalIncidentBanner />

      <div className="kpi-grid">
        <MetricCard label="Alerts received" value={totalReceived} />
        <MetricCard label="Noise suppressed" value={suppressed} />
        <MetricCard label="Active incidents" value={activeIncidents} />
        <MetricCard label="P1 / P2 / P3" value={`${sev.P1} / ${sev.P2} / ${sev.P3}`} mono />
        <MetricCard label="Escalations" value={escalatedIds.size} />
        {demoMode && demoKpis ? (
          <>
            <MetricCard label="MTTR reduced (min)" value={String(demoKpis.mttr ?? "—")} demo />
            <MetricCard label="Cost avoided (USD)" value={String(demoKpis.cost ?? "—")} demo />
          </>
        ) : null}
      </div>

      {(demoMode && (demoImpact || triageResult)) || triageResult ? (
        <MTTRPanel
          demoImpact={demoImpact}
          triageResult={triageResult}
          noiseSuppressed={suppressed}
          p1DetectionSec={p1Row && demoMode ? Math.round(wallSec) || 20 : undefined}
        />
      ) : null}

      <div className="home-grid">
        <section className="panel home-panel">
          <div className="stream-header">
            <h2 className="panel-title" style={{ margin: 0 }}>
              Alert stream
            </h2>
            {demoMode ? (
              <span className="stream-counter stream-live-pulse">Live · {alertRows.length} alerts</span>
            ) : null}
          </div>
          {!demoMode ? (
            <div className="idle-state-card">
              <p>
                Idle — use <strong>Start Alert Stream</strong> in the top bar to begin demo playback.
              </p>
            </div>
          ) : (
            <p className="mono" style={{ color: "var(--text-muted)", fontSize: "0.75rem", margin: "0 0 8px" }}>
              Noise suppression active · correlated groups merged
            </p>
          )}
          <div className="table-wrap">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Time</th>
                  <th>Service</th>
                  <th>Env</th>
                  <th>Sev</th>
                  <th>Title</th>
                  <th />
                </tr>
              </thead>
              <tbody>
                {alertRows.length === 0 ? (
                  <tr>
                    <td colSpan={6} className="mono" style={{ color: "var(--text-muted)" }}>
                      {demoMode ? "Awaiting alerts…" : "No alerts in view"}
                    </td>
                  </tr>
                ) : (
                  alertRows
                    .slice()
                    .reverse()
                    .slice(0, 40)
                    .map((r) => {
                      const isNew = !seenAlerts.current.has(r.alert_id);
                      if (isNew) seenAlerts.current.add(r.alert_id);
                      const rowClass = [
                        isNew ? "alert-row-enter" : "",
                        p1Row && r.alert_id === p1Row.alert_id ? "alert-row-p1" : "",
                        r.is_noise_candidate === "true" ? "alert-row-noise" : "",
                        r.is_trigger === "true" ? "alert-row-trigger" : "",
                      ]
                        .filter(Boolean)
                        .join(" ");
                      return (
                      <tr key={r.alert_id} className={rowClass || undefined}>
                        <td className="mono">{r.timestamp.slice(11, 19)}</td>
                        <td>{r.service}</td>
                        <td>{r.environment}</td>
                        <td>
                          <PriorityBadge priority={(r.severity as Priority) || "P4"} />
                        </td>
                        <td>{r.title}</td>
                        <td>
                          <button type="button" className="btn btn-sm" onClick={() => askAlert(r)}>
                            Ask agent
                          </button>
                        </td>
                      </tr>
                    );
                    })
                )}
              </tbody>
            </table>
          </div>
        </section>

        <section className="panel home-panel">
          <h2 className="panel-title">Agent decisions</h2>
          <ul className="decision-feed">
            {decisions.length === 0 ? (
              <li className="mono" style={{ color: "var(--text-muted)" }}>
                Awaiting stream…
              </li>
            ) : (
              decisions
                .slice()
                .reverse()
                .map((d) => (
                  <li key={d.id} className={`decision decision-${d.kind}`}>
                    <span className="mono">{d.at.toFixed(0)}s</span> {d.text}
                  </li>
                ))
            )}
          </ul>
        </section>
      </div>

      <div className="home-grid">
        <section className="panel">
          <h2 className="panel-title">Noise patterns</h2>
          <p className="mono" style={{ fontSize: "0.8125rem", margin: 0 }}>
            Suppressed candidates: {suppressed}
            {demoMode ? ` · visible noise flags: ${noiseCount(alertRows)}` : ""}
          </p>
        </section>

        <section className="panel">
          <h2 className="panel-title">Incident queue</h2>
          <IncidentQueue items={inv?.investigations ?? []} escalatedIds={escalatedIds} onAsk={openWith} />
        </section>
      </div>

      {triageResult ? (
        <section>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <h2 className="panel-title">P1 analysis</h2>
            <button type="button" className="btn btn-sm" onClick={scrollToAnalysis}>
              Jump to analysis
            </button>
          </div>
          <PiterResponseView
            response={triageResult}
            onFollowUp={(q) => void send(q)}
          />
        </section>
      ) : null}
    </div>
  );
}

function IncidentQueue({
  items,
  escalatedIds,
  onAsk,
}: {
  items: Investigation[];
  escalatedIds: Set<string>;
  onAsk: (p: { message: string }) => void;
}) {
  const [state, setState] = useState<Record<string, string>>({});

  if (!items.length) return <LoadingSkeleton lines={3} />;

  return (
    <ul className="incident-queue">
      {items.slice(0, 8).map((item) => {
        const st = state[item.id] || item.status || "open";
        const escalated = escalatedIds.has(item.id);
        return (
          <li key={item.id} className={`incident-row${item.priority === "P1" ? " incident-row-p1" : ""}`}>
            <div>
              <PriorityBadge priority={item.priority} />
              <span className="mono" style={{ marginLeft: 8 }}>
                {item.service}
              </span>
              <div style={{ fontSize: "0.8125rem", marginTop: 4 }}>{item.alert}</div>
            </div>
            <div className="incident-actions">
              <select
                className="select select-sm"
                value={escalated ? "escalated" : st}
                onChange={(e) => setState((s) => ({ ...s, [item.id]: e.target.value }))}
              >
                <option value="open">Open</option>
                <option value="in_process">In process</option>
                <option value="resolved">Resolved</option>
                <option value="escalated">Escalated</option>
              </select>
              <button
                type="button"
                className="btn btn-sm"
                onClick={() =>
                  onAsk({
                    message: `Incident ${item.id}: ${item.service} ${item.priority} — ${item.conclusionDetail || item.alert}`,
                  })
                }
              >
                Ask agent
              </button>
            </div>
          </li>
        );
      })}
    </ul>
  );
}
