import type { Metadata } from "next";

import { legalCopy } from "@/content/legal";

export const metadata: Metadata = {
  title: legalCopy.terms.title,
  description: "Temporary use conditions for reviewing the SheperD Preview.",
};

export default function TermsPage(): React.JSX.Element {
  return (
    <main className="notice-page" id="main-content">
      <p className="eyebrow">Preview notice</p>
      <h1>{legalCopy.terms.title}</h1>
      <p className="notice-intro">{legalCopy.terms.intro}</p>
      <div className="notice-sections">
        {legalCopy.terms.sections.map((section) => (
          <section key={section.heading}>
            <h2>{section.heading}</h2>
            <p>{section.body}</p>
          </section>
        ))}
      </div>
    </main>
  );
}
