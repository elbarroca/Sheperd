import type { Metadata } from "next";

import { legalCopy } from "@/content/legal";

export const metadata: Metadata = {
  title: legalCopy.privacy.title,
  description: "Mechanically verified application behavior for the SheperD Preview.",
};

export default function PrivacyPage(): React.JSX.Element {
  return (
    <main className="notice-page" id="main-content">
      <p className="eyebrow">Preview notice</p>
      <h1>{legalCopy.privacy.title}</h1>
      <p className="notice-intro">{legalCopy.privacy.intro}</p>
      <div className="notice-sections">
        {legalCopy.privacy.sections.map((section) => (
          <section key={section.heading}>
            <h2>{section.heading}</h2>
            <p>{section.body}</p>
          </section>
        ))}
      </div>
    </main>
  );
}
