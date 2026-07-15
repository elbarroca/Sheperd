import { siteCopy } from "@/content/site";

export function LimitsSection(): React.JSX.Element {
  return (
    <section className="section limits-section" id="limits" aria-labelledby="limits-heading">
      <h2 id="limits-heading">{siteCopy.limits.heading}</h2>
      <div className="limits-grid">
        {siteCopy.limits.items.map((item) => (
          <div key={item.title}>
            <h3>{item.title}</h3>
            <p>{item.text}</p>
          </div>
        ))}
      </div>
    </section>
  );
}
