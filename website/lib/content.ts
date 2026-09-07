export const navigationItems = [
  { label: "How it works", href: "#process" },
  { label: "What we review", href: "#evidence" },
  { label: "Pilot scope", href: "#pilot-scope" },
  { label: "Trust", href: "#trust" },
] as const;

export const processSteps = [
  {
    number: "01",
    title: "Share the invoices",
    description:
      "Start with the invoices you already have. Agree the review scope and a secure way to share the shipment records.",
  },
  {
    number: "02",
    title: "We review and coordinate",
    description:
      "SheperD checks the charges against shipment events and terms, builds the supporting record, and handles the carrier questions.",
  },
  {
    number: "03",
    title: "Follow the resolution",
    description:
      "Your point of contact follows the dispute and carrier response, keeping you informed of any credit or refund. Outcomes depend on the case.",
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
      "Define the invoices, review period, and support your finance or logistics team needs, with one point of contact for the work.",
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
      "Agree responsibilities, carrier coordination, reporting, and a secure data path before work begins. Payment and credit arrangements are scoped separately.",
  },
] as const;

export const faqItems = [
  {
    group: "Getting started",
    question: "What happens after I request a pilot?",
    answer:
      "Online intake is currently unavailable. Contact the team by email or phone to discuss your invoices, priorities, and review scope. Agree a secure handoff before sharing files.",
  },
  {
    group: "Scope and outcomes",
    question: "What does detention and demurrage mean?",
    answer:
      "Demurrage concerns a container staying at a marine terminal beyond its free time. Detention concerns extended use of intermodal equipment. The applicable terms, dates, and shipment facts determine how a charge should be reviewed.",
  },
  {
    group: "Getting started",
    question: "Is SheperD software?",
    answer:
      "SheperD is a managed service for U.S. importers. A dedicated team handles invoice review, carrier coordination, and disputes. There is no software for your team to install or operate.",
  },
  {
    group: "Scope and outcomes",
    question: "Can SheperD help with carrier payments?",
    answer:
      "Payment and cargo-release support can be discussed alongside invoice review. Any payment, financing, or credit arrangement requires a separate agreement; requesting information does not arrange a payment or release.",
  },
  {
    group: "Getting started",
    question: "Do I need to upload invoices now?",
    answer:
      "No. This website does not accept invoice files. Any file transfer would be a separate secure step after scope and data handling are agreed.",
  },
  {
    group: "Scope and outcomes",
    question: "Does SheperD guarantee a refund?",
    answer:
      "No. Eligibility and value depend on invoice language, dates, governing terms, operational facts, and available evidence. The page does not promise a refund.",
  },
  {
    group: "Scope and outcomes",
    question: "What if the review does not support a recovery path?",
    answer:
      "The team explains what the records support, what is missing, and whether there is a next step. A review can end without a recovery claim.",
  },
  {
    group: "Getting started",
    question: "What does the pilot cost?",
    answer:
      "The team will confirm scope and commercial terms before work begins. Pricing and any payment, financing, or credit arrangement are agreed separately.",
  },
  {
    group: "Getting started",
    question: "How long does a review take?",
    answer:
      "Timing depends on the records available and the carrier response. The team agrees the review scope and update cadence with you before work begins.",
  },
  {
    group: "Scope and outcomes",
    question: "Is the outcome cash or a carrier credit?",
    answer:
      "A resolution may be a cash refund or a carrier credit. SheperD tracks the actual outcome and makes the distinction clear in its reporting.",
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
  url: "https://sheperd.io/",
  contactEmail: "avi@sheperd.io",
  contactPhone: "+972537252334",
  contactPhoneLabel: "+972 53 7252 334",
  description:
    "Managed detention and demurrage support for U.S. importers, from invoice review and carrier coordination to disputes and recovery.",
} as const;
