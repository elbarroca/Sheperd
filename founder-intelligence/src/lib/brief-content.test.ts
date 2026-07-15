import { describe, expect, it } from "vitest";
import { briefLenses, MICHAEL_PLAN_SOURCE_PATH, researchFileHref } from "./content";

describe("founder brief content", () => {
  it("distills company, industry, and goals into traceable lenses", () => {
    expect(briefLenses.map((lens) => lens.id)).toEqual(["company", "industry", "goals"]);

    for (const lens of briefLenses) {
      expect(lens.finding.length).toBeGreaterThan(50);
      expect(lens.implication.length).toBeGreaterThan(50);
      expect(lens.nextAction.length).toBeGreaterThan(40);
      expect(lens.sourcePath.endsWith(".md")).toBe(true);
    }
  });

  it("creates a shareable deep link for the complete plan", () => {
    expect(researchFileHref(MICHAEL_PLAN_SOURCE_PATH)).toBe(
      "/research?file=10_Sources%2FSource%20-%2016%20Week%20Engagement%20Plan.md",
    );
  });
});
