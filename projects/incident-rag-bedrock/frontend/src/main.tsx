import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import App from "./App";
import { BootstrapProvider } from "@/context/bootstrap";
import "./styles.css";

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <BootstrapProvider>
      <App />
    </BootstrapProvider>
  </StrictMode>,
);
