import type { PageKey } from "@/types/api";

const NAV: { key: PageKey; label: string }[] = [
  { key: "home", label: "Operations" },
  { key: "analytics", label: "Agent Analytics" },
  { key: "history", label: "History" },
  { key: "analyzer", label: "Analyzer" },
  { key: "system", label: "System" },
];

export function Sidebar({
  page,
  onNavigate,
  onHome,
}: {
  page: PageKey;
  onNavigate: (key: PageKey) => void;
  onHome: () => void;
}) {
  return (
    <aside className="app-sidebar">
      <button type="button" className="nav-brand nav-brand-btn" onClick={onHome}>
        NOC
      </button>
      <nav style={{ display: "flex", flexDirection: "column", gap: "4px" }}>
        {NAV.map((item) => (
          <button
            key={item.key}
            type="button"
            className={`nav-item${page === item.key ? " active" : ""}`}
            onClick={() => onNavigate(item.key)}
            aria-current={page === item.key ? "page" : undefined}
          >
            <span>{item.label}</span>
          </button>
        ))}
      </nav>
    </aside>
  );
}
