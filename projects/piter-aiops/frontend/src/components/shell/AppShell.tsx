import { useState } from "react";
import type { PageKey } from "@/types/api";
import { SessionProvider } from "@/context/session";
import { NavigationProvider } from "@/context/navigation";
import { DemoProvider } from "@/context/demo";
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
    default:
      return <HomePage />;
  }
}

export function AppShell() {
  const [page, setPage] = useState<PageKey>("home");
  const goHome = () => setPage("home");

  return (
    <SessionProvider>
      <ToastProvider>
        <DemoProvider>
          <ChatDockProvider>
            <NavigationProvider navigate={setPage}>
              <div className="app-shell">
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
        </DemoProvider>
      </ToastProvider>
    </SessionProvider>
  );
}
