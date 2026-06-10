import {
  createContext,
  useCallback,
  useContext,
  useMemo,
  useState,
  type ReactNode,
} from "react";
import type { AlertRow, ChatDockPrefill, ChatResponse, HistoryMessage } from "@/types/api";
import {
  ApiError,
  clearHistory,
  fetchHistory,
  fetchIncidentsHistory,
  postChat,
  postFollowUp,
} from "@/lib/api-contract";
import { useSession } from "@/context/session";

export type DockMode = "collapsed" | "open" | "fullscreen";

type SessionEntry = { id: string; label: string; count: number };

type ChatDockContextValue = {
  mode: DockMode;
  setMode: (mode: DockMode) => void;
  toggleCollapsed: () => void;
  sessions: SessionEntry[];
  activeSessionId: string | null;
  setActiveSessionId: (id: string | null) => void;
  registerSession: (id: string, label?: string) => void;
  messages: HistoryMessage[];
  pending: boolean;
  error: string | null;
  lastResponse: ChatResponse | null;
  send: (text: string) => Promise<void>;
  openWith: (prefill: ChatDockPrefill) => void;
  loadSession: (sessionId: string) => Promise<void>;
  clearChat: () => Promise<void>;
  newSession: () => Promise<void>;
  hydrateSessions: () => Promise<void>;
  clearIncidentContext: () => void;
  contextAlert: Partial<AlertRow> | null;
};

const ChatDockContext = createContext<ChatDockContextValue | null>(null);

export function ChatDockProvider({ children }: { children: ReactNode }) {
  const { sessionId: globalSessionId, setSessionId: setGlobalSessionId } = useSession();
  const [mode, setMode] = useState<DockMode>("open");
  const [sessions, setSessions] = useState<SessionEntry[]>([]);
  const [activeSessionId, setActiveSessionId] = useState<string | null>(null);
  const [messages, setMessages] = useState<HistoryMessage[]>([]);
  const [pending, setPending] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [lastResponse, setLastResponse] = useState<ChatResponse | null>(null);
  const [contextAlert, setContextAlert] = useState<Partial<AlertRow> | null>(null);

  const registerSession = useCallback(
    (id: string, label?: string) => {
      setSessions((prev) => {
        if (prev.some((s) => s.id === id)) return prev;
        return [{ id, label: label || id.slice(0, 12), count: 0 }, ...prev];
      });
      setGlobalSessionId(id);
    },
    [setGlobalSessionId],
  );

  const loadSession = useCallback(async (sessionId: string) => {
    setError(null);
    try {
      const data = await fetchHistory(sessionId);
      setActiveSessionId(data.session_id);
      setMessages(data.messages);
      registerSession(data.session_id, data.session_id.slice(0, 12));
      setSessions((prev) =>
        prev.map((s) => (s.id === data.session_id ? { ...s, count: data.count } : s)),
      );
    } catch (e) {
      setError(e instanceof ApiError ? e.message : "Failed to load session");
    }
  }, [registerSession]);

  const send = useCallback(
    async (text: string) => {
      const trimmed = text.trim();
      if (!trimmed || pending) return;
      setPending(true);
      setError(null);
      setMessages((m) => [...m, { role: "user", content: trimmed, ts: Date.now() / 1000 }]);
      try {
        const sid = activeSessionId || globalSessionId;
        const data = sid
          ? await postFollowUp(sid, trimmed)
          : await postChat(trimmed, sid);
        setLastResponse(data);
        const nextSid = data.memory?.session_id || data.session_id || sid;
        if (nextSid) {
          setActiveSessionId(nextSid);
          registerSession(nextSid);
        }
        const hasStructured = Boolean(data.piter?.investigation || data.piter?.priority);
        const answer = hasStructured
          ? data.piter?.investigation?.slice(0, 400) || data.answer || "Structured analysis ready."
          : data.answer || "";
        if (answer) {
          setMessages((m) => [
            ...m,
            { role: "assistant", content: answer, ts: Date.now() / 1000, mode: data.mode },
          ]);
        }
      } catch (e) {
        setError(e instanceof ApiError ? e.message : "Chat failed");
      } finally {
        setPending(false);
      }
    },
    [activeSessionId, globalSessionId, pending, registerSession],
  );

  const clearChat = useCallback(async () => {
    const sid = activeSessionId || globalSessionId;
    setError(null);
    try {
      await clearHistory(sid);
      setMessages([]);
      setLastResponse(null);
    } catch (e) {
      setError(e instanceof ApiError ? e.message : "Failed to clear chat");
    }
  }, [activeSessionId, globalSessionId]);

  const hydrateSessions = useCallback(async () => {
    try {
      const hist = await fetchIncidentsHistory(50);
      const entries: SessionEntry[] = (hist.investigations || []).map((p) => ({
        id: p.session_id,
        label: `${p.service || "Investigation"} · ${p.severity || "—"}`,
        count: 0,
      }));
      setSessions((prev) => {
        const seen = new Set(prev.map((s) => s.id));
        const merged = [...prev];
        for (const e of entries) {
          if (!seen.has(e.id)) merged.push(e);
        }
        return merged;
      });
    } catch {
      /* history optional for demo */
    }
  }, []);

  const newSession = useCallback(async () => {
    setError(null);
    setActiveSessionId(null);
    setGlobalSessionId(null);
    setMessages([]);
    setLastResponse(null);
    setContextAlert(null);
    try {
      await clearHistory();
    } catch {
      /* fresh session — ignore if no prior history */
    }
  }, [setGlobalSessionId]);

  const openWith = useCallback(
    (prefill: ChatDockPrefill) => {
      setMode("open");
      if (prefill.alert) setContextAlert(prefill.alert);
      if (prefill.triageResponse) setLastResponse(prefill.triageResponse);
      if (prefill.sessionId) {
        setActiveSessionId(prefill.sessionId);
        setGlobalSessionId(prefill.sessionId);
        registerSession(prefill.sessionId);
        void loadSession(prefill.sessionId);
      }
      if (prefill.message) {
        void send(prefill.message);
      }
    },
    [loadSession, registerSession, send, setGlobalSessionId],
  );

  const toggleCollapsed = useCallback(() => {
    setMode((m) => (m === "collapsed" ? "open" : "collapsed"));
  }, []);

  const clearIncidentContext = useCallback(() => {
    setContextAlert(null);
  }, []);

  const value = useMemo(
    () => ({
      mode,
      setMode,
      toggleCollapsed,
      sessions,
      activeSessionId,
      setActiveSessionId,
      registerSession,
      messages,
      pending,
      error,
      lastResponse,
      send,
      openWith,
      loadSession,
      clearChat,
      newSession,
      hydrateSessions,
      clearIncidentContext,
      contextAlert,
    }),
    [
      mode,
      sessions,
      activeSessionId,
      messages,
      pending,
      error,
      lastResponse,
      send,
      openWith,
      loadSession,
      registerSession,
      toggleCollapsed,
      clearChat,
      newSession,
      hydrateSessions,
      clearIncidentContext,
      contextAlert,
    ],
  );

  return <ChatDockContext.Provider value={value}>{children}</ChatDockContext.Provider>;
}

export function useChatDock() {
  const ctx = useContext(ChatDockContext);
  if (!ctx) throw new Error("useChatDock must be used within ChatDockProvider");
  return ctx;
}
