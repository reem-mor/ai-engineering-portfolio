import {
  Activity,
  BookOpen,
  ClipboardList,
  LayoutDashboard,
  LineChart,
  Server,
  Sparkles,
} from "lucide-react";
import type { PageKey } from "@/types/api";

type NavItem = { key: PageKey; label: string; icon: typeof LayoutDashboard };

const OPS: NavItem[] = [
  { key: "home", label: "Operations", icon: LayoutDashboard },
  { key: "analyzer", label: "Analyzer", icon: Activity },
];

const INTEL: NavItem[] = [
  { key: "analytics", label: "Agent Analytics", icon: LineChart },
  { key: "history", label: "History", icon: ClipboardList },
];

const PLATFORM: NavItem[] = [
  { key: "system", label: "System & KB", icon: Server },
  { key: "guide", label: "Demo Guide", icon: BookOpen },
];

function NavButton({
  item,
  active,
  onNavigate,
}: {
  item: NavItem;
  active: boolean;
  onNavigate: (key: PageKey) => void;
}) {
  const Icon = item.icon;
  return (
    <button
      type="button"
      className={`nav-item${active ? " active" : ""}`}
      onClick={() => onNavigate(item.key)}
      aria-current={active ? "page" : undefined}
    >
      <Icon className="nav-item-icon" aria-hidden />
      <span>{item.label}</span>
    </button>
  );
}

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
        <Sparkles className="nav-item-icon" aria-hidden />
        <span>PITER NOC</span>
      </button>
      <nav style={{ display: "flex", flexDirection: "column", gap: "4px" }}>
        <div className="nav-section-label">Operations</div>
        {OPS.map((item) => (
          <NavButton key={item.key} item={item} active={page === item.key} onNavigate={onNavigate} />
        ))}
        <div className="nav-section-label">Intelligence</div>
        {INTEL.map((item) => (
          <NavButton key={item.key} item={item} active={page === item.key} onNavigate={onNavigate} />
        ))}
        <div className="nav-section-label">Platform</div>
        {PLATFORM.map((item) => (
          <NavButton key={item.key} item={item} active={page === item.key} onNavigate={onNavigate} />
        ))}
      </nav>
    </aside>
  );
}
