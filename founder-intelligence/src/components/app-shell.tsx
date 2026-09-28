import Link from "next/link";
import type { ReactNode } from "react";
import { SHEPERD_BRAND } from "@/lib/brand";

export function AppShell({ children }: { children: ReactNode }): ReactNode {
  return (
    <div className="app-shell">
      <a className="skip-link" href="#main-content">Skip to content</a>
      <header className="topbar">
        <div className="topbar-inner">
          <Link className="brand-lockup" href="/" aria-label={`${SHEPERD_BRAND.name} research home`}>
            <span className="brand-mark" aria-hidden="true">S</span>
            <span>
              <strong>{SHEPERD_BRAND.name}</strong>
              <small>Research desk</small>
            </span>
          </Link>
          <nav className="top-nav" aria-label="Research sections">
            <Link href="/">Briefs</Link>
            <Link href="/sources">Sources</Link>
            <Link href="/monthly">Monthly</Link>
            <Link href="/how-it-works">How it works</Link>
          </nav>
          <span className="read-only-badge">Read-only</span>
        </div>
      </header>
      <main id="main-content" className="main-content"><div className="content-frame">{children}</div></main>
      <footer className="dashboard-footer"><span>{SHEPERD_BRAND.name} research agents</span><span>Human review required before approval or export</span></footer>
    </div>
  );
}
