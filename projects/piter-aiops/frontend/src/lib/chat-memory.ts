import type { ChatTurn } from "@/components/piter/ops-ui";

const STORAGE_PREFIX = "piter-chat:";

export function loadChatTurns(sessionId: string): ChatTurn[] {
  if (!sessionId || sessionId === "demo-session-preview") return [];
  try {
    const raw = localStorage.getItem(`${STORAGE_PREFIX}${sessionId}`);
    if (!raw) return [];
    const parsed = JSON.parse(raw) as ChatTurn[];
    return Array.isArray(parsed) ? parsed : [];
  } catch {
    return [];
  }
}

export function saveChatTurns(sessionId: string, turns: ChatTurn[]): void {
  if (!sessionId || sessionId === "demo-session-preview" || !turns.length) return;
  try {
    localStorage.setItem(`${STORAGE_PREFIX}${sessionId}`, JSON.stringify(turns));
  } catch {
    /* quota or private mode */
  }
}

export function clearChatTurns(sessionId: string): void {
  if (!sessionId) return;
  try {
    localStorage.removeItem(`${STORAGE_PREFIX}${sessionId}`);
  } catch {
    /* ignore */
  }
}
