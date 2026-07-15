import { describe, expect, it, vi } from "vitest";

vi.mock("server-only", () => ({}));

import { getDecisionRoomExperiments } from "./data";

describe("decision room experiment DTO", () => {
  it("exposes all eight experiments with exact execution boundaries", () => {
    const experiments = getDecisionRoomExperiments();

    expect(experiments).toHaveLength(8);
    expect(experiments.filter((item) => item.executionState === "prepare-now").map((item) => item.experimentId)).toEqual(["EXP-001"]);
    expect(experiments.filter((item) => item.executionState === "synthetic-only").map((item) => item.experimentId)).toEqual(["EXP-002", "EXP-003"]);
    expect(experiments.filter((item) => item.executionState.startsWith("blocked-"))).toHaveLength(5);
  });

  it("exposes the board fields without inventing results or decisions", () => {
    const experiments = getDecisionRoomExperiments();

    expect(experiments.every((item) => (
      item.segment.length > 0
      && item.persona.length > 0
      && item.channel.length > 0
      && item.messageVersion.length > 0
      && item.cohort.length > 0
      && item.expectedLearning.length > 0
      && item.decisionDate.length > 0
      && item.continueThreshold.length > 0
      && item.changeThreshold.length > 0
      && item.stopThreshold.length > 0
    ))).toBe(true);
    expect(experiments.every((item) => item.result === null && item.decision === null)).toBe(true);
  });
});
