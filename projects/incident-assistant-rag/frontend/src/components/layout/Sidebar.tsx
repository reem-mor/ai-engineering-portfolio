import type { ReactNode } from "react";

export type NavItem = { id: string; label: string };

export type SidebarProps = {
  items: NavItem[];
  activeId: string;
  onSelect: (id: string) => void;
  environmentHint?: string;
};

function IconHome() {
  return (
    <svg className="sidebar__nav-icon" width={18} height={18} viewBox="0 0 24 24" fill="none" aria-hidden>
      <path d="M4 11L12 4l8 7v10a1 1 0 01-1 1h-5v-6H10v6H5a1 1 0 01-1-1V11z" stroke="currentColor" strokeWidth={1.6} strokeLinejoin="round" />
    </svg>
  );
}

function IconBooks() {
  return (
    <svg className="sidebar__nav-icon" width={18} height={18} viewBox="0 0 24 24" fill="none" aria-hidden>
      <path d="M7 5h8a2 2 0 012 2v12H7a2 2 0 00-2 2V7a2 2 0 012-2z" stroke="currentColor" strokeWidth={1.6} />
      <path d="M17 19h4V7a2 2 0 00-2-2h0" stroke="currentColor" strokeWidth={1.6} strokeLinecap="round" />
    </svg>
  );
}

function IconBubble() {
  return (
    <svg className="sidebar__nav-icon" width={18} height={18} viewBox="0 0 24 24" fill="none" aria-hidden>
      <path
        d="M6 17l-2 3V7a3 3 0 013-3h14a3 3 0 013 3v7a3 3 0 01-3 3H10l-4 3z"
        stroke="currentColor"
        strokeWidth={1.6}
        strokeLinejoin="round"
      />
    </svg>
  );
}

function IconAlert() {
  return (
    <svg className="sidebar__nav-icon" width={18} height={18} viewBox="0 0 24 24" fill="none" aria-hidden>
      <path d="M12 8v6M12 18h0" stroke="currentColor" strokeWidth={1.8} strokeLinecap="round" />
      <path
        d="M10.29 4.58L3.82 17.4a2 2 0 001.71 3h13.93a2 2 0 001.71-3l-6.46-12.82a2 2 0 00-3.42 0z"
        stroke="currentColor"
        strokeWidth={1.6}
        strokeLinejoin="round"
      />
    </svg>
  );
}

function IconUpload() {
  return (
    <svg className="sidebar__nav-icon" width={18} height={18} viewBox="0 0 24 24" fill="none" aria-hidden>
      <path d="M12 16V4m0 0l4 4m-4-4L8 8" stroke="currentColor" strokeWidth={1.6} strokeLinecap="round" />
      <path d="M4 15v5h16v-5" stroke="currentColor" strokeWidth={1.6} strokeLinecap="round" />
    </svg>
  );
}

function iconFor(id: string): ReactNode {
  switch (id) {
    case "dashboard":
      return <IconHome />;
    case "knowledge":
      return <IconBooks />;
    case "chat":
      return <IconBubble />;
    case "incident":
      return <IconAlert />;
    case "upload":
      return <IconUpload />;
    default:
      return null;
  }
}

export function Sidebar({ items, activeId, onSelect, environmentHint = "NOC dashboard" }: SidebarProps) {
  return (
    <aside className="sidebar">
      <div className="sidebar__brand-row">
        <svg className="sidebar__logo" width={36} height={36} viewBox="0 0 40 40" aria-hidden>
          <defs>
            <linearGradient id="iqg" x1="0" y1="0" x2="1" y2="1">
              <stop offset="0%" stopColor="#38bdf8" />
              <stop offset="100%" stopColor="#0ea5e9" />
            </linearGradient>
          </defs>
          <rect x={4} y={4} width={32} height={32} rx={8} fill="url(#iqg)" />
          <path d="M12 26V14l8 12 8-12v12" stroke="#0b1220" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" fill="none" />
        </svg>
        <div className="sidebar__brand-block">
          <h1 className="sidebar__title">IncidentIQ</h1>
          <p className="sidebar__tagline">RAG assistant</p>
        </div>
      </div>

      <p className="sidebar__env-pill">
        Workspace · <strong>{environmentHint}</strong>
      </p>

      <p className="sidebar__nav-label">Navigate</p>
      <nav aria-label="Primary">
        <ul className="sidebar__nav-list">
          {items.map((item) => (
            <li key={item.id}>
              <button
                type="button"
                className={`sidebar__nav-btn${activeId === item.id ? " sidebar__nav-btn--active" : ""}`}
                onClick={() => onSelect(item.id)}
                aria-current={activeId === item.id ? "page" : undefined}
              >
                {iconFor(item.id)}
                {item.label}
              </button>
            </li>
          ))}
        </ul>
      </nav>
    </aside>
  );
}
