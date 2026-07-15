export const navigationItems = [
  { label: "How it works", href: "#how-it-works" },
  { label: "Container journey", href: "#container-journey" },
  { label: "Our mission", href: "#mission" },
  { label: "Dashboard", href: "#recovery-dashboard" },
] as const;

export const marketStats = [
  {
    value: "$2.1B",
    label: "Estimated shipping-container overcharges each year",
  },
  {
    value: "$6.2B",
    label: "Estimated past-charge recovery opportunity",
  },
  {
    value: "3 years",
    label: "Of historical container charges to review",
  },
] as const;

export const benefits = [
  {
    icon: "cost",
    title: "Zero upfront cost",
    description: "No recovery, no fee.",
  },
  {
    icon: "workload",
    title: "Less internal work",
    description: "SheperD manages the audit and dispute process.",
  },
  {
    icon: "visibility",
    title: "Every charge tracked",
    description: "See each invoice, dispute, and approved refund.",
  },
] as const;

export const recoverySteps = [
  {
    icon: "invoice",
    number: "01",
    title: "Send container invoices",
    description: "Upload demurrage and detention invoices in minutes.",
  },
  {
    icon: "audit",
    number: "02",
    title: "We audit every charge",
    description: "160+ automated checks review dates, free time, and invoice details.",
  },
  {
    icon: "refund",
    number: "03",
    title: "Recover eligible fees",
    description: "SheperD manages the dispute and tracks approved refunds.",
  },
] as const;

export const containerEvents = [
  {
    icon: "freeTime",
    title: "Last free day (LFD)",
    description:
      "The stated cutoff for terminal free time on the applicable record.",
  },
  {
    icon: "availability",
    title: "Terminal availability",
    description:
      "Release status, holds, pickup windows, closures, and appointment access show whether the box could be retrieved.",
  },
  {
    icon: "gateOut",
    title: "Gate-out",
    description:
      "The timestamp when the loaded container leaves the marine terminal.",
  },
  {
    icon: "emptyReturn",
    title: "Empty return",
    description:
      "The timestamp and location where the carrier accepts the empty equipment back.",
  },
  {
    icon: "invoice",
    title: "Invoice line items",
    description:
      "Each billed day and fee matched against the event timeline and governing terms.",
  },
] as const;

export const missionOutcomes = [
  {
    icon: "prevent",
    title: "Prevent leakage",
    description:
      "Catch questionable container charges before they disappear into operating costs.",
  },
  {
    icon: "recover",
    title: "Recover eligible fees",
    description:
      "Build the evidence and manage each dispute from invoice to decision.",
  },
  {
    icon: "accountability",
    title: "Create accountability",
    description:
      "Give teams one visible record of charges, claims, and approved refunds.",
  },
] as const;

export const volumeOptions = [
  "Under 1,000",
  "1,000–5,000",
  "5,000–20,000",
  "20,000+",
] as const;

export const liveSource = {
  url: "https://www.sheperd.io/",
  checked: "2026-07-15",
  contactEmail: "info@sheperd.io",
  linkedin:
    "https://www.linkedin.com/company/sheperdio/?viewAsMember=true",
} as const;
