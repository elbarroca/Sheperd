import { describe, expect, it } from "vitest";
import knowledge from "../generated/knowledge-index.json";
import { competitorProfiles, marketEvidenceGroups, marketSignals, michaelTasks } from "./focused-content";

describe("focused founder dashboard content", () => {
  it("maps the full observed competitor set without implying performance", () => {
    expect(competitorProfiles).toHaveLength(14);
    expect(new Set(competitorProfiles.map((profile) => profile.url)).size).toBe(14);
    expect(competitorProfiles.filter((profile) => profile.category === "recovery")).toHaveLength(5);
    expect(competitorProfiles.filter((profile) => profile.category === "audit")).toHaveLength(4);
    expect(competitorProfiles.filter((profile) => profile.category === "enterprise")).toHaveLength(5);
    expect(competitorProfiles.every((profile) => profile.evidenceBoundary.length > 25)).toBe(true);
  });

  it("keeps market numbers attached to explicit boundaries", () => {
    expect(marketSignals).toHaveLength(4);
    expect(marketSignals.map((signal) => signal.value)).toEqual(["$15.4B", "296", "239,231", "14"]);
    expect(marketSignals.every((signal) => signal.boundary.length > 35)).toBe(true);
    expect(marketEvidenceGroups.reduce((total, group) => total + group.links.length, 0)).toBe(11);
    expect(marketEvidenceGroups.every((group) => group.boundary.length > 35)).toBe(true);
  });

  it("maps all eight workstreams to admitted sources and one external gate", () => {
    const admittedPaths = new Set(knowledge.files.map((file) => file.path));

    expect(michaelTasks).toHaveLength(8);
    expect(michaelTasks.filter((task) => task.state === "approval-gated")).toHaveLength(1);
    expect(michaelTasks.every((task) => admittedPaths.has(task.sourcePath))).toBe(true);
    expect(michaelTasks.every((task) => task.aiAssist.length > 35 && task.humanDecision.length > 35)).toBe(true);
  });

  it("uses plain hyphens in new dashboard copy", () => {
    const copy = JSON.stringify({ competitorProfiles, marketEvidenceGroups, marketSignals, michaelTasks });
    expect(copy).not.toMatch(/[—–]/u);
  });
});
