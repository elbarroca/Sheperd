import { ArrowRight, LinkedinLogo } from "@phosphor-icons/react";

import { liveSource, navigationItems } from "@/lib/content";

import { BrandLogo } from "./brand-logo";

export function SiteFooter() {
  return (
    <footer id="site-footer" className="site-footer">
      <div className="container footer-main">
        <div className="footer-overview">
          <BrandLogo compact />
          <p>
            SheperD makes shipping-container charge recovery a visible,
            repeatable part of import operations—from invoice review to refund.
          </p>
          <a className="footer-cta" href="/#audit-form">
            Start a free invoice audit
            <ArrowRight aria-hidden="true" size={18} />
          </a>
        </div>

        <div className="footer-column">
          <p className="footer-heading">Explore</p>
          <nav className="footer-links" aria-label="Footer navigation">
            {navigationItems.map((item) => (
              <a href={`/${item.href}`} key={item.href}>
                {item.label}
              </a>
            ))}
          </nav>
        </div>

        <div className="footer-column footer-contact">
          <p className="footer-heading">Contact</p>
          <a href={`mailto:${liveSource.contactEmail}`}>
            {liveSource.contactEmail}
          </a>
          <a
            href={liveSource.linkedin}
            target="_blank"
            rel="noopener noreferrer"
          >
            <LinkedinLogo aria-hidden="true" size={20} weight="fill" />
            LinkedIn
          </a>
        </div>
      </div>

      <div className="container footer-bottom">
        <span>© 2026 SheperD.IO, Inc.</span>
        <nav aria-label="Legal links">
          <a href="/privacy">Privacy Policy</a>
          <a href="/terms">Use Notice</a>
        </nav>
      </div>
    </footer>
  );
}
