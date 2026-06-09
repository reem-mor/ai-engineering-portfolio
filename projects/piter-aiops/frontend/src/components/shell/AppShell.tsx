import { useState } from "react";
import type { PageKey } from "@/types/api";
import { SessionProvider } from "@/context/session";
import { NavigationProvider } from "@/context/navigation";
import { DemoProvider, useDemo } from "@/context/demo";
import { ChatDockProvider } from "@/context/chat-dock";
import { ToastProvider } from "@/context/toast";
import { Sidebar } from "./Sidebar";
import { TopBar } from "./TopBar";
import { ChatDock } from "./ChatDock";
import { P1Modal } from "@/components/demo/P1Modal";
import { HomePage } from "@/pages/Home";
import { AnalyticsPage } from "@/pages/Analytics";
import { HistoryInvestigationsPage } from "@/pages/HistoryInvestigations";
import { AnalyzerPage } from "@/pages/Analyzer";
import { SystemPage } from "@/pages/System";
import { DemoGuidePage } from "@/pages/DemoGuide";

function PageView({ page }: { page: PageKey }) {
  switch (page) {
    case "home":
      return <HomePage />;
    case "analytics":
      return <AnalyticsPage />;
    case "history":
      return <HistoryInvestigationsPage />;
    case "analyzer":
      return <AnalyzerPage />;
    case "system":
      return <SystemPage />;
    case "guide":
      return <DemoGuidePage />;
    default:
      return <HomePage />;
  }
}

function ShellInner() {
  const [page, setPage] = useState<PageKey>("home");
  const { criticalMode } = useDemo();
  const goHome = () => setPage("home");

  return (
    <ChatDockProvider>
      <NavigationProvider navigate={setPage}>
        <div
          className={`app-shell${criticalMode ? " critical-mode" : ""}`}
          data-ui-version="demo-polish-v1"
        >
          <Sidebar page={page} onNavigate={setPage} onHome={goHome} />
          <div className="app-body">
            <TopBar />
            <div className="app-workspace">
              <main className="page-content">
                <PageView page={page} />
              </main>
              <ChatDock />
            </div>
          </div>
          <P1Modal />
        </div>
      </NavigationProvider>
    </ChatDockProvider>
  );
}

export function AppShell() {
  return (
    <SessionProvider>
      <ToastProvider>
        <DemoProvider>
          <ShellInner />
        </DemoProvider>
      </ToastProvider>
    </SessionProvider>
  );
}
