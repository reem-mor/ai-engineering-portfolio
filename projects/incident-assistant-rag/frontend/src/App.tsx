import { useState } from "react";
import { AppLayout } from "./components/layout/AppLayout";
import { Sidebar } from "./components/layout/Sidebar";
import { ChatPage } from "./pages/ChatPage";
import { DashboardPage } from "./pages/DashboardPage";
import { IncidentAnalyzePage } from "./pages/IncidentAnalyzePage";
import { KnowledgeBasePage } from "./pages/KnowledgeBasePage";
import { UploadPage } from "./pages/UploadPage";

const navItems = [
  { id: "dashboard", label: "Dashboard" },
  { id: "knowledge", label: "Knowledge Base" },
  { id: "chat", label: "RAG Chat" },
  { id: "incident", label: "Incident Analysis" },
  { id: "upload", label: "Upload" },
];

function renderPage(activeId: string, go: (id: string) => void) {
  switch (activeId) {
    case "dashboard":
      return <DashboardPage onNavigate={go} />;
    case "chat":
      return <ChatPage />;
    case "incident":
      return <IncidentAnalyzePage />;
    case "upload":
      return <UploadPage />;
    case "knowledge":
      return <KnowledgeBasePage />;
    default:
      return <DashboardPage onNavigate={go} />;
  }
}

export default function App() {
  const [activePage, setActivePage] = useState("dashboard");
  const go = (id: string) => setActivePage(id);

  return (
    <AppLayout
      sidebar={<Sidebar items={navItems} activeId={activePage} onSelect={go} />}
    >
      {renderPage(activePage, go)}
    </AppLayout>
  );
}
