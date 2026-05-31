import { MessageSquare, Activity, LayoutDashboard, Network } from "lucide-react";
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
            onClick={() => scrollToSection("live-kb")}
          >
            <MessageSquare className="size-3.5 text-[var(--tools)]" />
            Ask incident questions
          </button>
          <button type="button" className={navBtn} onClick={() => scrollToSection("mvp")}>
            <Activity className="size-3.5 text-[var(--interface)]" />
            Triage workflow
          </button>
          <button
            type="button"
            className={navBtn}
            onClick={() => {
              scrollToSection("demo-dashboard");
              startDemoTour();
            }}
          >
            <LayoutDashboard className="size-3.5 text-[var(--agent)]" />
            Demo &amp; Dashboard
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
            impact saved
          </span>
          <span>{totalSavedMin} min MTTR avoided</span>
          <span>{triageCount} triage{triageCount === 1 ? "" : "s"}</span>
          {lastTriageAt && (
            <span className="hidden sm:inline">Last: {lastTriageAt}</span>
          )}
        </div>
      </div>
    </header>
  );
}
