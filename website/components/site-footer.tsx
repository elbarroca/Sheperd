import { ArrowUpRight } from "@phosphor-icons/react";

import { navigationItems, sourceLinks } from "@/lib/content";
import { BrandLogo } from "./brand-logo";
import { PilotLink } from "./pilot-link";

export function SiteFooter() {
  return (
    <footer id="site-footer" className="site-footer">
      <div className="container footer-main">
        <div className="footer-overview">
          <BrandLogo compact />
          <p>A clearer record.<br />A more informed next step.</p>
          <PilotLink className="text-link">Request a pilot <ArrowUpRight aria-hidden="true" size={16} /></PilotLink>
        </div>
        <div className="footer-column">
          <p className="footer-heading">Explore</p>
          <nav className="footer-links" aria-label="Footer navigation">
            {navigationItems.map((item) => <a href={"/" + item.href} key={item.href}>{item.label}</a>)}
          </nav>
        </div>
        <div className="footer-column">
          <p className="footer-heading">Original sources</p>
          <nav className="footer-links" aria-label="Official sources">
            {sourceLinks.map((source) => (
              <a href={source.href} key={source.title} target="_blank" rel="noopener noreferrer">
                {source.issuer}<ArrowUpRight aria-hidden="true" size={13} />
              </a>
            ))}
          </nav>
        </div>
      </div>
      <div className="container footer-bottom">
        <span>SheperD. Case-specific review. No guaranteed recovery.</span>
        <nav aria-label="Legal links"><a href="/privacy">Privacy notice</a><a href="/terms">Use notice</a></nav>
      </div>
    </footer>
  );
}
