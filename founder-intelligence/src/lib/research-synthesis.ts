export type ResearchThemeState = "mixed evidence" | "blocked" | "hypothesis" | "internal only";

export type ResearchTheme = {
  id: string;
  theme: string;
  question: string;
  executiveTakeaway: string;
  studied: string;
  finding: string;
  founderMove: string;
  michaelMove: string;
  source: string;
  state: ResearchThemeState;
};

export const researchThemes: readonly ResearchTheme[] = [
  {
    id: "RS-01",
    theme: "Company truth",
    question: "What company and mandate are we actually operating?",
    executiveTakeaway: "The brand is visible; legal authority, ownership, and operating proof are incomplete.",
    studied: "Entity, founder role, authority, product state, claims, security, economics, and delivery capacity.",
    finding: "The SheperD brand and founder direction are visible. The legal and operating proof pack is not complete enough for external activation.",
    founderMove: "Admit named owners, demonstrations, dated decisions, and signed authority—or keep each gate blocked.",
    michaelMove: "Maintain the truth tables and contradiction log. Do not represent SheperD externally yet.",
    source: "06_Research/Company and Founder Dossier.md",
    state: "blocked",
  },
  {
    id: "RS-02",
    theme: "Problem and domain",
    question: "Is D&D recovery a real, addressable problem?",
    executiveTakeaway: "The recovery problem is material, but eligibility, economics, and outcomes stay case-specific.",
    studied: "D&D rules, invoice evidence, deadlines, dispute routes, buyer pain, competitors, and claim boundaries.",
    finding: "The process is material and evidence-heavy. Eligibility, route, recovery, and economics remain case-specific and reviewer-dependent.",
    founderMove: "Approve exact positioning and reviewed claims. Do not promise blanket eligibility, recovery, or automation.",
    michaelMove: "Build cited talk tracks, discovery questions, and objection responses that show uncertainty clearly.",
    source: "06_Research/Industry Regulatory and Competitive Dossier.md",
    state: "mixed evidence",
  },
  {
    id: "RS-03",
    theme: "Market learning",
    question: "Who should SheperD learn from first?",
    executiveTakeaway: "The GTM learning system is specified; demand, willingness to pay, and delivery economics are not proven.",
    studied: "ICP, personas, journey, channels, partners, CRM, content, cohorts, and commercial experiments.",
    finding: "The commercial learning system is well specified. Demand, willingness to pay, conversion, and delivery economics are not yet proven by comparable cohorts.",
    founderMove: "Authorize one bounded cohort only after the activation gates pass and capacity is named.",
    michaelMove: "Prepare segmentation, the CRM schema, and a one-variable experiment with full event capture.",
    source: "03_GTM/SheperD GTM Validation and Optimization - Control Note.md",
    state: "hypothesis",
  },
  {
    id: "RS-04",
    theme: "Operating system",
    question: "Can Michael run this without absorbing specialist authority?",
    executiveTakeaway: "Michael can orchestrate GTM and RevOps, but specialists must retain material approval rights.",
    studied: "Forty-five workflows across safe start, knowledge, GTM, delivery, learning, and governance.",
    finding: "Eight workflows are mapped internally, 25 are blocked, eight need an owner, and four sit outside Michael's independent scope.",
    founderMove: "Name owners, approvers, tools, response SLAs, and capacity before assigning outcome accountability.",
    michaelMove: "Run the source-owner-gate-measurement loop and escalate anything outside the admitted boundary.",
    source: "06_Research/Role and Workflow Atlas.md",
    state: "internal only",
  },
  {
    id: "RS-05",
    theme: "AI and automation",
    question: "Where can automation help without creating hidden risk?",
    executiveTakeaway: "Automation should begin with deterministic controls; no AI pilot or measured benefit exists.",
    studied: "Deterministic controls, reviewed drafts, human-only decisions, data classes, and modeled time savings.",
    finding: "No AI pilot is active and the benefit is not measured. Deterministic gates come first; D3 and material actions stay human-only.",
    founderMove: "Approve policy, tool, data path, owner, baseline, logging, retention, and rollback before any pilot.",
    michaelMove: "Test deterministic controls on synthetic or permitted records before reviewed drafting assistance.",
    source: "06_Research/AI Opportunity Register.md",
    state: "blocked",
  },
];

export const workflowSnapshot = [
  { label: "Total workflows", value: 45, tone: "neutral" },
  { label: "Mapped internally", value: 8, tone: "ready" },
  { label: "Blocked", value: 25, tone: "blocked" },
  { label: "Need an owner", value: 8, tone: "decision" },
  { label: "Outside Michael's scope", value: 4, tone: "neutral" },
] as const;

export const michaelOperatingLoop = [
  {
    id: "01",
    label: "Admit",
    detail: "Capture the source, evidence state, permission, and data class.",
    output: "Traceable work item",
  },
  {
    id: "02",
    label: "Route",
    detail: "Name the operator, accountable approver, due date, and controlling gate.",
    output: "Owned decision queue",
  },
  {
    id: "03",
    label: "Prepare",
    detail: "Build the internal brief, CRM structure, test, or proposed next action.",
    output: "Reviewable artifact",
  },
  {
    id: "04",
    label: "Execute after GO",
    detail: "Run only the approved bounded workflow; preserve cohort and version boundaries.",
    output: "Comparable evidence",
  },
  {
    id: "05",
    label: "Decide",
    detail: "Reconcile evidence and record continue, change, stop, or no-go.",
    output: "Versioned founder decision",
  },
] as const;

export const michaelCadence = [
  {
    label: "Daily async",
    detail: "Progress, blockers, and next actions.",
  },
  {
    label: "Weekly rhythm",
    detail: "Monday priorities, Wednesday claim blockers, Friday pipeline and approvals.",
  },
  {
    label: "Biweekly",
    detail: "Sprint retrospective and one continue, change, or stop decision.",
  },
  {
    label: "Monthly + gates",
    detail: "Founder risk review, plus formal decisions at Weeks 2, 6, 12, and 16.",
  },
] as const;
