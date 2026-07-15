export interface PublicSource {
  readonly sourceId: string;
  readonly title: string;
  readonly issuer: string;
  readonly checkedDate: string;
  readonly href: `https://${string}`;
}

export const publicSources = [
  {
    sourceId: "SRC-002",
    title: "46 CFR Part 541",
    issuer: "Electronic Code of Federal Regulations",
    checkedDate: "2026-07-15",
    href: "https://www.ecfr.gov/current/title-46/chapter-IV/subchapter-B/part-541",
  },
  {
    sourceId: "SRC-003",
    title: "46 U.S.C. 41301",
    issuer: "U.S. House Office of the Law Revision Counsel",
    checkedDate: "2026-07-15",
    href: "https://uscode.house.gov/view.xhtml?edition=prelim&num=0&req=granuleid%3AUSC-prelim-title46-section41301",
  },
  {
    sourceId: "SRC-008",
    title: "Guidance on Charge Complaint Interim Procedure",
    issuer: "Federal Maritime Commission",
    checkedDate: "2026-07-15",
    href: "https://www.fmc.gov/ocean-shipping-reform-act-of-2022-implementation/guidance-on-charge-complaint-interim-procedure/",
  },
] as const satisfies readonly PublicSource[];
