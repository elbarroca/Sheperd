import type { BriefLens } from "./types";

export const MICHAEL_PLAN_SOURCE_PATH = "10_Sources/Source - 16 Week Engagement Plan.md";

export function researchFileHref(path: string): string {
  return `/research?file=${encodeURIComponent(path)}`;
}

export const briefLenses: readonly BriefLens[] = [
  {
    id: "company",
    label: "Company truth",
    finding: "The vision is clear. Authority, product truth, ownership, and operating proof are not complete.",
    implication: "Michael can prepare the commercial system, but cannot represent SheperD independently yet.",
    nextAction: "Admit the entity, engagement, owners, product truth, and approved claims.",
    sourcePath: "06_Research/Company and Founder Dossier.md",
  },
  {
    id: "industry",
    label: "Industry truth",
    finding: "D&D recovery is a material problem, but eligibility, economics, and outcomes remain case-specific.",
    implication: "Messaging must show uncertainty and keep domain conclusions with qualified reviewers.",
    nextAction: "Approve the route boundary, reviewer, claims, and commercial truth table.",
    sourcePath: "06_Research/Industry Regulatory and Competitive Dossier.md",
  },
  {
    id: "goals",
    label: "16-week goal",
    finding: "The learner-to-leader arc is useful as a learning plan, not as a proven forecast.",
    implication: "Time does not unlock outreach or scale. Evidence and an explicit decision do.",
    nextAction: "Use three evidence gates: safe start, bounded cohort, repeatability audit.",
    sourcePath: MICHAEL_PLAN_SOURCE_PATH,
  },
];

export const phases = [
  {
    period: "Weeks 0-2",
    sourceLabel: "Immerse + build",
    admittedLabel: "Truth + safe-start gates",
    state: "prepare-now",
    detail: "Engagement, product, claims, CRM, secure intake, owners, baselines, and external-activation decision.",
  },
  {
    period: "Weeks 3-12",
    sourceLabel: "Activate + learn",
    admittedLabel: "One bounded cohort after GO",
    state: "approval-required",
    detail: "Warm, cold, partner, and inbound stay separate. Change one variable and preserve no-decisions.",
  },
  {
    period: "Weeks 13-16",
    sourceLabel: "Own + scale",
    admittedLabel: "Repeatability audit",
    state: "evidence-required",
    detail: "Scale language requires comparable cohorts, capacity, quality, cycle, and commercial evidence.",
  },
] as const;

export const operatingAxes = [
  "Domain knowledge",
  "Value proposition and customer journey",
  "Technology and CRM",
  "Sales infrastructure and marketing assets",
  "Digital presence and content",
  "Customer and partner segmentation",
  "Work rhythms and governance",
  "Live sales execution",
] as const;

export const ricardoNotes = [
  {
    id: "RN-001",
    title: "Treat the 16-week plan as a learning contract",
    sourceObservation: "The source defines an ambitious learner-to-leader arc with volume and outcome expectations across sixteen weeks.",
    note: "The strategic arc is useful, but its volume and outcome language is not yet an adopted forecast. Each phase needs evidence, owner, permission, and stop rules.",
    implication: "Approve Week 0 and Week 2 gates before any external cohort.",
    evidence: "10_Sources/Source - 16 Week Engagement Plan.md",
  },
  {
    id: "RN-002",
    title: "Michael is building the commercial operating system",
    sourceObservation: "The role charter combines market learning, CRM discipline, founder knowledge, and commercial coordination.",
    note: "The mandate is GTM and Revenue Operations, not generic marketing or independent regulatory/product authority.",
    implication: "Name product, domain, privacy, commercial, and website counterparts with response SLAs.",
    evidence: "03_GTM/Michael Role Charter.md",
  },
  {
    id: "RN-003",
    title: "Do not hide the eighth axis",
    sourceObservation: "The operating plan says seven axes but lists eight, including Live Sales Execution.",
    note: "The source says seven axes and lists eight. Live Sales Execution is a separate operating workstream with distinct risk and evidence requirements.",
    implication: "Show execution as approval-gated, not as an automatic continuation of preparation.",
    evidence: "10_Sources/Source - 16 Week Engagement Plan.md",
  },
  {
    id: "RN-004",
    title: "A dashboard cannot manufacture market proof",
    sourceObservation: "The research system and GTM design are mature, while no authorized comparable external cohort exists.",
    note: "Research and GTM design improved. Real market evidence remains 1.8 because no authorized comparable cohort exists.",
    implication: "Keep source, interpretation, and decision layers visually and structurally separate.",
    evidence: "03_GTM/SheperD GTM Validation and Optimization - Control Note.md",
  },
] as const;

export const improvementBacklog = [
  { id: "IMP-001", area: "Authority", title: "Admit entity, signatory, and engagement evidence", impact: 5, evidence: 2, risk: 1, effort: 2, gate: "GAP-001 to GAP-003", state: "prepare-now" },
  { id: "IMP-002", area: "Product", title: "Build demonstrated capability and check-catalog truth map", impact: 5, evidence: 2, risk: 2, effort: 3, gate: "GAP-004", state: "prepare-now" },
  { id: "IMP-003", area: "Claims", title: "Approve sentence-level claim, channel, and expiry matrix", impact: 5, evidence: 3, risk: 2, effort: 3, gate: "GAP-008", state: "prepare-now" },
  { id: "IMP-004", area: "Security", title: "Approve D2/D3 systems, access, retention, and incident controls", impact: 5, evidence: 1, risk: 1, effort: 4, gate: "GAP-009 and GAP-010", state: "prepare-now" },
  { id: "IMP-005", area: "Capacity", title: "Observe active time, wait, rework, quality, and reviewer SLA", impact: 4, evidence: 1, risk: 3, effort: 3, gate: "GAP-011", state: "approval-required" },
  { id: "IMP-006", area: "Market", title: "Run one permissioned warm cohort with complete event capture", impact: 5, evidence: 1, risk: 3, effort: 4, gate: "GAP-001 to GAP-011", state: "blocked-external" },
] as const;
