const steps = [
  { label: "Source", detail: "Original research and company material" },
  { label: "Evidence status", detail: "Verified, mixed, claimed, or unknown" },
  { label: "Ricardo analysis", detail: "Interpretation with limits visible" },
  { label: "Founder decision", detail: "Named owner records go or no-go" },
  { label: "Allowed action", detail: "Prepare, test internally, or activate" },
] as const;

export function DecisionFlow() {
  return (
    <section className="decision-flow section-block" aria-labelledby="decision-flow-title">
      <div className="section-heading compact-heading">
        <div>
          <p className="eyebrow">Decision flow</p>
          <h2 id="decision-flow-title">Nothing moves from research to action silently</h2>
        </div>
        <p>Every step keeps its source, owner, and boundary.</p>
      </div>
      <ol className="flow-steps">
        {steps.map((step, index) => (
          <li key={step.label}>
            <span>{String(index + 1).padStart(2, "0")}</span>
            <strong>{step.label}</strong>
            <p>{step.detail}</p>
          </li>
        ))}
      </ol>
    </section>
  );
}
