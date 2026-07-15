import { summarizeEvidence } from "@/lib/evidence";

export function EvidenceTide({ counts }: { counts: Record<string, number> }) {
  const summary = summarizeEvidence(counts);

  return (
    <section className="tide-card" aria-labelledby="evidence-mix-title">
      <div className="section-heading compact-heading">
        <div>
          <p className="eyebrow">Evidence mix</p>
          <h2 id="evidence-mix-title">What the brief can actually support</h2>
        </div>
        <span className="metric-id">{summary.total} sources</span>
      </div>
      {summary.total === 0 ? (
        <p className="empty-state">No admitted sources are available yet.</p>
      ) : (
        <>
          <div className="tide-line" aria-hidden="true">
            {summary.rows.map((row) => row.count > 0 ? (
              <span key={row.state} className={`tide-segment state-${row.state}`} style={{ width: `${row.percentage}%` }} />
            ) : null)}
          </div>
          <div className="evidence-table" role="table" aria-label="Evidence states by count and percentage">
            {summary.rows.map((row) => (
              <div key={row.state} className="legend-item" role="row">
                <span className={`legend-swatch state-${row.state}`} aria-hidden="true" />
                <span role="cell">{row.state.replaceAll("-", " ")}</span>
                <strong role="cell">{row.count}</strong>
                <span role="cell">{Math.round(row.percentage)}%</span>
              </div>
            ))}
          </div>
        </>
      )}
    </section>
  );
}
