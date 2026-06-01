/**
 * TanStack Router file route — production build uses main.tsx → App.tsx directly.
 * Kept so routeTree.gen.ts stays valid; no duplicate mock workflow here.
 */
import { createFileRoute } from "@tanstack/react-router";
import App from "@/App";

export const Route = createFileRoute("/")({
  component: App,
});
