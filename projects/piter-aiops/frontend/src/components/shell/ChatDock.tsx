import { useEffect, useRef, useState } from "react";
import {
  Bot,
  ChevronRight,
  Loader2,
  Maximize2,
  MessageSquare,
  Minimize2,
  Plus,
  Trash2,
  X,
} from "lucide-react";
import { COPILOT_COMMON_QUESTIONS } from "@/lib/common-questions";
import { DocumentUploadPanel } from "@/components/shell/DocumentUploadPanel";
import { useChatDock } from "@/context/chat-dock";
import { useSession } from "@/context/session";
import { useDemo } from "@/context/demo";
import { formatChatText, investigationSnippet } from "@/lib/chat-format";
import { SourceBadge } from "@/components/ui/SourceBadge";
import { Button } from "@/components/ui/Button";
import { PriorityBadge } from "@/components/noc/PriorityBadge";
import type { Priority } from "@/types/api";

export function ChatDock() {
  const {
    mode,
    setMode,
    toggleCollapsed,
    sessions,
    activeSessionId,
    selectSession,
    messages,
    pending,
    error,
    lastResponse,
    send,
    clearChat,
    newSession,
    clearIncidentContext,
    contextAlert,
    incidentSessionId,
    registerSession,
  } = useChatDock();
  const { setSessionId } = useSession();
  const { p1Row, triageResult } = useDemo();
  const [draft, setDraft] = useState("");
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const sid = triageResult?.memory?.session_id || triageResult?.session_id;
    if (!sid) return;
    registerSession(sid, `${p1Row?.service || "Investigation"} P1`, {
      incident: true,
      activate: !incidentSessionId,
    });
  }, [triageResult, p1Row?.service, registerSession, incidentSessionId]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, pending]);

  if (mode === "collapsed") {
    return (
      <aside className="chat-dock chat-dock-collapsed">
        <button type="button" className="dock-rail-btn" onClick={toggleCollapsed} title="Open Agent Copilot">
          <MessageSquare size={18} />
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

  const alert = contextAlert || p1Row;
  const followups = lastResponse?.recommended_followups || lastResponse?.next_questions || [];

  const scrollToAnalysis = () => {
    document.getElementById("piter-analysis-panel")?.scrollIntoView({ behavior: "smooth" });
  };

  return (
    <aside className={`chat-dock${mode === "fullscreen" ? " chat-dock-full" : ""}`}>
      <header className="chat-dock-header">
        <div className="chat-dock-title">
          <Bot size={18} className="chat-dock-title-icon" aria-hidden />
          <div>
            <span className="chat-dock-title-text">Agent Copilot</span>
            <span className="chat-dock-title-sub">PITER incident assistant</span>
          </div>
        </div>
        <div className="chat-dock-tools">
          <button type="button" className="btn btn-sm" onClick={() => void newSession()} title="New session">
            <Plus size={14} /> New Session
          </button>
          <button
            type="button"
            className="btn btn-sm"
            onClick={() => void clearChat()}
            title="Clear active session messages"
          >
            <Trash2 size={14} /> Clear Chat
          </button>
          <button
            type="button"
            className="btn btn-icon"
            onClick={() => setMode(mode === "fullscreen" ? "open" : "fullscreen")}
            title={mode === "fullscreen" ? "Exit full panel" : "Expand full panel"}
          >
            {mode === "fullscreen" ? <Minimize2 size={16} /> : <Maximize2 size={16} />}
          </button>
          <button type="button" className="btn btn-icon" onClick={toggleCollapsed} title="Collapse">
            <ChevronRight size={16} />
          </button>
        </div>
      </header>

      {alert ? (
        <div className="chat-context-chip">
          <span className="chat-context-label">
            Current context: {(alert.severity as string) || "P1"} {alert.service} incident
          </span>
          <PriorityBadge priority={(alert.severity as Priority) || "P4"} />
          <span>
            {alert.service} · {alert.environment} · {alert.alert_id}
          </span>
          <button
            type="button"
            className="chat-context-clear"
            onClick={clearIncidentContext}
            title="Clear incident context"
            aria-label="Clear incident context"
          >
            <X size={14} />
          </button>
        </div>
      ) : null}

      <div className="chat-common-questions">
        {COPILOT_COMMON_QUESTIONS.map((q) => (
          <button key={q} type="button" className="follow-up-chip" onClick={() => void send(q)} disabled={pending}>
            {q}
          </button>
        ))}
      </div>

      <div className="chat-sessions">
        <label className="label" htmlFor="chat-session-select">
          Session
        </label>
        <select
          id="chat-session-select"
          className="select"
          value={activeSessionId || ""}
          onChange={(e) => {
            const id = e.target.value || null;
            selectSession(id);
            setSessionId(id);
          }}
        >
          <option value="">New / unsaved session</option>
          {sessions.map((s) => (
            <option key={s.id} value={s.id}>
              {s.label}
              {s.count > 0 ? ` (${s.count} msgs)` : ""}
            </option>
          ))}
        </select>
      </div>

      <div className="chat-messages">
        {messages.length === 0 && !pending ? (
          <p className="chat-empty">
            Ask about the selected incident, prior alerts, runbooks, or escalation paths. Follow-ups use session
            memory when available.
          </p>
        ) : null}
        {messages.map((m, i) => (
          <div key={i} className={`chat-bubble chat-${m.role}`}>
            <div className="chat-role">
              {m.role === "user" ? "You" : "PITER Agent"}
              {m.role === "assistant" && m.mode ? (
                <span style={{ marginLeft: 8 }}>
                  <SourceBadge mode={m.mode} />
                </span>
              ) : null}
            </div>
            <div className="chat-text">{formatChatText(m.content)}</div>
          </div>
        ))}
        {pending ? (
          <div className="chat-bubble chat-assistant chat-thinking" role="status" aria-live="polite">
            <Loader2 size={14} className="chat-thinking-spinner" aria-hidden />
            Agent investigating…
          </div>
        ) : null}
        {error ? <div className="chat-error">{error}</div> : null}
        <div ref={bottomRef} />
      </div>

      {lastResponse?.piter && messages.length > 0 ? (
        <div className="chat-summary-card">
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <strong>Analysis summary</strong>
            <SourceBadge mode={lastResponse.mode} fallbackUsed={lastResponse.fallback_used} />
          </div>
          {lastResponse.piter.priority ? (
            <div style={{ marginTop: 6 }}>
              <PriorityBadge priority={lastResponse.piter.priority as Priority} />
            </div>
          ) : null}
          <p className="chat-summary-snippet">{investigationSnippet(lastResponse)}</p>
          <Button variant="secondary" size="sm" onClick={scrollToAnalysis}>
            View full analysis
          </Button>
          {followups.length > 0 ? (
            <div className="follow-up-chips">
              {followups.slice(0, 4).map((q) => (
                <button key={q} type="button" className="follow-up-chip" onClick={() => void send(q)}>
                  {q}
                </button>
              ))}
            </div>
          ) : null}
        </div>
      ) : null}

      <DocumentUploadPanel compact />

      <footer className="chat-compose">
        <textarea
          className="textarea chat-input"
          rows={2}
          value={draft}
          placeholder="Ask the copilot about this incident…"
          onChange={(e) => setDraft(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter" && !e.shiftKey) {
              e.preventDefault();
              submit();
            }
          }}
        />
        <Button variant="primary" onClick={submit} disabled={pending} loading={pending}>
          Send
        </Button>
      </footer>
    </aside>
  );
}
