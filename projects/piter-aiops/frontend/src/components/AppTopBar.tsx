import {
  MessageSquare,
  Activity,
  LayoutDashboard,
  Network,
  Target,
  Search,
  ShieldCheck,
  ArrowUpRight,
  CheckCircle2,
  History,
} from "lucide-react";
import { scrollToSection } from "@/lib/workflow-utils";
import { useDemoTour } from "@/context/demo-tour";

type AppTopBarProps = {
  totalSavedDollars: number;
  totalSavedMin: number;
  triageCount: number;
  lastTriageAt: string | null;
};

export function AppTopBar({
  totalSavedDollars,
  totalSavedMin,
  triageCount,
  lastTriageAt,
}: AppTopBarProps) {
  const { startDemoTour } = useDemoTour();

  const navBtn =
    "inline-flex items-center gap-1.5 rounded-md border border-border bg-card/80 px-2.5 py-1.5 text-xs font-medium hover:bg-card transition";

  return (
    <header className="sticky top-0 z-50 border-b border-border bg-background/90 backdrop-blur-md">
      <div className="mx-auto flex max-w-6xl flex-wrap items-center justify-between gap-3 px-4 py-2.5 md:px-6">
        <nav className="flex flex-wrap items-center gap-2">
          <button
            type="button"
            className={navBtn}
            onClick={() => scrollToSection("priority-center")}
          >
            <Target className="size-3.5 text-[var(--destructive)]" />
            Priority Center
          </button>
          <button type="button" className={navBtn} onClick={() => scrollToSection("investigation")}>
            <Search className="size-3.5 text-[var(--rag)]" />
            Investigation
          </button>
          <button type="button" className={navBtn} onClick={() => scrollToSection("triage-plan")}>
            <Activity className="size-3.5 text-[var(--interface)]" />
            Triage Plan
          </button>
          <button type="button" className={navBtn} onClick={() => scrollToSection("escalation")}>
            <ArrowUpRight className="size-3.5 text-[var(--agent)]" />
            Escalation Hub
          </button>
          <button type="button" className={navBtn} onClick={() => scrollToSection("resolution")}>
            <CheckCircle2 className="size-3.5 text-[var(--resolution)]" />
            Resolution
          </button>
          <button
            type="button"
            className={navBtn}
            onClick={() => {
              scrollToSection("agent-analytics");
              startDemoTour();
            }}
          >
            <LayoutDashboard className="size-3.5 text-[var(--tools)]" />
            Agent Analytics
          </button>
          <button type="button" className={navBtn} onClick={() => scrollToSection("live-kb")}>
            <MessageSquare className="size-3.5 text-[var(--tools)]" />
            Knowledge Base
          </button>
          <button type="button" className={navBtn} onClick={() => scrollToSection("incident-history")}>
            <History className="size-3.5 text-[var(--ingest)]" />
            History
          </button>
          <button
            type="button"
            className={navBtn}
            onClick={() => scrollToSection("architecture")}
          >
            <Network className="size-3.5 text-[var(--rag)]" />
            Architecture
          </button>
        </nav>

        <div className="flex flex-wrap items-center gap-3 text-xs text-muted-foreground">
          <span>
            <span className="font-semibold text-[var(--resolution)]">
              ${totalSavedDollars.toLocaleString()}
            </span>{" "}
            cost avoided
          </span>
          <span>{totalSavedMin} min MTTR reduced</span>
          <span>{triageCount} incident{triageCount === 1 ? "" : "s"}</span>
          {lastTriageAt && (
            <span className="hidden sm:inline">Last: {lastTriageAt}</span>
          )}
        </div>
      </div>
    </header>
  );
}
