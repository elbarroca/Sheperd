export interface MarketOpportunitySource {
  title: string;
  href: string;
  checkedAt: string;
}

export type MarketOpportunity =
  | {
      status: "suppressed";
      figure: null;
      source: null;
    }
  | {
      status: "approved";
      figure: string;
      source: MarketOpportunitySource;
    };

export const marketOpportunity: MarketOpportunity = {
  status: "approved",
  figure: "$13B",
  source: {
    title: "The Economic Value of America's Ports",
    href: "https://nam.org/wp-content/uploads/securepdfs/2026/02/BTW-2026-Web.vF_.pdf",
    checkedAt: "2026-09-15",
  },
};

export function getMarketOpportunityDisplay(
  state: MarketOpportunity,
): { figure: string | null; source: MarketOpportunitySource | null } {
  if (state.status === "suppressed") {
    return { figure: null, source: null };
  }

  return { figure: state.figure, source: state.source };
}
