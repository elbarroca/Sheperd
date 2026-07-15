import type { Experiment, PriorityWeights, RankedExperiment } from "./types";

export const DEFAULT_WEIGHTS: PriorityWeights = {
  learningValue: 35,
  evidenceReadiness: 35,
  lowerRisk: 20,
  lowerEffort: 10,
};

const ELIGIBLE_STATES = new Set(["prepare-now", "synthetic-only"]);

function assertScore(value: number, field: string): void {
  if (!Number.isInteger(value) || value < 1 || value > 5) {
    throw new Error(`${field} must be an integer from 1 to 5`);
  }
}

export function rankExperiments(
  experiments: Experiment[],
  weights: PriorityWeights = DEFAULT_WEIGHTS,
): RankedExperiment[] {
  const totalWeight = Object.values(weights).reduce((sum, value) => sum + value, 0);
  if (Object.values(weights).some((value) => value < 0) || totalWeight <= 0) {
    throw new Error("Priority weights must be non-negative and include one positive value");
  }
  return experiments
    .map((experiment) => {
      assertScore(experiment.learningValue, "learningValue");
      assertScore(experiment.evidenceReadiness, "evidenceReadiness");
      assertScore(experiment.risk, "risk");
      assertScore(experiment.effort, "effort");
      const priorityScore =
        (experiment.learningValue * weights.learningValue +
          experiment.evidenceReadiness * weights.evidenceReadiness +
          (6 - experiment.risk) * weights.lowerRisk +
          (6 - experiment.effort) * weights.lowerEffort) /
        totalWeight;
      return {
        ...experiment,
        executionAllowed: ELIGIBLE_STATES.has(experiment.executionState),
        priorityScore: Number(priorityScore.toFixed(2)),
      };
    })
    .sort(
      (left, right) =>
        Number(right.executionAllowed) - Number(left.executionAllowed) ||
        right.priorityScore - left.priorityScore ||
        left.experimentId.localeCompare(right.experimentId),
    );
}
