"use client";

import { useMemo, useState } from "react";
import { DEFAULT_WEIGHTS, rankExperiments } from "@/lib/priority";
import type { Experiment, PriorityWeights } from "@/lib/types";

const controls: { key: keyof PriorityWeights; label: string }[] = [
  { key: "learningValue", label: "Learning value" },
  { key: "evidenceReadiness", label: "Evidence readiness" },
  { key: "lowerRisk", label: "Lower risk" },
  { key: "lowerEffort", label: "Lower effort" },
];

export function PriorityLab({ experiments }: { experiments: Experiment[] }) {
  const [weights, setWeights] = useState<PriorityWeights>(DEFAULT_WEIGHTS);
  const ranked = useMemo(() => rankExperiments(experiments, weights), [experiments, weights]);

  function setWeight(key: keyof PriorityWeights, value: number): void {
    setWeights((current) => {
      const next = { ...current, [key]: value };

      return Object.values(next).some((weight) => weight > 0) ? next : current;
    });
  }

  return (
    <div className="priority-workbench">
      <aside className="weight-console">
        <p className="eyebrow">Visible planning weights</p>
        <h2>Change the lens—not the gate.</h2>
        {controls.map((control) => (
          <label key={control.key}>
            <span>{control.label}</span>
            <output>{weights[control.key]}</output>
            <input
              type="range"
              aria-label={control.label}
              min="0"
              max="100"
              value={weights[control.key]}
              onChange={(event) => setWeight(control.key, Number(event.target.value))}
            />
          </label>
        ))}
        <button type="button" className="reset-button" onClick={() => setWeights(DEFAULT_WEIGHTS)}>Reset weights</button>
        <p className="console-note">Priority is not ROI, causality, conversion prediction, or execution approval.</p>
      </aside>
      <section className="ranked-list" aria-live="polite" aria-label="Ranked experiments">
        {ranked.map((experiment, index) => (
          <article key={experiment.experimentId} className={`ranked-item ${experiment.executionAllowed ? "is-eligible" : "is-blocked"}`}>
            <span className="rank-number">{String(index + 1).padStart(2, "0")}</span>
            <strong className="rank-score">{experiment.priorityScore.toFixed(2)}</strong>
            <div className="rank-copy">
              <div className="rank-title-row">
                <h3>{experiment.experimentId} · {experiment.name}</h3>
                <span className={`state-pill ${experiment.executionAllowed ? "state-eligible" : "state-blocked"}`}>
                  {experiment.executionState.replaceAll("-", " ")}
                </span>
              </div>
              <p>{experiment.hypothesis}</p>
            </div>
          </article>
        ))}
      </section>
    </div>
  );
}
