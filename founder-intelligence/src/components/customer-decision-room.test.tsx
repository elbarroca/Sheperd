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
    expect(markup).toContain("External activation blocked");
    expect(markup).toContain("0 admitted records");
    expect(markup).toContain("No customer evidence has been promoted");
    expect(markup).toContain("TAM, SAM, SOM unknown");
  });

  it("renders the complete experiment board and source layer without fake outcomes", () => {
    const markup = renderToStaticMarkup(
      <CustomerDecisionRoom experiments={getDecisionRoomExperiments()} />,
    );

    expect((markup.match(/DRAFT - HUMAN REVIEW REQUIRED/g) ?? [])).toHaveLength(2);
    expect(markup).toContain("EXP-001");
    expect(markup).toContain("EXP-008");
    expect((markup.match(/Result<\/span><strong>Not run/g) ?? [])).toHaveLength(8);
    expect(markup).toContain("Open Knowledge map");
    expect(markup).toContain("/knowledge?file=");
    expect(markup).not.toMatch(/[—–]/u);
  });
});
