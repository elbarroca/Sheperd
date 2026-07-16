export type DecisionRoomEvidenceState =
  | "supported"
  | "hypothesis"
  | "research-now"
  | "founder-decision"
  | "pilot-measurement"
  | "designed"
  | "setup-ready"
  | "needs-approval"
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
  michaelPlan: "10_Sources/Source - 16 Week Engagement Plan.md",
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
  title: "Run the founder truth-and-gates workshop",
  instruction: "Review GAP-001 through GAP-012: authority, current product and service truth, claims, secure data, commercial terms, list provenance, reviewer capacity, and delivery capacity. Record an explicit external-activation GO or NO-GO.",
  owner: "Michael",
  approver: "Avi",
  doneWhen: "All 12 gates have an admitted, rejected, or incomplete state, plus an owner, target date, and evidence link; no unsupported GO.",
  sourcePath: DECISION_ROOM_SOURCES.control,
} as const;

export const decisionManifest: readonly DecisionManifestItem[] = [
  { id: "customer", label: "Customer", state: "hypothesis", stateLabel: "ICP set" },
  { id: "economics", label: "Economics", state: "research-now", stateLabel: "Research plan" },
  { id: "offer", label: "Offer", state: "setup-ready", stateLabel: "Set up next" },
  { id: "claims", label: "Claims", state: "designed", stateLabel: "Guardrails set" },
  { id: "journey", label: "Journey", state: "designed", stateLabel: "Designed" },
  { id: "experiments", label: "Experiment", state: "prepare-now", stateLabel: "EXP-001 ready" },
  { id: "outcomes", label: "Outcome", state: "pilot-measurement", stateLabel: "Pilot measures" },
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

export const icpQualificationDimensions = [
  {
    id: "01",
    label: "Exposure",
    signal: "Recurring U.S. ocean-container D&D exposure within a bounded carrier and port set",
    minimumProof: "A dated invoice pattern, operating event, or sourceable trigger",
    decision: "Keep researching when the exposure is only inferred",
  },
  {
    id: "02",
    label: "Owner",
    signal: "A named finance owner plus an operations or data counterpart",
    minimumProof: "Roles, decision path, and a current reason to review the problem",
    decision: "Disqualify when no accountable owner exists",
  },
  {
    id: "03",
    label: "Evidence",
    signal: "Invoice and event metadata can be accessed through an approved path",
    minimumProof: "Available fields, source system, authority, and secure intake state",
    decision: "Do not request case data before the path is approved",
  },
  {
    id: "04",
    label: "Delivery",
    signal: "The case scope fits available product, reviewer, and domain capacity",
    minimumProof: "Named reviewer, bounded scope, checklist, and service-level expectation",
    decision: "Narrow or pause when review capacity is unavailable",
  },
  {
    id: "05",
    label: "Permission",
    signal: "The account source, relationship, channel, consent, and DNC state are explicit",
    minimumProof: "Permitted source, checked date, owner, and approved message version",
    decision: "Only a permissioned account may enter a pilot cohort",
  },
] as const;

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
  conclusion: "Public context is already usable. Every missing commercial input now has a research, founder-decision, or pilot-measurement path.",
  sourcePath: DECISION_ROOM_SOURCES.market,
  publicSignals: [
    {
      label: "Collected D&D context",
      value: "$15.4B",
      state: "supported" as const,
      sourceId: "SRC-009",
      meaning: "FMC-reported collections by nine carriers from 2020-04-01 through 2025-03-31.",
      boundary: "Materiality context, not an eligible or recoverable pool.",
    },
    {
      label: "FY2025 Charge Complaints",
      value: "296",
      state: "supported" as const,
      sourceId: "SRC-022",
      meaning: "The FMC received 296 Charge Complaints and investigated 164 through the process.",
      boundary: "Route activity, not a market eligibility or recovery rate.",
    },
    {
      label: "FY2025 complaint relief",
      value: "$2.89M",
      state: "supported" as const,
      sourceId: "SRC-022",
      meaning: "FMC-reported charges refunded, waived, or cancelled through the Charge Complaint route.",
      boundary: "One public route, not all direct disputes or SheperD outcomes.",
    },
    {
      label: "Identified U.S. importers",
      value: "240,535",
      state: "supported" as const,
      sourceId: "SRC-044",
      meaning: "The final Census 2023-2024 profile reports the broad 2024 importer universe.",
      boundary: "All modes; not an ocean-container, D&D exposure, or buyer count.",
    },
    {
      label: "Public success-fee signal",
      value: "20%-35%",
      state: "research-now" as const,
      sourceId: "SRC-031/032",
      meaning: "Observed vendor pages show 20%, 25%-35%, and typical 30% success-fee language.",
      boundary: "Vendor-stated and internally inconsistent; context only, not SheperD pricing.",
    },
  ],
  inputWorkbench: [
    {
      label: "Eligible invoice value",
      lane: "Pilot measurement",
      state: "pilot-measurement" as const,
      method: "Review the first permissioned invoice cohort. Record billed value, rule checks, factual exclusions, reviewer, and decision.",
      owner: "Michael + domain reviewer",
      output: "Eligible-value range with denominator and exclusions",
      nextAction: "Avi approves the pilot cohort; Michael versions the review sheet.",
      sourcePath: DECISION_ROOM_SOURCES.market,
    },
    {
      label: "Realized outcome share",
      lane: "Pilot measurement",
      state: "pilot-measurement" as const,
      method: "Reconcile requested, waived, credited, refunded, rejected, reversed, and expired value as separate events.",
      owner: "Michael + customer finance owner",
      output: "Realized outcome rate by value and case",
      nextAction: "Add the outcome event schema before the first case is accepted.",
      sourcePath: DECISION_ROOM_SOURCES.cadence,
    },
    {
      label: "Fee and recovered-value definition",
      lane: "Founder decision",
      state: "founder-decision" as const,
      method: "Use public vendor pricing only as context. Decide fee, credit and waiver treatment, timing, clawbacks, and minimum case economics.",
      owner: "Avi + commercial/legal",
      output: "Approved one-page commercial term sheet",
      nextAction: "Record the fee and recovered-value choices under GAP-006 during EXP-001.",
      sourcePath: DECISION_ROOM_SOURCES.product,
    },
    {
      label: "Customer and delivery effort",
      lane: "Pilot measurement",
      state: "pilot-measurement" as const,
      method: "Time active work, wait, rework, reviewer time, and secure-intake support for every pilot case.",
      owner: "Michael + product/data owner",
      output: "Case cost, workload, cycle-time, and capacity range",
      nextAction: "Add timestamps and work-minute fields to the pilot record.",
      sourcePath: DECISION_ROOM_SOURCES.cadence,
    },
    {
      label: "ROI and sensitivity",
      lane: "Research now",
      state: "research-now" as const,
      method: "Build the low, base, and high scenario template now; populate it only with the approved fee and observed pilot ranges.",
      owner: "Michael prepares; Avi approves",
      output: "Bounded sensitivity table with assumptions and error limits",
      nextAction: "Build the blank model now. Calculate after fee and pilot inputs exist.",
      sourcePath: DECISION_ROOM_SOURCES.market,
    },
  ],
  sizing: [
    {
      label: "TAM setup",
      state: "research-now" as const,
      owner: "Michael + research",
      method: "Build the U.S. ocean-container D&D invoice denominator, then apply measured eligibility, realized outcome, and approved fee inputs.",
      result: null,
    },
    {
      label: "SAM setup",
      state: "research-now" as const,
      owner: "Michael",
      method: "Create a named account universe filtered by ocean exposure, recurring D&D, evidence access, geography, and delivery coverage.",
      result: null,
    },
    {
      label: "SOM setup",
      state: "pilot-measurement" as const,
      owner: "Avi + Michael",
      method: "Use observed case capacity, qualification, cycle time, review quality, realized outcomes, and fee reconciliation.",
      result: null,
    },
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
    state: "setup-ready" as const,
    stateLabel: "Set up now",
    purpose: "Show which records, owners, dates, and approvals are present or missing.",
    owner: "Michael",
    setupAction: "Turn the existing D0/D1 checklist into a one-page intake and sample output.",
    readyWhen: "Avi approves scope and product/data names the reviewer.",
    proof: "Versioned checklist, sample report, owner, and turnaround.",
    guardrail: "No recovery estimate, eligibility decision, or legal conclusion.",
  },
  {
    title: "Invoice-readiness review",
    state: "needs-approval" as const,
    stateLabel: "Set up next",
    purpose: "Surface completeness and calculation exceptions for human review.",
    owner: "Product/data + Michael",
    setupAction: "Name the secure intake path, required fields, checklist owner, and review SLA.",
    readyWhen: "D2 metadata is approved; D3 stays inside an approved case system.",
    proof: "Secure intake test, checklist version, access owner, and sample case.",
    guardrail: "Do not label an invoice invalid, recoverable, or guaranteed.",
  },
  {
    title: "Reviewed audit",
    state: "needs-approval" as const,
    stateLabel: "Needs reviewer",
    purpose: "Produce case-specific findings with sources, exceptions, and confidence.",
    owner: "Domain reviewer + product/data",
    setupAction: "Choose the named reviewer, escalation rule, and sign-off record.",
    readyWhen: "The D3 path and human review workflow pass a sample case.",
    proof: "Reviewer rubric, decision log, and source-linked sample finding.",
    guardrail: "No automatic legal or recovery decision.",
  },
  {
    title: "Recovery support",
    state: "founder-decision" as const,
    stateLabel: "Needs founder terms",
    purpose: "Prepare an approved evidence packet and human-authorized follow-up.",
    owner: "Avi + commercial/legal",
    setupAction: "Define authority, permitted routes, fee treatment, customer approvals, and delivery capacity.",
    readyWhen: "Contract, authority, route, reviewer, and capacity are recorded.",
    proof: "Approved terms, authorization, route checklist, and reconciliation method.",
    guardrail: "No refund guarantee or unapproved filing.",
  },
  {
    title: "Future prevention",
    state: "pilot-measurement" as const,
    stateLabel: "Needs pilot evidence",
    purpose: "Turn repeated case patterns into prevention and control proposals.",
    owner: "Product/data + Avi",
    setupAction: "Define the pattern threshold and the next-90 product decision before analysing outcomes.",
    readyWhen: "Comparable outcomes support a repeated pattern and a reviewed control.",
    proof: "Cohort definition, pattern count, false-positive review, and product decision.",
    guardrail: "Do not present future prevention as a current product capability.",
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
    state: "setup-ready" as const,
  },
  {
    title: "Qualification",
    friction: "Interest can exist without an owner, evidence path, urgency, or delivery capacity.",
    proof: "Account fit, pain, economic and operational owners, evidence readiness, and next action",
    owner: "Michael plus product/data",
    state: "setup-ready" as const,
  },
  {
    title: "Data intake",
    friction: "Invoice and event records may be sensitive, incomplete, unsafe, or unauthorized.",
    proof: "Authority, DPA or NDA state, approved secure method, checklist version, reviewer, and SLA",
    owner: "Product/security plus legal/privacy",
    state: "needs-approval" as const,
  },
  {
    title: "Audit review",
    friction: "Completeness, calculation exceptions, and eligibility are different decisions.",
    proof: "Versioned checklist, source-linked findings, confidence, exceptions, and named human reviewer",
    owner: "Product/data plus domain/legal",
    state: "needs-approval" as const,
  },
  {
    title: "Claim authorization",
    friction: "A reviewed finding does not authorize filing, pricing, settlement, or customer representation.",
    proof: "Contract, authority, approved route, exact wording, commercial terms, and human approval",
    owner: "Avi plus commercial/legal",
    state: "founder-decision" as const,
  },
  {
    title: "Recovery",
    friction: "Requested, waived, credited, refunded, rejected, and reversed value are not equivalent.",
    proof: "Outcome event, amount and form, dates, source, fee treatment, reversals, and reconciliation",
    owner: "Finance owner plus Michael",
    state: "pilot-measurement" as const,
  },
  {
    title: "Learning",
    friction: "One case or one warm path cannot prove a repeatable motion.",
    proof: "Comparable cohorts, cycle time, work, wait, quality, loss reasons, outcomes, and capacity",
    owner: "Avi plus Michael",
    state: "pilot-measurement" as const,
  },
] as const;

export const targetAccountQueue = {
  records: [] as readonly TargetAccountRecord[],
  state: "The account queue is ready to populate",
  instruction: "The 16-week proposal says SheperD has source data for a prioritized list, but no account rows are admitted here yet. Import only after source, consent, DNC, owner, and next-action fields are recorded.",
  sourcePath: DECISION_ROOM_SOURCES.crm,
  fieldGroups: [
    { label: "Account", fields: ["Stable ID", "Company", "Geography", "ICP rationale", "D&D trigger"] },
    { label: "Buyer", fields: ["Function", "Buying role", "Relationship", "Permitted source", "DNC state"] },
    { label: "Opening", fields: ["Persona", "Message version", "Claim approval", "Channel", "Cohort"] },
    { label: "Control", fields: ["Owner", "Next action", "Due date", "Blocker", "Outcome reason"] },
  ],
} as const;

export const icpSetupMetrics = [
  {
    label: "Beachheads",
    value: icpProfile.segments.length,
    state: "Hypotheses defined",
  },
  {
    label: "Buying roles",
    value: buyingCommittee.length,
    state: "Committee mapped",
  },
  {
    label: "Proof filters",
    value: icpQualificationDimensions.length,
    state: "Qualification staged",
  },
  {
    label: "Admission gates",
    value: icpProfile.admissionGates.length,
    state: "Required before entry",
  },
  {
    label: "Disqualifiers",
    value: icpProfile.disqualifiers.length,
    state: "Stop rules explicit",
  },
  {
    label: "Admitted accounts",
    value: targetAccountQueue.records.length,
    state: "No rows imported",
  },
] as const;

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
  { label: "Target accounts", value: "0 admitted records", boundary: "The proposal says source data exists; no CRM or permissioned account rows are connected to this workspace yet." },
  { label: "Experiment results", value: "Not run", boundary: "EXP-001 is ready for the founder setup workshop; execution results start at zero." },
  { label: "Win and loss evidence", value: "Capture template ready", boundary: "No records yet; reason, alternative, price, burden, security, and no-decision fields are defined." },
  { label: "Customer outcomes", value: "Measurement fields ready", boundary: "No observed result yet; outcome, effort, cycle, reviewer, and reconciliation fields are defined." },
  { label: "Market sizing", value: "Model staged; no approved value", boundary: "TAM, SAM, and SOM methods are defined but cannot use charge, importer, or vendor figures as a shortcut." },
] as const;

export const decisionRoomSourceShelf = [
  { label: "GTM control and next decision", path: DECISION_ROOM_SOURCES.control },
  { label: "Michael's original 16-week proposal", path: DECISION_ROOM_SOURCES.michaelPlan },
  { label: "ICP, personas, and admission", path: DECISION_ROOM_SOURCES.icp },
  { label: "Offer, objections, and talk tracks", path: DECISION_ROOM_SOURCES.offer },
  { label: "Claims and evidence register", path: DECISION_ROOM_SOURCES.claims },
  { label: "Product and commercial truth", path: DECISION_ROOM_SOURCES.product },
  { label: "Customer journey and funnel", path: DECISION_ROOM_SOURCES.journey },
  { label: "CRM schema and control fields", path: DECISION_ROOM_SOURCES.crm },
  { label: "Experiment and KPI contract", path: DECISION_ROOM_SOURCES.cadence },
  { label: "Market evidence and sizing boundary", path: DECISION_ROOM_SOURCES.market },
] as const;
