const scoreDefinitions = [
  ["researchSystem", "Research system", "Current sources and controls"],
  ["gtmDesign", "GTM design", "Decision architecture"],
  ["realMarketEvidence", "Market evidence", "Observed customer truth"],
  ["safeExecutionReadiness", "Safe readiness", "Authority and risk gates"],
] as const;

export function ScoreGrid({ scores }: { scores: Record<(typeof scoreDefinitions)[number][0], number> }) {
  return (
    <section className="score-grid" aria-label="Four separate planning scores">
      {scoreDefinitions.map(([key, label, note]) => {
        const value = scores[key];
        return (
          <article key={key} className="score-card">
            <div className="score-topline">
              <span>{label}</span>
              <strong>{value.toFixed(1)}</strong>
            </div>
            <div className="score-track" aria-label={`${label}: ${value} out of 10`}>
              <span style={{ width: `${value * 10}%` }} />
            </div>
            <p>{note}</p>
          </article>
        );
      })}
    </section>
  );
}
