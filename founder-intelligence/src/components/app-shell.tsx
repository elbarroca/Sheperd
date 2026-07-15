import type { ReactNode } from "react";
import Image from "next/image";
import Link from "next/link";
import { Navigation } from "./navigation";

export function AppShell({ children }: { children: ReactNode }) {
  return (
    <div className="app-shell">
      <a className="skip-link" href="#main-content">Skip to content</a>
      <header className="topbar">
        <div className="topbar-inner">
          <Link className="brand-lockup" href="/" aria-label="SheperD founder intelligence home">
            <Image src="/icon.svg" alt="" width={36} height={36} priority />
            <div>
              <p className="brand-name">SheperD</p>
              <p className="brand-product">Founder intelligence</p>
            </div>
          </Link>
          <Navigation />
          <div className="hold-card" role="status">
            <span className="hold-light" aria-hidden="true" />
            <div><strong>External hold</strong><span>D0 / D1 only</span></div>
          </div>
        </div>
      </header>
      <main id="main-content" className="main-content">
        <div className="content-frame">{children}</div>
        <footer className="dashboard-footer">
          <span>SheperD founder intelligence</span>
          <span>Private research workspace</span>
          <span>Evidence snapshot: 2026-07-15</span>
        </footer>
      </main>
    </div>
  );
}
