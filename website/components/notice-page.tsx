import { BrandLogo } from "./brand-logo";
import Head from "next/head";
import { SiteFooter } from "./site-footer";

interface NoticePageProps {
  eyebrow: string;
  title: string;
  summary: string;
  sections: ReadonlyArray<{
    heading: string;
    body: string;
  }>;
}

export function NoticePage({
  eyebrow,
  title,
  summary,
  sections,
}: NoticePageProps) {
  return (
    <div className="recovery-site">
      <Head><meta name="description" content={summary} /></Head>
      <a className="skip-link" href="#main-content">
        Skip to content
      </a>
      <header className="site-header">
        <nav className="container header-layout notice-nav" aria-label="Notice navigation">
          <BrandLogo />
          <a className="button button-secondary button-small" href="/">
            Back to site
          </a>
        </nav>
      </header>
      <main id="main-content" className="notice-main" tabIndex={-1}>
        <article className="container notice-article">
          <p className="eyebrow eyebrow-blue">{eyebrow}</p>
          <h1>{title}</h1>
          <p className="notice-summary">{summary}</p>
          <div className="notice-sections">
            {sections.map((section) => (
              <section key={section.heading}>
                <h2>{section.heading}</h2>
                <p>{section.body}</p>
              </section>
            ))}
          </div>
        </article>
      </main>
      <SiteFooter />
    </div>
  );
}
