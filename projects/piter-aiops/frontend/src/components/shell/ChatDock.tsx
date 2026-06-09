import { useEffect, useRef, useState } from "react";
import { useChatDock } from "@/context/chat-dock";
import { useSession } from "@/context/session";
import { fetchHistory } from "@/lib/api-contract";
import { PiterResponseView } from "@/components/noc/PiterResponseView";

export function ChatDock() {
  const {
    mode,
    setMode,
    toggleCollapsed,
    sessions,
    activeSessionId,
    setActiveSessionId,
    messages,
    pending,
    error,
    lastResponse,
    send,
    loadSession,
    clearChat,
  } = useChatDock();
  const { setSessionId } = useSession();
  const [draft, setDraft] = useState("");
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    void fetchHistory().then((h) => {
      if (h.session_id) {
        setActiveSessionId(h.session_id);
        void loadSession(h.session_id);
      }
    });
  }, [loadSession, setActiveSessionId]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, pending]);

  if (mode === "collapsed") {
    return (
      <aside className="chat-dock chat-dock-collapsed">
        <button type="button" className="dock-rail-btn" onClick={toggleCollapsed} title="Open agent chat">
          ◈
        </button>
      </aside>
    );
  }

  const submit = () => {
    const text = draft.trim();
    if (!text) return;
    setDraft("");
    void send(text);
  };

  return (
    <aside className={`chat-dock${mode === "fullscreen" ? " chat-dock-full" : ""}`}>
      <header className="chat-dock-header">
        <span>Agent Chat</span>
        <div className="chat-dock-tools">
          <button
            type="button"
            className="btn btn-sm"
            onClick={() => void clearChat()}
            title="Clear chat history"
          >
            Clear
          </button>
          <button
            type="button"
            className="btn btn-icon"
            onClick={() => setMode(mode === "fullscreen" ? "open" : "fullscreen")}
            title={mode === "fullscreen" ? "Exit full panel" : "Expand full panel"}
          >
            {mode === "fullscreen" ? "⊟" : "⊞"}
          </button>
          <button type="button" className="btn btn-icon" onClick={toggleCollapsed} title="Collapse">
            ›
          </button>
        </div>
      </header>

      {sessions.length > 0 ? (
        <div className="chat-sessions">
          <label className="label">Sessions</label>
          <select
            className="select"
            value={activeSessionId || ""}
            onChange={(e) => {
              const id = e.target.value;
              setActiveSessionId(id || null);
              setSessionId(id || null);
              if (id) void loadSession(id);
            }}
          >
            <option value="">—</option>
            {sessions.map((s) => (
              <option key={s.id} value={s.id}>
                {s.label} ({s.count})
              </option>
            ))}
          </select>
        </div>
      ) : null}

      <div className="chat-messages">
        {messages.length === 0 && !pending ? (
          <p className="chat-empty">Ask about alerts, incidents, or runbooks.</p>
        ) : null}
        {messages.map((m, i) => (
          <div key={i} className={`chat-bubble chat-${m.role}`}>
            <div className="chat-role">{m.role === "user" ? "You" : "PITER"}</div>
            <div className="chat-text">{m.content}</div>
          </div>
        ))}
        {pending ? <div className="chat-bubble chat-assistant chat-thinking">Agent thinking…</div> : null}
        {error ? <div className="chat-error">{error}</div> : null}
        <div ref={bottomRef} />
      </div>

      {lastResponse?.piter && messages.length > 0 ? (
        <div className="chat-structured">
          <PiterResponseView response={lastResponse} />
        </div>
      ) : null}

      <footer className="chat-compose">
        <textarea
          className="textarea chat-input"
          rows={2}
          value={draft}
          placeholder="Message agent…"
          onChange={(e) => setDraft(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter" && !e.shiftKey) {
              e.preventDefault();
              submit();
            }
          }}
        />
        <button type="button" className="btn btn-primary" onClick={submit} disabled={pending}>
          Send
        </button>
      </footer>
    </aside>
  );
}
