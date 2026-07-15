import type { ReactNode } from "react";
import Image from "next/image";
import Link from "next/link";
import { SHEPERD_BRAND } from "@/lib/brand";
import { Navigation } from "./navigation";

export function AppShell({ children }: { children: ReactNode }) {
  return (
    <div className="app-shell">
      <a className="skip-link" href="#main-content">Skip to content</a>
      <header className="topbar">
        <div className="topbar-inner">
          <Link className="brand-lockup" href="/" aria-label={`${SHEPERD_BRAND.name} founder intelligence home`}>
            <Image className="brand-mark" src={SHEPERD_BRAND.logo.path} alt="" width={47} height={36} priority />
            <div>
              <p className="brand-name">{SHEPERD_BRAND.name}</p>
              <p className="brand-product">Founder intelligence</p>
            </div>
          </Link>
          <Navigation />
          <div className="hold-card" role="status">
            <span className="hold-light" aria-hidden="true" />
            <div><strong>External hold</strong><span>Research only</span></div>
          </div>
        </div>
      </header>
      <main id="main-content" className="main-content">
        <div className="content-frame">{children}</div>
        <footer className="dashboard-footer">
          <span className="footer-brand-source">
            <strong>{SHEPERD_BRAND.name} founder intelligence</strong>
            <a href={SHEPERD_BRAND.publicSite} target="_blank" rel="noreferrer">Public brand source</a>
          </span>
          <span>Public read-only research brief</span>
          <span>Evidence snapshot: 2026-07-15</span>
        </footer>
      </main>
    </div>
  );
}
