import { describe, expect, it } from "vitest";
import { rankExperiments } from "./priority";
import type { Experiment } from "./types";

const experiments: Experiment[] = [
  {
    experimentId: "EXP-001",
    name: "Founder gate",
    hypothesis: "Resolve blockers",
    executionState: "prepare-now",
    learningValue: 5,
    evidenceReadiness: 5,
    risk: 1,
    effort: 2,
  },
  {
    experimentId: "EXP-004",
    name: "Warm cohort",
    hypothesis: "Learn from outreach",
    executionState: "blocked-external",
    learningValue: 5,
    evidenceReadiness: 5,
    risk: 1,
    effort: 1,
  },
];

describe("rankExperiments", () => {
  it("keeps blocked experiments blocked regardless of score", () => {
    const ranked = rankExperiments(experiments, {
      learningValue: 100,
      evidenceReadiness: 0,
      lowerRisk: 0,
      lowerEffort: 0,
    });
    expect(ranked[0].experimentId).toBe("EXP-001");
    expect(ranked.find((item) => item.experimentId === "EXP-004")?.executionAllowed).toBe(false);
  });

  it("rejects an empty weighting model", () => {
    expect(() => rankExperiments(experiments, {
      learningValue: 0,
      evidenceReadiness: 0,
      lowerRisk: 0,
      lowerEffort: 0,
    })).toThrow(/one positive value/);
  });
});
