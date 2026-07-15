import { describe, expect, it } from "vitest";
import knowledge from "../generated/knowledge-index.json";
import {
  claimReadiness,
  DECISION_ROOM_SOURCES,
  decisionManifest,
  decisionRoomSourceShelf,
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
    expect(decisionManifest.find((item) => item.label === "Economics")?.state).toBe("unknown");
    expect(decisionManifest.find((item) => item.label === "Outcome")?.state).toBe("no-data");
  });

  it("keeps account, economics, market sizing, and outcomes fail-closed", () => {
    expect(targetAccountQueue.records).toHaveLength(0);
    expect(painEconomics.factors.slice(1).every((factor) => (
      factor.value.startsWith("Unknown") || factor.value === "Unavailable"
    ))).toBe(true);
    expect(painEconomics.sizing.every((item) => item.value === "Unknown")).toBe(true);
    expect(outcomeState.map((item) => item.value)).toContain("0 admitted records");
    expect(outcomeState.map((item) => item.value)).toContain("None admitted");
    expect(outcomeState.map((item) => item.value)).toContain("TAM, SAM, SOM unknown");
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
