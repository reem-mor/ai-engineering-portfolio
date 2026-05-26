import type { ReactNode } from "react";

export type AppLayoutProps = {
  sidebar: ReactNode;
  children: ReactNode;
};

export function AppLayout({ sidebar, children }: AppLayoutProps) {
  return (
    <div className="app-shell">
      <div className="app-shell__sidebar">{sidebar}</div>
      <main className="app-shell__main">
        <div className="app-shell__content">{children}</div>
      </main>
    </div>
  );
}
