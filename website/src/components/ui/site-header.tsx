import { SealLink } from "@/components/motion/seal-link";
import { siteCopy } from "@/content/site";

export function SiteHeader(): React.JSX.Element {
  return (
    <header className="site-header">
      <div className="site-header-inner">
        <a className="wordmark" href="#top" aria-label="SheperD Preview home">
          {siteCopy.brand}
        </a>

        <nav className="desktop-navigation" aria-label="Primary navigation">
          {siteCopy.navigation.map((item) => (
            <a href={item.href} key={item.href}>
              {item.label}
            </a>
          ))}
        </nav>

        <SealLink className="header-cta" href="#review-requirements">
          {siteCopy.hero.cta}
        </SealLink>

        <details className="mobile-navigation">
          <summary>Menu</summary>
          <nav aria-label="Mobile navigation">
            {siteCopy.navigation.map((item) => (
              <a href={item.href} key={item.href}>
                {item.label}
              </a>
            ))}
          </nav>
        </details>
      </div>
    </header>
  );
}
