export const navigationItems = [
  { label: "How it works", href: "#process" },
  { label: "What we review", href: "#evidence" },
  { label: "Pilot scope", href: "#pilot-scope" },
  { label: "Trust", href: "#trust" },
] as const;

export const processSteps = [
  {
    number: "01",
    title: "Bring the invoice and operating record",
    description:
      "Start with the charge as billed, then gather the dates, events, and terms that explain what happened.",
  },
  {
    number: "02",
    title: "Build the case from the evidence",
    description:
      "SheperD organizes the billing record, operational timeline, governing terms, and visible gaps into one review path.",
  },
  {
    number: "03",
    title: "Support the dispute and track the outcome",
    description:
      "Where the evidence supports a case, the pilot can define next steps toward a carrier credit or refund. No outcome is guaranteed.",
  },
] as const;

export const evidenceLayers = [
  {
    icon: "billing",
    title: "Billing record",
    description:
      "Invoice line items, bill of lading references, payment state, charge dates, and the party identified on the bill.",
    label: "What was billed",
  },
  {
    icon: "timeline",
    title: "Operational timeline",
    description:
      "Availability, pickup, return, terminal timing, appointments, holds, closures, and communications around the container.",
    label: "What happened",
  },
  {
    icon: "terms",
    title: "Governing terms",
    description:
      "Free-time terms, tariff or contract language, route, source dates, and the version of the rule or record that applies.",
    label: "What governs",
  },
] as const;

export const pilotScope = [
  {
    number: "01",
    title: "A focused record review",
    description:
      "Start with the charge, the owner, the review period, and the records already available.",
  },
  {
    number: "02",
    title: "A clear evidence map",
    description:
      "See which billing, operating, and governing records are present, missing, or still need human review.",
  },
  {
    number: "03",
    title: "A next-step conversation",
    description:
      "Agree the scope, data path, responsibilities, and decision boundary before any secure file handoff.",
  },
] as const;

export const faqItems = [
  {
    question: "What happens after I request a pilot?",
    answer:
      "Pilot intake is currently unavailable, and the form does not accept or send your details. When intake opens, the first conversation will cover scope, owners, available records, and the next data step.",
  },
  {
    question: "Do I need to upload invoices now?",
    answer:
      "No. This website does not accept invoice files. Any file transfer would be a separate secure step after scope and data handling are agreed.",
  },
  {
    question: "Does SheperD guarantee a refund?",
    answer:
      "No. Eligibility and value depend on invoice language, dates, governing terms, operational facts, and available evidence. The page does not promise a refund.",
  },
  {
    question: "What if the review does not support a recovery path?",
    answer:
      "The review should make that boundary clear and identify the missing evidence or next decision rather than manufacture a result.",
  },
  {
    question: "What does the pilot cost?",
    answer:
      "Commercial terms are agreed before any engagement. No fee or success-fee percentage is published on this website.",
  },
  {
    question: "How long does a review take?",
    answer:
      "Timing is scoped with the pilot owner after the records, review capacity, and responsibilities are confirmed. No blanket SLA is promised.",
  },
  {
    question: "Is the outcome cash or a carrier credit?",
    answer:
      "That depends on the carrier process and case facts. A pilot must distinguish cash refunds from credits and record what was actually realized.",
  },
] as const;

export const volumeOptions = [
  "Under 1,000",
  "1,000–5,000",
  "5,000–20,000",
  "20,000+",
] as const;

export const roleOptions = [
  "CFO / finance leader",
  "Controller / AP leader",
  "Supply chain / logistics leader",
  "Operations / data owner",
  "Other",
] as const;

export const sourceLinks = [
  {
    issuer: "eCFR",
    title: "46 CFR Part 541",
    href: "https://www.ecfr.gov/current/title-46/chapter-IV/subchapter-B/part-541",
  },
  {
    issuer: "Federal Maritime Commission",
    title: "Charge Complaint interim guidance",
    href: "https://www.fmc.gov/ocean-shipping-reform-act-of-2022-implementation/guidance-on-charge-complaint-interim-procedure/",
  },
  {
    issuer: "U.S. Code",
    title: "46 U.S.C. §41301",
    href: "https://www.govinfo.gov/link/uscode/46/41301?link-type=html&year=mostrecent",
  },
] as const;

export const liveSource = {
  contactEmail: "info@sheperd.io",
  linkedin: "https://www.linkedin.com/company/sheperdio/?viewAsMember=true",
} as const;
