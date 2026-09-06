import { ArrowUpRight } from "@phosphor-icons/react";

import { liveSource, navigationItems } from "@/lib/content";
import { BrandLogo } from "./brand-logo";
import { PilotLink } from "./pilot-link";

export function SiteFooter() {
  return (
    <footer id="site-footer" className="site-footer">
      <div className="container footer-main">
        <div className="footer-overview">
          <BrandLogo compact />
          <p>{liveSource.description}</p>
          <PilotLink className="text-link">Request a pilot <ArrowUpRight aria-hidden="true" size={16} /></PilotLink>
        </div>
        <div className="footer-column">
          <p className="footer-heading">Explore</p>
          <nav className="footer-links" aria-label="Footer navigation">
            {navigationItems.map((item) => <a href={"/" + item.href} key={item.href}>{item.label}</a>)}
          </nav>
        </div>
        <div className="footer-column">
          <p className="footer-heading">Contact SheperD</p>
          <nav className="footer-links" aria-label="Contact SheperD">
            <a href={`mailto:${liveSource.contactEmail}`}>{liveSource.contactEmail}</a>
            <a href={`tel:${liveSource.contactPhone}`}>{liveSource.contactPhoneLabel}</a>
            <a href={liveSource.url} target="_blank" rel="noopener noreferrer">
              sheperd.io<ArrowUpRight aria-hidden="true" size={13} />
            </a>
          </nav>
        </div>
      </div>
      <div className="container footer-bottom">
        <span>SheperD · D&amp;D services for U.S. importers.</span>
        <nav aria-label="Legal links"><a href="/privacy">Privacy notice</a><a href="/terms">Use notice</a></nav>
      </div>
    </footer>
  );
}
