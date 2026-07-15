export type EvidenceStatus =
  | "verified-and-approved"
  | "approved-company-description"
  | "educational-primary-source"
  | "company-claim"
  | "internal-proposal"
  | "internal-observation"
  | "inference"
  | "unverified"
  | "mixed"
  | "contradicted"
  | "expired"
  | "internal-only";

export type PublicationChannel = "preview-web" | "production-web";

export interface PublicClaim {
  readonly claimId: string;
  readonly exactText: string;
  readonly evidenceStatus: EvidenceStatus;
  readonly sourceIds: readonly string[];
  readonly sourceUrls: readonly string[];
  readonly checkedDate: string;
  readonly expiresOn: string;
  readonly approvedFor: readonly PublicationChannel[];
  readonly approvedBy: string | null;
  readonly approvalDate: string | null;
  readonly notes: string;
}

export const ALLOWED_PUBLIC_STATES = [
  "verified-and-approved",
  "approved-company-description",
  "educational-primary-source",
] as const satisfies readonly EvidenceStatus[];

export const claims = {
  "EDU-EVIDENCE-001": {
    claimId: "EDU-EVIDENCE-001",
    exactText:
      "Reviewing a D&D invoice may require billing facts, operational evidence, governing terms, and current rules.",
    evidenceStatus: "educational-primary-source",
    sourceIds: ["SRC-002", "SRC-008"],
    sourceUrls: [
      "https://www.ecfr.gov/current/title-46/chapter-IV/subchapter-B/part-541",
      "https://www.fmc.gov/ocean-shipping-reform-act-of-2022-implementation/guidance-on-charge-complaint-interim-procedure/",
    ],
    checkedDate: "2026-07-15",
    expiresOn: "2026-08-14",
    approvedFor: [],
    approvedBy: null,
    approvalDate: null,
    notes: "Candidate wording. Domain or legal publication approval is missing.",
  },
  "EDU-541-001": {
    claimId: "EDU-541-001",
    exactText:
      "Current 46 CFR Part 541 contains invoice content, issuance timing, and dispute-process requirements.",
    evidenceStatus: "educational-primary-source",
    sourceIds: ["SRC-002", "SRC-007"],
    sourceUrls: [
      "https://www.ecfr.gov/current/title-46/chapter-IV/subchapter-B/part-541",
      "https://www.fmc.gov/articles/u-s-court-of-appeals-issues-decision-in-case-on-demurrage-and-detention-billing-practices/",
    ],
    checkedDate: "2026-07-15",
    expiresOn: "2026-08-14",
    approvedFor: [],
    approvedBy: null,
    approvalDate: null,
    notes: "Candidate wording. Domain or legal publication approval is missing.",
  },
  "EDU-41301-001": {
    claimId: "EDU-41301-001",
    exactText:
      "The three-year period in 46 U.S.C. 41301 is a complaint limitation, not blanket refund eligibility.",
    evidenceStatus: "educational-primary-source",
    sourceIds: ["SRC-003"],
    sourceUrls: [
      "https://uscode.house.gov/view.xhtml?edition=prelim&num=0&req=granuleid%3AUSC-prelim-title46-section41301",
    ],
    checkedDate: "2026-07-15",
    expiresOn: "2026-08-14",
    approvedFor: [],
    approvedBy: null,
    approvalDate: null,
    notes: "Candidate wording. Domain or legal publication approval is missing.",
  },
  "EDU-FMC-001": {
    claimId: "EDU-FMC-001",
    exactText:
      "FMC investigations do not represent the complainant and do not guarantee a refund.",
    evidenceStatus: "educational-primary-source",
    sourceIds: ["SRC-008"],
    sourceUrls: [
      "https://www.fmc.gov/ocean-shipping-reform-act-of-2022-implementation/guidance-on-charge-complaint-interim-procedure/",
    ],
    checkedDate: "2026-07-15",
    expiresOn: "2026-08-14",
    approvedFor: [],
    approvedBy: null,
    approvalDate: null,
    notes: "Candidate wording. Domain or legal publication approval is missing.",
  },
  "EDU-CASE-001": {
    claimId: "EDU-CASE-001",
    exactText:
      "Outcomes depend on the applicable rules, route, deadlines, records, and case facts.",
    evidenceStatus: "educational-primary-source",
    sourceIds: ["SRC-002", "SRC-003", "SRC-008"],
    sourceUrls: [
      "https://www.ecfr.gov/current/title-46/chapter-IV/subchapter-B/part-541",
      "https://uscode.house.gov/view.xhtml?edition=prelim&num=0&req=granuleid%3AUSC-prelim-title46-section41301",
      "https://www.fmc.gov/ocean-shipping-reform-act-of-2022-implementation/guidance-on-charge-complaint-interim-procedure/",
    ],
    checkedDate: "2026-07-15",
    expiresOn: "2026-08-14",
    approvedFor: [],
    approvedBy: null,
    approvalDate: null,
    notes: "Candidate wording. Domain or legal publication approval is missing.",
  },
} as const satisfies Record<string, PublicClaim>;

export type ClaimId = keyof typeof claims;

export const productionRequiredClaimIds = [
  "EDU-EVIDENCE-001",
  "EDU-541-001",
  "EDU-41301-001",
  "EDU-FMC-001",
  "EDU-CASE-001",
] as const satisfies readonly ClaimId[];
