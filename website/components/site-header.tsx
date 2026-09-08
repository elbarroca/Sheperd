"use client";

import { List, X } from "@phosphor-icons/react";
import { AnimatePresence, m } from "motion/react";
import { useEffect, useState } from "react";
import { usePathname } from "next/navigation";

import { navigationItems } from "@/lib/content";
import { recoveryCta } from "@/lib/recovery-content";

import { BrandLogo } from "./brand-logo";

const MOBILE_MENU_EXIT_MS = 260;

export function SiteHeader() {
  const [isOpen, setIsOpen] = useState(false);
  const pathname = usePathname();

  const anchorHref = (href: string) =>
    href.startsWith("#") && pathname !== "/" ? `/${href}` : href;

  useEffect(() => {
    if (!isOpen) return undefined;

    function closeOnEscape(event: KeyboardEvent) {
      if (event.key === "Escape") setIsOpen(false);
    }

    window.addEventListener("keydown", closeOnEscape);
    return () => window.removeEventListener("keydown", closeOnEscape);
  }, [isOpen]);

  function followMobileLink(href: string) {
    setIsOpen(false);

    if (href.startsWith("/")) {
      window.location.assign(href);
      return;
    }

    window.history.replaceState(null, "", href);
    window.setTimeout(() => {
      document.querySelector(href)?.scrollIntoView({
        behavior: window.matchMedia("(prefers-reduced-motion: reduce)").matches
          ? "auto"
          : "smooth",
        block: "start",
      });
    }, MOBILE_MENU_EXIT_MS);
  }

  return (
    <header className="site-header">
      <nav className="container header-layout" aria-label="Primary navigation">
        <BrandLogo />

        <div className="header-links">
          {navigationItems.map((item) => (
            <a href={anchorHref(item.href)} key={item.href}>
              {item.label}
            </a>
          ))}
        </div>

        <a className="button button-small header-audit" href="/pilot">
          {recoveryCta}
        </a>

        <div className="mobile-header-actions">
          <a className="mobile-audit-link" href="/pilot">
            {recoveryCta}
          </a>
          <button
            className="mobile-nav-toggle"
            type="button"
            aria-expanded={isOpen}
            aria-controls="mobile-navigation"
            aria-label={isOpen ? "Close navigation" : "Open navigation"}
            onClick={() => setIsOpen((current) => !current)}
          >
            {isOpen ? (
              <X aria-hidden="true" size={22} />
            ) : (
              <List aria-hidden="true" size={23} />
            )}
          </button>
        </div>
      </nav>

      <AnimatePresence initial={false}>
        {isOpen ? (
          <m.div
            id="mobile-navigation"
            className="mobile-navigation"
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.24, ease: [0.22, 1, 0.36, 1] }}
          >
            <div className="container mobile-navigation-inner">
              {navigationItems.map((item) => (
                <a
                  href={anchorHref(item.href)}
                  key={item.href}
                  onClick={(event) => {
                    event.preventDefault();
                    followMobileLink(anchorHref(item.href));
                  }}
                >
                  {item.label}
                </a>
              ))}
              <a
                className="button"
                href="/pilot"
                onClick={(event) => {
                  event.preventDefault();
                  followMobileLink("/pilot");
                }}
              >
                {recoveryCta}
              </a>
            </div>
          </m.div>
        ) : null}
      </AnimatePresence>
    </header>
  );
}
