export type DecisionRoomEvidenceState =
  | "supported"
  | "hypothesis"
  | "unknown"
  | "gated"
  | "blocked"
  | "designed"
  | "prepare-now"
  | "no-data";

export interface DecisionManifestItem {
  id: string;
  label: string;
  state: DecisionRoomEvidenceState;
  stateLabel: string;
}

export interface TargetAccountRecord {
  accountId: string;
  company: string;
  trigger: string;
  persona: string;
  openingAngle: string;
  source: string;
  owner: string;
  nextAction: string;
}

export const DECISION_ROOM_SOURCES = {
  control: "03_GTM/SheperD GTM Validation and Optimization - Control Note.md",
  icp: "03_GTM/ICP and Stakeholder Personas.md",
  offer: "03_GTM/Sales and Objection Playbook.md",
  claims: "01_Company/Claims and Evidence Register.md",
  product: "01_Company/Product and Business Model.md",
  journey: "03_GTM/Customer Journey and Funnel.md",
  crm: "04_Operations/CRM Data Model.md",
  cadence: "04_Operations/Operating Cadence and KPI Dictionary.md",
  market: "06_Research/Market Evidence and Source Map.md",
} as const;

export const currentDecision = {
  experimentId: "EXP-001",
  title: "Hold the founder truth-and-gates workshop",
  instruction: "Admit, reject, or assign the exact evidence for GAP-001 through GAP-012 before any external activation.",
  owner: "GTM lead - Michael",
  approver: "Founder - Avi",
  doneWhen: "All 12 gates have a recorded state, owner, date, and evidence link.",
  sourcePath: DECISION_ROOM_SOURCES.control,
} as const;

export const decisionManifest: readonly DecisionManifestItem[] = [
  { id: "customer", label: "Customer", state: "hypothesis", stateLabel: "Hypothesis" },
  { id: "economics", label: "Economics", state: "unknown", stateLabel: "Unknown" },
  { id: "offer", label: "Offer", state: "gated", stateLabel: "Gated" },
  { id: "claims", label: "Claims", state: "blocked", stateLabel: "External blocked" },
  { id: "journey", label: "Journey", state: "designed", stateLabel: "Designed" },
  { id: "experiments", label: "Experiment", state: "prepare-now", stateLabel: "EXP-001 ready" },
  { id: "outcomes", label: "Outcome", state: "no-data", stateLabel: "No data" },
];

export const icpProfile = {
  state: "hypothesis" as const,
  bestFit: "A U.S. importer or BCO with recurring container volume, material D&D exposure, centralized finance ownership, accessible invoice and event evidence, and a manageable carrier and port set.",
  boundary: "Company size, revenue, TEU volume, and public pain signals are context only. They do not establish eligibility, qualification, or expected recovery.",
  sourcePath: DECISION_ROOM_SOURCES.icp,
  segments: [
    {
      title: "Finance-owned recurring review",
      signal: "Recurring D&D coding plus a named finance owner",
      learning: "Whether reconciliation and auditability create a valid next step",
      disqualifier: "No owner or no evidence path",
    },
    {
      title: "Concentrated port and carrier exposure",
      signal: "Manageable carrier and port mix plus recurring exceptions",
      learning: "Whether narrower evidence patterns reduce submission friction",
      disqualifier: "Highly fragmented mix without support capacity",
    },
    {
      title: "Partner-referred importer",
      signal: "Permissioned introduction from a broker, 3PL, or advisor",
      learning: "Whether trusted access improves held meetings and valid submissions",
      disqualifier: "No consent, account ownership, or referral terms",
    },
    {
      title: "Audit-pay adjacency",
      signal: "Existing freight-audit workflow that lacks D&D depth",
      learning: "Whether partner, embed, or direct-service delivery fits",
      disqualifier: "Channel conflict or unclear data rights",
    },
  ],
  admissionGates: [
    "Permitted source, checked date, and unambiguous DNC or opt-out state",
    "One segment, persona, channel, message version, relationship state, and date window",
    "Dated, sourceable problem trigger or an explicit unknown",
    "Metadata-only readiness and an approved secure path before any case request",
    "Named product or data owner with available review capacity",
    "Exact message version and claim IDs approved for the intended channel",
  ],
  disqualifiers: [
    "No permitted source or ambiguous DNC state",
    "No named problem owner, current trigger, or relevant U.S. ocean D&D exposure",
    "No lawful and secure evidence path",
    "Requested outcome depends on a guarantee, legal advice, or unsupported claim",
    "Product, data, or reviewer capacity is unavailable",
    "Economics, authority, coverage, or data rights fall outside approved scope",
  ],
} as const;

export const buyingCommittee = [
  {
    role: "Finance",
    people: "CFO, VP Finance, Controller, AP",
    caresAbout: "Realized cash or credit, auditability, effort, fee, and timing",
    triggers: "Finance close, recurring accessorial review, margin pressure, or an audit finding",
    proof: "Recovery mechanics, fee definition, audit trail, case proof, and security",
  },
  {
    role: "Supply chain and logistics",
    people: "Head of logistics, supply chain leadership",
    caresAbout: "Carrier accountability, recurring patterns, and less escalation work",
    triggers: "Repeated carrier or terminal exception, closure, hold, portal change, or backlog",
    proof: "Factual timelines, carrier and port knowledge, and a collaboration model",
  },
  {
    role: "Operations and data",
    people: "AP, operations, and data owner",
    caresAbout: "A clear checklist, secure intake, minimal rework, and status visibility",
    triggers: "Missing-document loops, invoice backlog, reconciliation failure, or unclear ownership",
    proof: "Exact fields, formats, turnaround, ownership, and support",
  },
  {
    role: "Risk and procurement",
    people: "Legal, procurement, security, and privacy",
    caresAbout: "Authority, data processing, retention, liability, and terms",
    triggers: "Vendor review, sensitive-data concern, contract review, or system-access request",
    proof: "Contracts, privacy and security controls, access, retention, and incident response",
  },
  {
    role: "Partner",
    people: "Broker, 3PL, auditor, or consultant",
    caresAbout: "Client value, trust, referral clarity, speed, and economics",
    triggers: "Repeated client questions that cannot be resolved without channel conflict",
    proof: "Referral SLA, account ownership, reporting, and delivery quality",
  },
] as const;

export const painEconomics = {
  formula: "Eligible D&D value x realized outcome share x approved fee - customer effort and delivery cost",
  conclusion: "The problem is material. Recoverable value, fee economics, sensitivity ranges, and ROI remain unknown.",
  sourcePath: DECISION_ROOM_SOURCES.market,
  factors: [
    {
      label: "Reported charge context",
      value: "$15.4B",
      state: "supported" as const,
      boundary: "FMC-reported collections by nine carriers from 2020-04-01 through 2025-03-31. Not an eligible or recoverable pool.",
    },
    {
      label: "Eligible D&D value",
      value: "Unknown - no admitted range",
      state: "unknown" as const,
      boundary: "Requires invoice-level rules, facts, timing, governing terms, and evidence.",
    },
    {
      label: "Realized outcome share",
      value: "Unknown - no admitted range",
      state: "unknown" as const,
      boundary: "Cash, credit, waiver, rejection, reversal, and expiry need separate reconciliation.",
    },
    {
      label: "Approved fee",
      value: "Unknown - no admitted range",
      state: "unknown" as const,
      boundary: "Fee percentage, recovered-value definition, payment timing, and clawbacks are unapproved.",
    },
    {
      label: "Customer and delivery effort",
      value: "Unknown - no admitted range",
      state: "unknown" as const,
      boundary: "Active work, wait, rework, reviewer time, and secure-intake burden are unmeasured.",
    },
    {
      label: "ROI and sensitivity",
      value: "Unavailable",
      state: "blocked" as const,
      boundary: "Do not calculate until representative ranges, methodology, error bounds, reviewer, and approval exist.",
    },
  ],
  sizing: [
    { label: "TAM", value: "Unknown", requirement: "Invoice denominator, eligibility, realized outcomes, and approved fee" },
    { label: "SAM", value: "Unknown", requirement: "Reachable named accounts, evidence access, geography, and delivery coverage" },
    { label: "SOM", value: "Unknown", requirement: "Comparable cohorts, case capacity, cycle time, quality, and cash or credit reconciliation" },
  ],
} as const;

export const competitiveDecision = {
  sourcePath: DECISION_ROOM_SOURCES.offer,
  differentiation: [
    { title: "Evidence completeness", criterion: "More complete records with fewer reviewer corrections" },
    { title: "Decision speed", criterion: "Less reviewed time from intake to submit, stop, or escalate" },
    { title: "Net outcome", criterion: "Realized cash, credit, or waiver after fee and customer work" },
    { title: "Control", criterion: "Clear provenance, owners, approvals, access, and retention" },
  ],
  objections: [
    { objection: "We already dispute charges", response: "Ask about coverage, cycle time, backlog, and outcome tracking. Do not claim superiority." },
    { objection: "Carriers will not pay", response: "Acknowledge case dependence and explore the evidence and dispute route." },
    { objection: "We cannot share invoices", response: "Stop at metadata-first scoping until approved security controls exist." },
    { objection: "How much will we recover?", response: "Do not estimate. Explain the bounded review process and required evidence." },
    { objection: "Is this software or a service?", response: "Separate demonstrated current service, MVP, pilot capability, and roadmap." },
  ],
  winLossCapture: [
    "Alternative selected and why",
    "Price and commercial-model objection",
    "Implementation and customer-work burden",
    "Security, authority, or evidence-path failure",
    "Cycle time, reviewer capacity, and no-decision reason",
  ],
} as const;

export const offerLadder = [
  {
    title: "Evidence-readiness diagnostic",
    state: "gated" as const,
    output: "Present and missing records, owners, dates, and approvals",
    entry: "D0/D1 or approved synthetic metadata",
    gate: "Product/data and reviewer approval",
    prohibited: "Recovery estimate, eligibility, or legal conclusion",
  },
  {
    title: "Invoice-readiness review",
    state: "blocked" as const,
    output: "Completeness and calculation exceptions for human review",
    entry: "Approved D2 metadata; D3 only in a secure case system",
    gate: "Secure intake and checklist owner",
    prohibited: "Invalid, recoverable, or guaranteed outcome",
  },
  {
    title: "Reviewed audit",
    state: "blocked" as const,
    output: "Case-specific findings with source links and confidence",
    entry: "Approved D3 path",
    gate: "Product/data and domain/legal review",
    prohibited: "Automatic legal or recovery decision",
  },
  {
    title: "Recovery support",
    state: "blocked" as const,
    output: "Approved evidence packet and human-authorized follow-up",
    entry: "Contract, authority, route, and capacity",
    gate: "Commercial, legal, and domain approval",
    prohibited: "Refund guarantee or unapproved filing",
  },
  {
    title: "Future prevention",
    state: "blocked" as const,
    output: "Pattern and control proposals from admitted outcomes",
    entry: "Comparable outcome evidence",
    gate: "Product proof and next-90 decision",
    prohibited: "Present-tense product capability",
  },
] as const;

export const claimReadiness = [
  {
    id: "C-016",
    topic: "Material charge context",
    state: "Verified context",
    safeWording: "The FMC reports about $15.4B collected by nine carriers over the stated five-year period.",
    prohibited: "The charge pool is invalid, eligible, or recoverable market value.",
    approver: "Domain/legal reviewer and Avi for the exact channel",
  },
  {
    id: "C-003",
    topic: "Commercial model",
    state: "Company claim",
    safeWording: "SheperD says it uses a success-fee model.",
    prohibited: "Any fee percentage, guaranteed economics, or unreviewed recovered-value definition.",
    approver: "Avi and commercial/legal",
  },
  {
    id: "C-005",
    topic: "Automated checks",
    state: "Mixed and unresolved",
    safeWording: "SheperD markets a 160+ check engine; current implementation is unverified.",
    prohibited: "The complete automated engine is live, proven, or currently available.",
    approver: "Product/data, domain reviewer, and Avi",
  },
  {
    id: "C-024",
    topic: "Current review service",
    state: "Company claim",
    safeWording: "SheperD says it reviews D&D charges and supporting records for potential dispute opportunities.",
    prohibited: "SheperD automatically identifies invalid or recoverable invoices.",
    approver: "Product/data, domain reviewer, and Avi",
  },
  {
    id: "C-025",
    topic: "Case dependence",
    state: "Verified context",
    safeWording: "Eligibility and value depend on invoice content, timing, terms, facts, route, and evidence.",
    prohibited: "A blanket legal conclusion or automatic eligibility decision.",
    approver: "Domain/legal reviewer and Avi for the exact channel",
  },
  {
    id: "C-027",
    topic: "Evidence-readiness offer",
    state: "Internal proposal",
    safeWording: "A proposed review can identify which records, owners, dates, and approvals are present or missing.",
    prohibited: "Recovery estimate, eligibility, or present-tense delivery claim before approval.",
    approver: "Product/data, reviewer, and Avi",
  },
  {
    id: "C-028",
    topic: "Outcome limitation",
    state: "Policy",
    safeWording: "No refund or recovery is promised before case-specific review.",
    prohibited: "Any guaranteed refund, recovery, timing, or legal outcome.",
    approver: "Required in every approved external message",
  },
] as const;

export const customerJourney = [
  {
    title: "Discovery",
    friction: "Public interest does not prove a relevant D&D problem or permission to contact.",
    proof: "Permitted source, dated trigger, persona, message version, and human-reviewed first step",
    owner: "Michael",
    state: "blocked" as const,
  },
  {
    title: "Qualification",
    friction: "Interest can exist without an owner, evidence path, urgency, or delivery capacity.",
    proof: "Account fit, pain, economic and operational owners, evidence readiness, and next action",
    owner: "Michael plus product/data",
    state: "blocked" as const,
  },
  {
    title: "Data intake",
    friction: "Invoice and event records may be sensitive, incomplete, unsafe, or unauthorized.",
    proof: "Authority, DPA or NDA state, approved secure method, checklist version, reviewer, and SLA",
    owner: "Product/security plus legal/privacy",
    state: "blocked" as const,
  },
  {
    title: "Audit review",
    friction: "Completeness, calculation exceptions, and eligibility are different decisions.",
    proof: "Versioned checklist, source-linked findings, confidence, exceptions, and named human reviewer",
    owner: "Product/data plus domain/legal",
    state: "blocked" as const,
  },
  {
    title: "Claim authorization",
    friction: "A reviewed finding does not authorize filing, pricing, settlement, or customer representation.",
    proof: "Contract, authority, approved route, exact wording, commercial terms, and human approval",
    owner: "Avi plus commercial/legal",
    state: "blocked" as const,
  },
  {
    title: "Recovery",
    friction: "Requested, waived, credited, refunded, rejected, and reversed value are not equivalent.",
    proof: "Outcome event, amount and form, dates, source, fee treatment, reversals, and reconciliation",
    owner: "Finance owner plus Michael",
    state: "no-data" as const,
  },
  {
    title: "Learning",
    friction: "One case or one warm path cannot prove a repeatable motion.",
    proof: "Comparable cohorts, cycle time, work, wait, quality, loss reasons, outcomes, and capacity",
    owner: "Avi plus Michael",
    state: "no-data" as const,
  },
] as const;

export const targetAccountQueue = {
  records: [] as readonly TargetAccountRecord[],
  state: "No admitted target-account records",
  instruction: "Populate only after source, permission, DNC, message, secure-data, and reviewer-capacity gates pass.",
  sourcePath: DECISION_ROOM_SOURCES.crm,
  fieldGroups: [
    { label: "Account", fields: ["Stable ID", "Company", "Geography", "ICP rationale", "D&D trigger"] },
    { label: "Buyer", fields: ["Function", "Buying role", "Relationship", "Permitted source", "DNC state"] },
    { label: "Opening", fields: ["Persona", "Message version", "Claim approval", "Channel", "Cohort"] },
    { label: "Control", fields: ["Owner", "Next action", "Due date", "Blocker", "Outcome reason"] },
  ],
} as const;

export const messageLibrary = [
  {
    persona: "Finance",
    direction: "Lead with auditability, cash or credit treatment, workload, and approved fee mechanics.",
    claimIds: "C-003, C-025, C-026, C-028",
    proof: "Approved contract economics and reconciliation method",
  },
  {
    persona: "Logistics",
    direction: "Lead with factual event timelines and evidence gaps. Do not blame carriers or declare charges invalid.",
    claimIds: "C-023, C-024, C-025",
    proof: "Demonstrated workflow and reviewed terminology",
  },
  {
    persona: "AP and operations",
    direction: "Lead with a bounded readiness checklist and a missing-item workflow.",
    claimIds: "C-027, C-028",
    proof: "Approved checklist, intake path, owner, and SLA",
  },
  {
    persona: "Legal and procurement",
    direction: "Lead with authority, human review, case specificity, and contract boundaries.",
    claimIds: "C-025, C-028",
    proof: "Entity, terms, reviewer, insurance, and security evidence",
  },
  {
    persona: "Security and privacy",
    direction: "Lead with minimum data, approved systems, access, retention, and deletion.",
    claimIds: "No external claim approved",
    proof: "Approved privacy, DPA, and security pack",
  },
  {
    persona: "Partner",
    direction: "Lead with permission, account ownership, referral SLA, and no client-data leakage.",
    claimIds: "C-025, C-028",
    proof: "Approved partner terms and delivery capacity",
  },
] as const;

export const outcomeState = [
  { label: "Target accounts", value: "0 admitted records", boundary: "No CRM or permitted account list is connected." },
  { label: "Experiment results", value: "Not run", boundary: "EXP-001 is prepare-now; all other experiments are synthetic-only or blocked." },
  { label: "Win and loss evidence", value: "None admitted", boundary: "Capture reasons only after permissioned comparable activity exists." },
  { label: "Customer outcomes", value: "None admitted", boundary: "No comparable submission, recovery, fee, effort, or cycle evidence exists." },
  { label: "Market sizing", value: "TAM, SAM, SOM unknown", boundary: "Do not infer addressable value from charges, importer counts, or vendor claims." },
] as const;

export const decisionRoomSourceShelf = [
  { label: "GTM control and next decision", path: DECISION_ROOM_SOURCES.control },
  { label: "ICP, personas, and admission", path: DECISION_ROOM_SOURCES.icp },
  { label: "Offer, objections, and talk tracks", path: DECISION_ROOM_SOURCES.offer },
  { label: "Claims and evidence register", path: DECISION_ROOM_SOURCES.claims },
  { label: "Product and commercial truth", path: DECISION_ROOM_SOURCES.product },
  { label: "Customer journey and funnel", path: DECISION_ROOM_SOURCES.journey },
  { label: "CRM schema and control fields", path: DECISION_ROOM_SOURCES.crm },
  { label: "Experiment and KPI contract", path: DECISION_ROOM_SOURCES.cadence },
  { label: "Market evidence and sizing boundary", path: DECISION_ROOM_SOURCES.market },
] as const;
