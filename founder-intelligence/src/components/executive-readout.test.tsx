import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";
import { ExecutiveReadout } from "./executive-readout";

const scores = {
  researchSystem: 9.3,
  gtmDesign: 9.2,
  realMarketEvidence: 1.8,
  safeExecutionReadiness: 3.3,
};

describe("ExecutiveReadout", () => {
  it("renders the core distinction and exact planning scores", () => {
    const markup = renderToStaticMarkup(<ExecutiveReadout scores={scores} />);

    expect(markup).toContain("Prepared to learn. Not cleared to scale.");
    expect(markup).toContain("Preparation does not prove demand.");
    expect(markup).toContain("9.3");
    expect(markup).toContain("1.8");
  });

  it("renders all five evidence-state-labelled golden nuggets", () => {
    const markup = renderToStaticMarkup(<ExecutiveReadout scores={scores} />);

    expect((markup.match(/<li>/g) ?? [])).toHaveLength(5);
    expect(markup).toContain("RS-01");
    expect(markup).toContain("RS-05");
    expect(markup).toContain("Internal research synthesis—not an external performance or readiness claim.");
  });
});
