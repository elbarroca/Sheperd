import type { ReactNode } from "react";
import { Navigation } from "./navigation";

export function AppShell({ children }: { children: ReactNode }) {
  return (
    <div className="app-shell">
      <a className="skip-link" href="#main-content">Skip to content</a>
      <aside className="sidebar">
        <div className="brand-lockup">
          <span className="brand-signal" aria-hidden="true" />
          <div>
            <p className="brand-name">SheperD</p>
            <p className="brand-product">Founder intelligence</p>
          </div>
        </div>
        <div className="hold-card" role="status">
          <span className="hold-light" aria-hidden="true" />
          <div>
            <strong>External hold</strong>
            <span>Research-only · D0/D1</span>
          </div>
        </div>
        <Navigation />
        <div className="sidebar-foot">
          <span>Briefing build</span>
          <strong>2026.07.15</strong>
          <span>No external connectors</span>
        </div>
      </aside>
      <main id="main-content" className="main-content">{children}</main>
    </div>
  );
}
