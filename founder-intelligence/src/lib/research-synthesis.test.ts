import { describe, expect, it } from "vitest";
import { michaelCadence, michaelOperatingLoop, researchThemes, workflowSnapshot } from "./research-synthesis";

describe("research synthesis", () => {
  it("distills five traceable research questions", () => {
    expect(researchThemes).toHaveLength(5);
    expect(new Set(researchThemes.map((theme) => theme.id)).size).toBe(researchThemes.length);

    for (const theme of researchThemes) {
      expect(theme.question.length).toBeGreaterThan(20);
      expect(theme.executiveTakeaway.length).toBeGreaterThan(60);
      expect(theme.finding.length).toBeGreaterThan(40);
      expect(theme.founderMove.length).toBeGreaterThan(30);
      expect(theme.michaelMove.length).toBeGreaterThan(30);
      expect(theme.source.endsWith(".md")).toBe(true);
    }
  });

  it("reconciles the complete workflow atlas", () => {
    const categorizedWorkflows = workflowSnapshot.slice(1).reduce((sum, item) => sum + item.value, 0);

    expect(workflowSnapshot[0]?.value).toBe(45);
    expect(categorizedWorkflows).toBe(45);
  });

  it("keeps the operating loop and cadence bounded", () => {
    expect(michaelOperatingLoop.map((step) => step.label)).toEqual([
      "Admit",
      "Route",
      "Prepare",
      "Execute after GO",
      "Decide",
    ]);
    expect(michaelCadence).toHaveLength(4);
  });
});
