const order = ["verified", "mixed", "company-claim", "internal-proposal", "internal-observation", "unverified"];

export function EvidenceTide({ counts }: { counts: Record<string, number> }) {
  const total = Object.values(counts).reduce((sum, value) => sum + value, 0) || 1;
  return (
    <section className="tide-card" aria-labelledby="evidence-tide-title">
      <div className="section-heading compact-heading">
        <div>
          <p className="eyebrow">Evidence tide line</p>
          <h2 id="evidence-tide-title">What the current brief is made of</h2>
        </div>
        <span className="metric-id">{total} sources</span>
      </div>
      <div className="tide-line" role="img" aria-label={order.map((state) => `${state}: ${counts[state] ?? 0}`).join(", ")}>
        {order.map((state) => {
          const count = counts[state] ?? 0;
          return count ? <span key={state} className={`tide-segment state-${state}`} style={{ width: `${(count / total) * 100}%` }} /> : null;
        })}
      </div>
      <div className="tide-legend">
        {order.map((state) => (
          <div key={state} className="legend-item">
            <span className={`legend-swatch state-${state}`} aria-hidden="true" />
            <span>{state.replaceAll("-", " ")}</span>
            <strong>{counts[state] ?? 0}</strong>
          </div>
        ))}
      </div>
    </section>
  );
}
