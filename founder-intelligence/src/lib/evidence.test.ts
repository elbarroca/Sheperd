import { describe, expect, it } from "vitest";
import { summarizeEvidence } from "./evidence";

describe("summarizeEvidence", () => {
  it("reports an empty corpus as zero sources", () => {
    const summary = summarizeEvidence({});

    expect(summary.total).toBe(0);
    expect(summary.rows.every((row) => row.percentage === 0)).toBe(true);
  });

  it("calculates whole percentages from observed counts", () => {
    const summary = summarizeEvidence({ verified: 17, mixed: 3 });

    expect(summary.total).toBe(20);
    expect(summary.rows.find((row) => row.state === "verified")?.percentage).toBe(85);
  });
});
