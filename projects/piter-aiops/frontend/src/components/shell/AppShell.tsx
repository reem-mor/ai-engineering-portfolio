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
import { KnowledgeBasePage } from "@/pages/KnowledgeBasePage";
import { BedrockStatusPage } from "@/pages/BedrockStatusPage";
import { PostMortemsPage } from "@/pages/PostMortemsPage";
import { useChatDock } from "@/context/chat-dock";

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
    case "knowledge":
      return <KnowledgeBasePage />;
    case "bedrock":
      return <BedrockStatusPage />;
    case "postmortems":
      return <PostMortemsPage />;
    case "system":
      return <SystemPage />;
    case "guide":
      return <DemoGuidePage />;
    default:
      return <HomePage />;
  }
}

function ShellLayout() {
  const [page, setPage] = useState<PageKey>("home");
  const { criticalMode } = useDemo();
  const { setMode } = useChatDock();
  const goHome = () => setPage("home");
  const openChat = () => setMode("open");

  return (
    <NavigationProvider navigate={setPage}>
      <div
        className={`app-shell${criticalMode ? " critical-mode" : ""}`}
        data-ui-version="demo-polish-v4"
      >
        <Sidebar page={page} onNavigate={setPage} onHome={goHome} onOpenChat={openChat} />
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
  );
}

function ShellInner() {
  return (
    <ChatDockProvider>
      <ShellLayout />
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
