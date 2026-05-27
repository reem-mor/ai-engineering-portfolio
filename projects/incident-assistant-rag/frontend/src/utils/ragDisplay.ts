/** Display helpers for RAG trust states (no API changes). */

import { NO_KB_MATCH_MESSAGE } from "../content/opsCopy";

export const KB_NO_CONTEXT_HINT =
  "Answers use only retrieved runbook and incident documentation—not general model knowledge.";

export const KB_EXPAND_NO_MATCH_HINT = NO_KB_MATCH_MESSAGE;

export function severityPriorityLabel(severity: string): string | null {
  const s = severity.toLowerCase().trim();
  if (s === "critical") return "P1";
  if (s === "high") return "P2";
  if (s === "medium") return "P3";
  if (s === "low") return "P4";
  return null;
}

export function isLowConfidence(confidence: string): boolean {
  return confidence.toLowerCase().trim() === "low";
}

export function trustBannerTitle(usedContext: boolean, confidence: string): string {
  if (!usedContext) return "No knowledge-base match";
  if (isLowConfidence(confidence)) return "Low-confidence match";
  return "Grounded in retrieved context";
}
