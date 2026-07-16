import { describe, expect, it } from "vitest";
import knowledge from "../generated/knowledge-index.json";
import {
  buyingCommittee,
  claimReadiness,
  currentDecision,
  DECISION_ROOM_SOURCES,
  decisionManifest,
  decisionRoomSourceShelf,
  icpProfile,
  icpQualificationDimensions,
  icpSetupMetrics,
  offerLadder,
  outcomeState,
  painEconomics,
  targetAccountQueue,
} from "./decision-room-content";

describe("customer and decision room content", () => {
  it("links every decision area to an admitted canonical source", () => {
    const admittedPaths = new Set(knowledge.files.map((file) => file.path));
    const sourcePaths = Object.values(DECISION_ROOM_SOURCES);

    expect(sourcePaths.every((path) => admittedPaths.has(path))).toBe(true);
    expect(decisionRoomSourceShelf.map((source) => source.path)).toEqual(sourcePaths);
  });

  it("covers the complete decision dependency without upgrading evidence", () => {
    expect(decisionManifest.map((item) => item.label)).toEqual([
      "Customer",
      "Economics",
      "Offer",
      "Claims",
      "Journey",
      "Experiment",
      "Outcome",
    ]);
    expect(decisionManifest.find((item) => item.label === "Customer")?.state).toBe("hypothesis");
    expect(decisionManifest.find((item) => item.label === "Economics")?.state).toBe("research-now");
    expect(decisionManifest.find((item) => item.label === "Offer")?.state).toBe("setup-ready");
    expect(decisionManifest.find((item) => item.label === "Outcome")?.state).toBe("pilot-measurement");
  });

  it("turns every missing economics input into owned setup work without inventing results", () => {
    expect(targetAccountQueue.records).toHaveLength(0);
    expect(painEconomics.publicSignals.map((signal) => signal.value)).toEqual([
      "$15.4B",
      "296",
      "$2.89M",
      "240,535",
      "20%-35%",
    ]);
    expect(painEconomics.inputWorkbench.every((input) => (
      input.method.length > 60
      && input.owner.length > 5
      && input.output.length > 20
      && input.nextAction.length > 20
      && Object.values(DECISION_ROOM_SOURCES).includes(input.sourcePath)
    ))).toBe(true);
    expect(new Set(painEconomics.inputWorkbench.map((input) => input.state))).toEqual(new Set([
      "pilot-measurement",
      "founder-decision",
      "research-now",
    ]));
    expect(painEconomics.sizing.every((item) => item.result === null)).toBe(true);
    expect(offerLadder.map((offer) => offer.state)).not.toContain("blocked");
    expect(offerLadder.map((offer) => offer.stateLabel)).toEqual([
      "Set up now",
      "Set up next",
      "Needs reviewer",
      "Needs founder terms",
      "Needs pilot evidence",
    ]);
    expect(outcomeState.map((item) => item.value)).toContain("0 admitted records");
    expect(outcomeState.map((item) => item.value)).toContain("Not run");
    expect(outcomeState.map((item) => item.value)).toContain("Model staged; no approved value");
    expect(targetAccountQueue.instruction).toContain("source data for a prioritized list");
  });

  it("keeps EXP-001 aligned with the canonical founder gate", () => {
    expect(currentDecision.title).toBe("Run the founder truth-and-gates workshop");
    expect(currentDecision.instruction).toContain("GAP-001 through GAP-012");
    expect(currentDecision.doneWhen).toContain("All 12 gates");
  });

  it("derives ICP setup metrics from admitted structures without a synthetic score", () => {
    expect(icpSetupMetrics.map((metric) => metric.value)).toEqual([
      icpProfile.segments.length,
      buyingCommittee.length,
      icpQualificationDimensions.length,
      icpProfile.admissionGates.length,
      icpProfile.disqualifiers.length,
      targetAccountQueue.records.length,
    ]);
    expect(icpQualificationDimensions.map((dimension) => dimension.label)).toEqual([
      "Exposure",
      "Owner",
      "Evidence",
      "Delivery",
      "Permission",
    ]);
    expect(JSON.stringify({ icpQualificationDimensions, icpSetupMetrics })).not.toMatch(/score|%/iu);
  });

  it("keeps claim wording bounded and plain", () => {
    expect(claimReadiness).toHaveLength(7);
    expect(claimReadiness.every((claim) => (
      claim.safeWording.length > 30 && claim.prohibited.length > 30 && claim.approver.length > 10
    ))).toBe(true);

    const copy = JSON.stringify({
      claimReadiness,
      decisionManifest,
      outcomeState,
      painEconomics,
      targetAccountQueue,
    });
    expect(copy).not.toMatch(/[—–]/u);
  });
});
