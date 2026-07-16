import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it, vi } from "vitest";

vi.mock("server-only", () => ({}));

import { getDecisionRoomExperiments } from "../lib/data";
import { CustomerDecisionRoom } from "./customer-decision-room";

describe("CustomerDecisionRoom", () => {
  it("renders one evidence-controlled page with explicit empty states", () => {
    const markup = renderToStaticMarkup(
      <CustomerDecisionRoom experiments={getDecisionRoomExperiments()} />,
    );

    expect((markup.match(/<h1/g) ?? [])).toHaveLength(1);
    expect(markup).toContain("Customer and decision room");
    expect(markup).toContain("Setup active");
    expect(markup).toContain("Run the founder truth-and-gates workshop");
    expect(markup).toContain("GAP-001 through GAP-012");
    expect(markup).toContain("Current ICP setup metrics");
    expect(markup).toContain("Five evidence filters define pilot fit");
    expect(markup).toContain("This is a qualification method, not a predictive score.");
    expect(markup).toContain("No rows imported");
    expect(markup).toContain("Most of the economics work can start now");
    expect(markup).toContain("Every missing input has a method and owner");
    expect(markup).toContain("0 admitted records");
    expect(markup).toContain("The measurement system is defined; observed results start at zero");
    expect(markup).toContain("Model staged; no approved value");
  });

  it("renders the complete experiment board and source layer without fake outcomes", () => {
    const markup = renderToStaticMarkup(
      <CustomerDecisionRoom experiments={getDecisionRoomExperiments()} />,
    );

    expect((markup.match(/DRAFT - HUMAN REVIEW REQUIRED/g) ?? [])).toHaveLength(2);
    expect(markup).toContain("EXP-001");
    expect(markup).toContain("EXP-008");
    expect((markup.match(/Result<\/span><strong>Not run/g) ?? [])).toHaveLength(8);
    expect(markup).toContain("240,535");
    expect(markup).toContain("20%-35%");
    expect(markup).toContain("The offer ladder is a build sequence, not a wall of blockers");
    expect(markup).toContain("The 16-week proposal says SheperD has source data for a prioritized list");
    expect((markup.match(/Likely objections/g) ?? [])).toHaveLength(1);
    expect(markup).toContain("Open Knowledge map");
    expect(markup).toContain("/knowledge?file=");
    expect(markup).not.toMatch(/[—–]/u);
  });
});
