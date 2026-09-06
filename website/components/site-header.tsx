"use client";

import { List } from "@phosphor-icons/react";
import { useRef } from "react";
import { useRouter } from "next/router";

import { navigationItems } from "@/lib/content";
import { BrandLogo } from "./brand-logo";
import { PilotLink } from "./pilot-link";

export function SiteHeader() {
  const { pathname } = useRouter();
  const menuRef = useRef<HTMLDetailsElement>(null);
  const anchorHref = (href: string): string => pathname === "/" ? href : "/" + href;
  function closeMenu(): void {
    if (menuRef.current) menuRef.current.open = false;
  }

  return (
    <header className="site-header">
      <nav className="container header-layout" aria-label="Primary navigation">
        <BrandLogo />
        <div className="header-links">
          {navigationItems.map((item) => <a href={anchorHref(item.href)} key={item.href}>{item.label}</a>)}
        </div>
        <div className="header-actions">
          <PilotLink className="button button-small header-pilot" onClick={closeMenu}>Request a pilot</PilotLink>
          <details className="mobile-menu" ref={menuRef} onKeyDown={(event) => {
            if (event.key === "Escape") {
              closeMenu();
              menuRef.current?.querySelector("summary")?.focus();
            }
          }}>
            <summary aria-label="Navigation menu"><List aria-hidden="true" size={24} /></summary>
            <div className="mobile-navigation">
              {navigationItems.map((item) => (
                <a href={anchorHref(item.href)} key={item.href} onClick={closeMenu}>{item.label}</a>
              ))}
            </div>
          </details>
        </div>
      </nav>
    </header>
  );
}
