"use client";

import { List, X } from "@phosphor-icons/react";
import { AnimatePresence, m } from "motion/react";
import { useEffect, useState } from "react";

import { navigationItems } from "@/lib/content";

import { BrandLogo } from "./brand-logo";

const MOBILE_MENU_EXIT_MS = 260;

export function SiteHeader() {
  const [isOpen, setIsOpen] = useState(false);

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
            <a href={item.href} key={item.href}>
              {item.label}
            </a>
          ))}
        </div>

        <a className="button button-small header-audit" href="#audit-form">
          Free Invoice Audit
        </a>

        <div className="mobile-header-actions">
          <a className="mobile-audit-link" href="#audit-form">
            Free audit
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
                  href={item.href}
                  key={item.href}
                  onClick={(event) => {
                    event.preventDefault();
                    followMobileLink(item.href);
                  }}
                >
                  {item.label}
                </a>
              ))}
              <a
                className="button"
                href="#audit-form"
                onClick={(event) => {
                  event.preventDefault();
                  followMobileLink("#audit-form");
                }}
              >
                Get a Free Invoice Audit
              </a>
            </div>
          </m.div>
        ) : null}
      </AnimatePresence>
    </header>
  );
}
