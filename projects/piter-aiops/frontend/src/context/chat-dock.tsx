import {
  createContext,
  useCallback,
  useContext,
  useMemo,
  useState,
  type ReactNode,
} from "react";
import type { ChatDockPrefill, ChatResponse, HistoryMessage } from "@/types/api";
import { ApiError, fetchHistory, postChat } from "@/lib/api-contract";

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
};

const ChatDockContext = createContext<ChatDockContextValue | null>(null);

export function ChatDockProvider({ children }: { children: ReactNode }) {
  const [mode, setMode] = useState<DockMode>("open");
  const [sessions, setSessions] = useState<SessionEntry[]>([]);
  const [activeSessionId, setActiveSessionId] = useState<string | null>(null);
  const [messages, setMessages] = useState<HistoryMessage[]>([]);
  const [pending, setPending] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [lastResponse, setLastResponse] = useState<ChatResponse | null>(null);

  const registerSession = useCallback((id: string, label?: string) => {
    setSessions((prev) => {
      if (prev.some((s) => s.id === id)) return prev;
      return [{ id, label: label || id.slice(0, 12), count: 0 }, ...prev];
    });
  }, []);

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
        const data = await postChat(trimmed, activeSessionId);
        setLastResponse(data);
        const sid = data.memory?.session_id || data.session_id || activeSessionId;
        if (sid) {
          setActiveSessionId(sid);
          registerSession(sid);
        }
        const answer = data.answer || data.piter?.investigation || "";
        setMessages((m) => [
          ...m,
          { role: "assistant", content: answer, ts: Date.now() / 1000, mode: data.mode },
        ]);
      } catch (e) {
        setError(e instanceof ApiError ? e.message : "Chat failed");
      } finally {
        setPending(false);
      }
    },
    [activeSessionId, pending, registerSession],
  );

  const openWith = useCallback(
    (prefill: ChatDockPrefill) => {
      setMode("open");
      if (prefill.sessionId) {
        setActiveSessionId(prefill.sessionId);
        registerSession(prefill.sessionId);
        void loadSession(prefill.sessionId);
      }
      if (prefill.message) {
        void send(prefill.message);
      }
    },
    [loadSession, registerSession, send],
  );

  const toggleCollapsed = useCallback(() => {
    setMode((m) => (m === "collapsed" ? "open" : "collapsed"));
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
    ],
  );

  return <ChatDockContext.Provider value={value}>{children}</ChatDockContext.Provider>;
}

export function useChatDock() {
  const ctx = useContext(ChatDockContext);
  if (!ctx) throw new Error("useChatDock must be used within ChatDockProvider");
  return ctx;
}
