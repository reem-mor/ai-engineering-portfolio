import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import App from "./App";
import { BootstrapProvider } from "@/context/bootstrap";
import { DemoTourProvider } from "@/context/demo-tour";
import { WorkflowSessionProvider } from "@/context/workflow-session";
import "./styles.css";

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <BootstrapProvider>
      <DemoTourProvider>
        <WorkflowSessionProvider>
          <App />
        </WorkflowSessionProvider>
      </DemoTourProvider>
    </BootstrapProvider>
  </StrictMode>,
);
