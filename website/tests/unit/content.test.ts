import { describe, expect, it } from "vitest";
import { recoveryFaqs, recoverySteps } from "../../lib/recovery-content";

describe("recovery responsibility and commercial boundaries", () => {
  it("gives the customer only the invoice handoff", () => {
    expect(recoverySteps.filter((step) => step.owner === "Your part").map((step) => step.kind)).toEqual(["invoice"]);
    expect(recoverySteps.filter((step) => step.owner === "SheperD").map((step) => step.kind)).toEqual(["review", "recovery"]);
  });
  it("distinguishes possible outcomes and does not invent a fee or guarantee", () => {
    const copy = JSON.stringify({ recoverySteps, recoveryFaqs });
    expect(copy).toContain("cash refund or a carrier credit");
    expect(copy).toContain("does not guarantee");
    expect(copy).not.toMatch(/\d+%|guaranteed refund|three.year/i);
  });
});
