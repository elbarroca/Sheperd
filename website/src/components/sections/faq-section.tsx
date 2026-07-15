import { siteCopy } from "@/content/site";

export function FaqSection(): React.JSX.Element {
  return (
    <section className="section faq-section" aria-labelledby="faq-heading">
      <div className="section-heading">
        <h2 id="faq-heading">{siteCopy.faq.heading}</h2>
      </div>
      <div className="faq-grid">
        {siteCopy.faq.items.map((item) => (
          <details key={item.question}>
            <summary>{item.question}</summary>
            <p>{item.answer}</p>
          </details>
        ))}
      </div>
    </section>
  );
}
