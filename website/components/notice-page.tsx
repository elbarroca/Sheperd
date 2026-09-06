import { SiteHeader } from "./site-header";
import { SiteFooter } from "./site-footer";

interface NoticePageProps {
  eyebrow: string;
  title: string;
  summary: string;
  sections: ReadonlyArray<{ heading: string; body: string }>;
}

export function NoticePage({ eyebrow, title, summary, sections }: NoticePageProps) {
  return (
    <>
      <a className="skip-link" href="#main-content">Skip to content</a>
      <SiteHeader />
      <main id="main-content" className="notice-main section-paper" tabIndex={-1}>
        <article className="container notice-article">
          <p className="eyebrow">{eyebrow}</p>
          <h1>{title}</h1>
          <p className="notice-summary">{summary}</p>
          <div className="notice-sections">
            {sections.map((section) => (
              <section key={section.heading}><h2>{section.heading}</h2><p>{section.body}</p></section>
            ))}
          </div>
          <a className="text-link" href="/">Back to the website</a>
        </article>
      </main>
      <SiteFooter />
    </>
  );
}
