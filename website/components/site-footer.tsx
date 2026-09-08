import { ArrowRight, ArrowUpRight } from "@phosphor-icons/react";

import { navigationItems, sourceLinks } from "@/lib/content";
import { recoveryCta } from "@/lib/recovery-content";

import { BrandLogo } from "./brand-logo";

export function SiteFooter() {
  return (
    <footer id="site-footer" className="site-footer">
      <div className="container footer-main">
        <div className="footer-overview">
          <BrandLogo compact />
          <p>
            You send the invoices. We handle the recovery.
          </p>
          <a className="footer-cta" href="/pilot">
            {recoveryCta}
            <ArrowRight aria-hidden="true" size={18} />
          </a>
        </div>

        <div className="footer-column">
          <p className="footer-heading">Explore</p>
          <nav className="footer-links" aria-label="Footer navigation">
            {navigationItems.map((item) => (
              <a href={item.href} key={item.href}>
                {item.label}
              </a>
            ))}
          </nav>
        </div>

        <div className="footer-column footer-contact">
          <p className="footer-heading">Contact</p>
          <a href="/pilot">
            Start a recovery enquiry
            <ArrowUpRight aria-hidden="true" size={16} />
          </a>
          <span className="footer-muted">Detention &amp; demurrage recovery for importers</span>
        </div>

        <div className="footer-column">
          <p className="footer-heading">Sources</p>
          <nav className="footer-links" aria-label="Official sources">
            {sourceLinks.slice(0, 2).map((source) => (
              <a
                href={source.href}
                key={source.title}
                target="_blank"
                rel="noopener noreferrer"
              >
                {source.issuer}
                <ArrowUpRight aria-hidden="true" size={16} />
              </a>
            ))}
          </nav>
        </div>
      </div>

      <div className="container footer-bottom">
        <span>SheperD. Outcomes depend on the facts of individual charges and claims.</span>
        <nav aria-label="Legal links">
          <a href="/privacy">Privacy Policy</a>
          <a href="/terms">Use Notice</a>
        </nav>
      </div>
    </footer>
  );
}
