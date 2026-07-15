export const EVIDENCE_ORDER = [
  "verified",
  "mixed",
  "company-claim",
  "internal-proposal",
  "internal-observation",
  "unverified",
] as const;

export interface EvidenceSummaryRow {
  state: (typeof EVIDENCE_ORDER)[number];
  count: number;
  percentage: number;
}

export interface EvidenceSummary {
  total: number;
  rows: EvidenceSummaryRow[];
}

export function summarizeEvidence(counts: Record<string, number>): EvidenceSummary {
  const total = Object.values(counts).reduce((sum, value) => sum + value, 0);
  const denominator = Math.max(total, 1);

  return {
    total,
    rows: EVIDENCE_ORDER.map((state) => {
      const count = counts[state] ?? 0;

      return {
        state,
        count,
        percentage: (count / denominator) * 100,
      };
    }),
  };
}
