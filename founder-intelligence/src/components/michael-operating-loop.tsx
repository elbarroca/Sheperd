import type { JSX } from "react";
import { michaelCadence, michaelOperatingLoop, workflowSnapshot } from "@/lib/research-synthesis";

export function MichaelOperatingLoop(): JSX.Element {
  return (
    <section className="michael-operating-system section-block" aria-labelledby="michael-loop-title">
      <div className="section-heading">
        <div>
          <p className="eyebrow">Weekly operating system</p>
          <h2 id="michael-loop-title">Turn every finding into an owned decision</h2>
        </div>
        <p>Michael runs the loop. Founders and specialists retain the approvals that make action legitimate.</p>
      </div>

      <dl className="workflow-snapshot" aria-label="Workflow coverage snapshot">
        {workflowSnapshot.map((item) => (
          <div key={item.label} className={`workflow-tone-${item.tone}`}>
            <dt>{item.label}</dt>
            <dd>{item.value}</dd>
          </div>
        ))}
      </dl>

      <ol className="operating-loop" aria-label="Michael's five-step operating loop">
        {michaelOperatingLoop.map((step) => (
          <li key={step.id} className={step.id === "04" ? "is-gated" : undefined}>
            <span>{step.id}</span>
            <h3>{step.label}</h3>
            <p>{step.detail}</p>
            <strong>{step.output}</strong>
          </li>
        ))}
      </ol>

      <div className="cadence-grid">
        {michaelCadence.map((item) => (
          <article key={item.label}>
            <h3>{item.label}</h3>
            <p>{item.detail}</p>
          </article>
        ))}
      </div>
    </section>
  );
}
