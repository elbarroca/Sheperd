export interface PromptItem {
  readonly title: string;
  readonly prompt: string;
}

export const siteCopy = {
  brand: "SheperD",
  previewLabel: "Preview",
  navigation: [
    { label: "Requirements", href: "#review-requirements" },
    { label: "Process", href: "#process" },
    { label: "Sources", href: "#sources" },
    { label: "Limits", href: "#limits" },
  ],
  hero: {
    audience: "For importer finance and logistics teams",
    headline: "Start with the record.",
    support:
      "Align invoice facts, operating records, applicable rules, and open questions before review.",
    cta: "Review requirements",
    evidenceClasses: [
      { label: "Billing facts", detail: "What the invoice states" },
      { label: "Operational facts", detail: "What happened and when" },
      { label: "Applicable terms", detail: "Which text applies to the dates" },
    ],
  },
  manifest: {
    heading: "One charge. Three questions.",
    body: "Keep each answer separate until the record supports a case-specific conclusion.",
    items: [
      { title: "Billing facts", prompt: "What does the invoice state?" },
      { title: "Operational facts", prompt: "What happened operationally?" },
      { title: "Applicable terms", prompt: "Which terms and rules apply?" },
    ] satisfies readonly PromptItem[],
  },
  requirements: {
    heading: "Build the review checklist.",
    body: "Use these prompts to identify gaps before any case-specific conclusion.",
    items: [
      {
        title: "Invoice record",
        prompt: "Which invoice and shipment record are under review?",
      },
      {
        title: "Payment record",
        prompt: "Was the charge paid, credited, or still open?",
      },
      {
        title: "Terms",
        prompt: "Which tariff, contract, and free-time terms apply to the dates?",
      },
      {
        title: "Operations",
        prompt: "Which events establish availability, pickup, return, holds, or closures?",
      },
      {
        title: "Communications",
        prompt: "Which messages document requests, responses, and disputed facts?",
      },
    ] satisfies readonly PromptItem[],
  },
  process: {
    heading: "Keep the path conditional.",
    body: "Each step can expose a missing record, a new reviewer, or a different route.",
    steps: [
      {
        title: "Frame the question",
        prompt: "Define the charge, dates, parties, and open issue.",
      },
      {
        title: "Confirm authority",
        prompt: "Identify who may provide records and who must review the case.",
      },
      {
        title: "Assemble the record",
        prompt: "Separate available evidence from missing evidence.",
      },
      {
        title: "Compare sources",
        prompt: "Match dates, terms, events, and the current source text.",
      },
      {
        title: "Escalate for review",
        prompt: "Route case-specific judgments to an authorized human reviewer.",
      },
      {
        title: "Record the outcome",
        prompt: "Preserve the decision, basis, limits, and next action.",
      },
    ] satisfies readonly PromptItem[],
  },
  limits: {
    heading: "What this Preview does not do.",
    items: [
      {
        title: "No case decision",
        text: "This Preview does not determine compliance, eligibility, legal position, or likely outcome.",
      },
      {
        title: "No collection",
        text: "There is no form, upload, contact capture, analytics, or tracking script in this application.",
      },
      {
        title: "No production claim",
        text: "Company capabilities, commercial terms, contact details, customer proof, and legal notices remain suppressed.",
      },
    ],
  },
  faq: {
    heading: "Preview questions",
    items: [
      {
        question: "Does this Preview accept invoices?",
        answer: "No. This application has no form, upload, or account system.",
      },
      {
        question: "Does it assess a case?",
        answer: "No. The page organizes review questions but does not evaluate records or reach a conclusion.",
      },
      {
        question: "Why is company detail limited?",
        answer: "Exact company, product, commercial, contact, and legal wording is awaiting publication approval.",
      },
      {
        question: "Where can the source text be checked?",
        answer: "The Sources section links directly to the current official pages listed in this Preview.",
      },
    ],
  },
  footer: {
    notice: "Preview only. This application has no form, upload, analytics, or contact capture.",
  },
} as const;
