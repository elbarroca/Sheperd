const scoreDefinitions = [
  ["researchSystem", "Research system", "Current sources and controls"],
  ["gtmDesign", "GTM design", "Decision architecture"],
  ["realMarketEvidence", "Market evidence", "Observed customer truth"],
  ["safeExecutionReadiness", "Safe readiness", "Authority and risk gates"],
] as const;

function getBand(value: number): string {
  if (value < 3) return "Early evidence";
  if (value < 5) return "Blocked";
  if (value < 8) return "Developing";
  return "Strong";
}

export function ScoreGrid({ scores }: { scores: Record<(typeof scoreDefinitions)[number][0], number> }) {
  return (
    <section className="score-grid" aria-label="Four separate planning scores">
      {scoreDefinitions.map(([key, label, note]) => {
        const value = scores[key];
        const rounded = Math.round(value);
        return (
          <article key={key} className="score-card">
            <div className="score-topline">
              <div><span>{label}</span><small>{getBand(value)}</small></div>
              <strong>{rounded}<span>/10</span></strong>
            </div>
            <meter min="0" max="10" value={value} aria-label={`${label}: ${value} out of 10`} />
            <p>{note}</p>
          </article>
        );
      })}
      <details className="score-method">
        <summary>How to read these scores</summary>
        <p>Scores are planning heuristics rounded for scanning. They do not measure probability, ROI, or approval. Observed counts and named gates remain the decision evidence.</p>
      </details>
    </section>
  );
}
