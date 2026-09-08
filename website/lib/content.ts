export const navigationItems = [
  { label: "How it works", href: "/how-it-works" },
  { label: "For importers", href: "/for-importers" },
  { label: "About", href: "/about" },
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
