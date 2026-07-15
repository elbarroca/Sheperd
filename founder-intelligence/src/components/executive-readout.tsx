import type { JSX } from "react";
import { researchThemes } from "../lib/research-synthesis";

type ExecutiveScores = {
  researchSystem: number;
  gtmDesign: number;
  realMarketEvidence: number;
  safeExecutionReadiness: number;
};

type ExecutiveReadoutProps = {
  scores: ExecutiveScores;
};

export function ExecutiveReadout({ scores }: ExecutiveReadoutProps): JSX.Element {
  return (
    <section className="executive-readout section-block" aria-labelledby="executive-readout-title">
      <div className="executive-thesis">
        <div>
          <p className="eyebrow">The 60-second read</p>
          <h2 id="executive-readout-title">Prepared to learn. Not cleared to scale.</h2>
        </div>
        <div>
          <strong>Core message</strong>
          <p>SheperD has a strong research and GTM operating design. The missing layer is admitted authority, comparable market evidence, safe execution, and proven delivery economics.</p>
          <small>Internal research synthesis—not an external performance or readiness claim.</small>
        </div>
      </div>

      <div className="evidence-tension" aria-label="Preparation compared with external proof">
        <article className="evidence-tension-strong">
          <span>Strong preparation</span>
          <h3>Designed to learn</h3>
          <dl>
            <div><dt>Research system</dt><dd><strong>{scores.researchSystem.toFixed(1)}</strong><span>/ 10</span></dd></div>
            <div><dt>GTM design</dt><dd><strong>{scores.gtmDesign.toFixed(1)}</strong><span>/ 10</span></dd></div>
          </dl>
        </article>
        <div className="evidence-tension-gap">
          <span>Key distinction</span>
          <strong>Preparation does not prove demand.</strong>
        </div>
        <article className="evidence-tension-weak">
          <span>Not yet proven</span>
          <h3>Blocked from scaling</h3>
          <dl>
            <div><dt>Market evidence</dt><dd><strong>{scores.realMarketEvidence.toFixed(1)}</strong><span>/ 10</span></dd></div>
            <div><dt>Safe readiness</dt><dd><strong>{scores.safeExecutionReadiness.toFixed(1)}</strong><span>/ 10</span></dd></div>
          </dl>
        </article>
      </div>

      <div className="nugget-heading">
        <h3>Five golden nuggets from the study</h3>
        <p>Read these first. Open the evidence trail below when a decision needs the underlying study and source path.</p>
      </div>
      <ol className="executive-nuggets">
        {researchThemes.map((theme) => (
          <li key={theme.id}>
            <header>
              <code>{theme.id}</code>
              <span className={`synthesis-state synthesis-state-${theme.state.replaceAll(" ", "-")}`}>{theme.state}</span>
            </header>
            <h4>{theme.theme}</h4>
            <p>{theme.executiveTakeaway}</p>
          </li>
        ))}
      </ol>
    </section>
  );
}
