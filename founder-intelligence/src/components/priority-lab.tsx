"use client";

import { useState } from "react";
import { DEFAULT_WEIGHTS, rankExperiments } from "@/lib/priority";
import type { Experiment, PriorityWeights } from "@/lib/types";

const controls: { key: keyof PriorityWeights; label: string; note: string }[] = [
  { key: "learningValue", label: "Learning value", note: "How much uncertainty the test could remove" },
  { key: "evidenceReadiness", label: "Evidence readiness", note: "How ready the required inputs and controls are" },
  { key: "lowerRisk", label: "Lower risk", note: "Preference for lower-risk work" },
  { key: "lowerEffort", label: "Lower effort", note: "Preference for lower-effort work" },
];

export function PriorityLab({ experiments }: { experiments: Experiment[] }) {
  const [weights, setWeights] = useState<PriorityWeights>(DEFAULT_WEIGHTS);
  const ranked = rankExperiments(experiments, weights);
  const allowed = ranked.filter((experiment) => experiment.executionAllowed);
  const blocked = ranked.filter((experiment) => !experiment.executionAllowed);

  function setWeight(key: keyof PriorityWeights, value: number): void {
    setWeights((current) => {
      const next = { ...current, [key]: value };

      return Object.values(next).some((weight) => weight > 0) ? next : current;
    });
  }

  return (
    <section className="priority-lab section-block" aria-labelledby="priority-title">
      <div className="section-heading">
        <div>
          <p className="eyebrow">Dependency-first queue</p>
          <h2 id="priority-title">Three internal experiments can move now</h2>
        </div>
        <p>Eligibility comes before weighted priority. No slider can unlock blocked external work.</p>
      </div>

      <div className="priority-summary" aria-label="Experiment eligibility summary">
        <div><strong>{allowed.length}</strong><span>internal experiments allowed</span></div>
        <div><strong>{blocked.length}</strong><span>experiments blocked</span></div>
        <div><strong>0</strong><span>external experiments allowed</span></div>
      </div>

      <div className="priority-matrix-block">
        <div className="matrix-copy">
          <p className="eyebrow">Learning value and readiness</p>
          <h3>Start high and right, but only inside the gate</h3>
          <p>Position reflects the observed 1 to 5 inputs. Color communicates current eligibility.</p>
        </div>
        <div className="priority-matrix" role="img" aria-label="Experiments positioned by evidence readiness and learning value">
          <span className="matrix-y-label">Learning value</span>
          <span className="matrix-x-label">Evidence readiness</span>
          <span className="matrix-zone">Higher value and readiness</span>
          {experiments.map((experiment) => {
            const isAllowed = allowed.some((item) => item.experimentId === experiment.experimentId);

            return (
              <span
                key={experiment.experimentId}
                className={`matrix-point ${isAllowed ? "is-eligible" : "is-blocked"}`}
                style={{ left: `${experiment.evidenceReadiness * 17}%`, bottom: `${experiment.learningValue * 16}%` }}
                title={`${experiment.experimentId}: ${experiment.name}`}
              >
                {experiment.experimentId.replace("EXP-", "")}
              </span>
            );
          })}
        </div>
      </div>

      <div className="ranked-list" aria-label="Ranked internal experiments">
        {allowed.map((experiment, index) => (
          <article key={experiment.experimentId} className="ranked-item is-eligible">
            <span className="rank-number">{String(index + 1).padStart(2, "0")}</span>
            <div className="rank-copy">
              <div className="rank-title-row">
                <h3>{experiment.name}</h3>
                <span className="state-pill state-eligible">Allowed internally</span>
              </div>
              <p>{experiment.hypothesis}</p>
              <span className="rank-score">Planning score {experiment.priorityScore.toFixed(1)} / 5</span>
            </div>
          </article>
        ))}
      </div>

      <details className="weight-console">
        <summary>Advanced: adjust planning weights</summary>
        <div className="weight-console-body">
          <fieldset>
            <legend>Visible planning weights</legend>
            {controls.map((control) => {
              const id = `weight-${control.key}`;

              return (
                <div className="weight-control" key={control.key}>
                  <div>
                    <label htmlFor={id}>{control.label}</label>
                    <span>{control.note}</span>
                    <output htmlFor={id}>{weights[control.key]}</output>
                  </div>
                  <input
                    id={id}
                    type="range"
                    min="0"
                    max="100"
                    value={weights[control.key]}
                    onChange={(event) => setWeight(control.key, Number(event.target.value))}
                  />
                </div>
              );
            })}
          </fieldset>
          <button type="button" className="reset-button" onClick={() => setWeights(DEFAULT_WEIGHTS)}>Reset weights</button>
          <p className="console-note">Priority is not ROI, causality, conversion prediction, or execution approval.</p>
        </div>
      </details>

      <details className="blocked-experiments">
        <summary>Inspect {blocked.length} blocked experiments</summary>
        <ul>
          {blocked.map((experiment) => (
            <li key={experiment.experimentId}>
              <div><code>{experiment.experimentId}</code><strong>{experiment.name}</strong></div>
              <span>{experiment.executionState.replaceAll("-", " ")}</span>
            </li>
          ))}
        </ul>
      </details>
    </section>
  );
}
