import { describe, expect, it } from "vitest";
import knowledge from "../generated/knowledge-index.json";
import {
  competitorProfiles,
  marketEvidenceGroups,
  marketSignals,
  michaelGtmPlays,
  michaelPillars,
  michaelTasks,
  michaelWeeklyPlan,
} from "./focused-content";

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

  it("turns the proposal into a complete, gated 16-week route", () => {
    const admittedPaths = new Set(knowledge.files.map((file) => file.path));
    const usedPillars = new Set(michaelWeeklyPlan.flatMap((week) => week.pillars));
    const sourcePaths = michaelWeeklyPlan.flatMap((week) => week.sourcePaths);

    expect(michaelWeeklyPlan.map((week) => week.week)).toEqual(Array.from({ length: 16 }, (_, index) => index + 1));
    expect(michaelPillars).toHaveLength(8);
    expect(usedPillars).toEqual(new Set(michaelPillars.map((pillar) => pillar.id)));
    expect(michaelWeeklyPlan.filter((week) => week.state === "prepare-now")).toHaveLength(2);
    expect(michaelWeeklyPlan.filter((week) => week.state === "execute-after-go")).toHaveLength(10);
    expect(michaelWeeklyPlan.filter((week) => week.state === "evidence-review")).toHaveLength(3);
    expect(michaelWeeklyPlan.filter((week) => week.state === "founder-decision")).toHaveLength(1);
    expect(sourcePaths.every((path) => admittedPaths.has(path))).toBe(true);
  });

  it("turns research into four sourced GTM plays without opening the external gate", () => {
    const admittedPaths = new Set(knowledge.files.map((file) => file.path));

    expect(michaelGtmPlays).toHaveLength(4);
    expect(michaelGtmPlays.filter((play) => play.state === "execute-after-go")).toHaveLength(1);
    expect(michaelGtmPlays.flatMap((play) => play.sourcePaths).every((path) => admittedPaths.has(path))).toBe(true);
    expect(michaelGtmPlays.every((play) => play.steps.length === 3 && play.boundary.length > 55)).toBe(true);
  });

  it("uses plain hyphens in new dashboard copy", () => {
    const copy = JSON.stringify({
      competitorProfiles,
      marketEvidenceGroups,
      marketSignals,
      michaelGtmPlays,
      michaelPillars,
      michaelTasks,
      michaelWeeklyPlan,
    });
    expect(copy).not.toMatch(/[—–]/u);
  });
});
