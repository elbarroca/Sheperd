import { describe, expect, it } from "vitest";
import {
  getMarketOpportunityDisplay,
  type MarketOpportunity,
} from "../../lib/market-opportunity";

describe("market opportunity claim gate", () => {
  it("does not expose a figure or source while suppressed", () => {
    const state: MarketOpportunity = {
      status: "suppressed",
      figure: null,
      source: null,
    };

    expect(getMarketOpportunityDisplay(state)).toEqual({
      figure: null,
      source: null,
    });
  });

  it("exposes the figure only with complete source metadata", () => {
    const state: MarketOpportunity = {
      status: "approved",
      figure: "$13B",
      source: {
        title: "Approved market source",
        href: "https://example.com/source",
        checkedAt: "2026-09-15",
      },
    };

    expect(getMarketOpportunityDisplay(state)).toEqual({
      figure: "$13B",
      source: state.source,
    });
  });
});
