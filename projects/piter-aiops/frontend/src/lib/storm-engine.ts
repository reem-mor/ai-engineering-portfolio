import type { AgentDecision, AlertRow } from "@/types/api";

/** Wall-clock second when the P1 candidate modal fires (presenter choreography). */
export const P1_WALL_SECONDS = 20;
/** Total compressed storm playback duration on the wall clock. */
export const STORM_WALL_SECONDS = 90;
const DATA_P1_OFFSET = 175;
const DATA_DURATION = 300;

export function dataOffsetForWall(wallSec: number): number {
  if (wallSec <= P1_WALL_SECONDS) {
    return (wallSec / P1_WALL_SECONDS) * DATA_P1_OFFSET;
  }
  const tail = wallSec - P1_WALL_SECONDS;
  const tailWall = STORM_WALL_SECONDS - P1_WALL_SECONDS;
  return DATA_P1_OFFSET + (tail / tailWall) * (DATA_DURATION - DATA_P1_OFFSET);
}

export function visibleRowsAt(rows: AlertRow[], wallSec: number): AlertRow[] {
  const threshold = dataOffsetForWall(wallSec);
  return rows.filter((r) => Number(r.seconds_offset) <= threshold);
}

export function shouldShowP1Popup(
  rows: AlertRow[],
  wallSec: number,
  alreadyShown: boolean,
): boolean {
  if (alreadyShown) return false;
  if (wallSec < P1_WALL_SECONDS) return false;
  return rows.some((r) => r.is_trigger === "true" || r.severity === "P1");
}

export function deriveDecisions(
  prev: AgentDecision[],
  added: AlertRow[],
  wallSec: number,
): AgentDecision[] {
  const next = [...prev];
  const noise = added.filter((r) => r.is_noise_candidate === "true");
  if (noise.length) {
    next.push({
      id: `noise-${wallSec}`,
      at: wallSec,
      kind: "noise",
      text: `Suppressed ${noise.length} noise candidate${noise.length > 1 ? "s" : ""}`,
    });
  }
  const groups = new Map<string, number>();
  for (const r of added) {
    const key = r.correlation_id || `${r.environment}:${r.service}`;
    groups.set(key, (groups.get(key) || 0) + 1);
  }
  for (const [key, count] of groups) {
    if (count > 1) {
      next.push({
        id: `grp-${key}-${wallSec}`,
        at: wallSec,
        kind: "group",
        text: `Grouped ${count} alerts on ${key.split(":").pop() || key}`,
      });
    }
  }
  const p1 = added.find((r) => r.is_trigger === "true" || r.severity === "P1");
  if (p1) {
    next.push({
      id: `p1-${p1.alert_id}`,
      at: wallSec,
      kind: "p1",
      text: `P1 candidate: ${p1.service} @ ${p1.environment} — ${p1.title}`,
    });
  }
  return next.slice(-40);
}

export function countSeverities(rows: AlertRow[]): Record<string, number> {
  const out: Record<string, number> = { P1: 0, P2: 0, P3: 0, P4: 0 };
  for (const r of rows) {
    const s = r.severity || "P4";
    out[s] = (out[s] || 0) + 1;
  }
  return out;
}

export function alertToTriagePayload(row: AlertRow) {
  return {
    alert_id: row.alert_id,
    service: row.service,
    environment: row.environment,
    severity: row.severity,
    symptom: row.title,
    description: row.title,
    alert_time: row.timestamp,
  };
}
