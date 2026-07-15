import { volumeOptions } from "./content";

type AnnualVolume = (typeof volumeOptions)[number];

export interface AuditRequest {
  submissionId: string;
  fullName: string;
  workEmail: string;
  phone: string;
  company: string;
  city: string;
  state: string;
  annualVolume: AnnualVolume;
  website: string;
}

type ParseResult =
  | { success: true; data: AuditRequest }
  | { success: false; message: string };

const FIELD_LIMITS = {
  submissionId: 36,
  fullName: 100,
  workEmail: 254,
  phone: 40,
  company: 120,
  city: 80,
  state: 80,
  annualVolume: 20,
  website: 200,
} as const;

const EMAIL_PATTERN = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
const UUID_PATTERN =
  /^[0-9a-f]{8}-[0-9a-f]{4}-[1-8][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;
const UNSAFE_CONTROL_PATTERN = /[\u0000-\u001f\u007f]/;

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function readString(
  record: Record<string, unknown>,
  field: keyof typeof FIELD_LIMITS,
): string | null {
  const value = record[field];
  if (typeof value !== "string") return null;

  const normalized = value.trim();
  if (
    normalized.length > FIELD_LIMITS[field] ||
    UNSAFE_CONTROL_PATTERN.test(normalized)
  ) {
    return null;
  }

  return normalized;
}

export function parseAuditRequest(value: unknown): ParseResult {
  if (!isRecord(value)) {
    return { success: false, message: "Invalid audit request." };
  }

  const submissionId = readString(value, "submissionId");
  const fullName = readString(value, "fullName");
  const workEmail = readString(value, "workEmail");
  const phone = readString(value, "phone");
  const company = readString(value, "company");
  const city = readString(value, "city");
  const state = readString(value, "state");
  const annualVolume = readString(value, "annualVolume");
  const website = readString(value, "website");

  if (
    !submissionId ||
    !UUID_PATTERN.test(submissionId) ||
    !fullName ||
    !workEmail ||
    !EMAIL_PATTERN.test(workEmail) ||
    !phone ||
    !company ||
    !city ||
    !state ||
    !annualVolume ||
    !volumeOptions.some((option) => option === annualVolume) ||
    website === null
  ) {
    return { success: false, message: "Please check every audit request field." };
  }

  return {
    success: true,
    data: {
      submissionId,
      fullName,
      workEmail,
      phone,
      company,
      city,
      state,
      annualVolume: annualVolume as AnnualVolume,
      website,
    },
  };
}

export function createAuditEmailText(request: AuditRequest): string {
  return [
    "New free container invoice audit request",
    "",
    `Name: ${request.fullName}`,
    `Work email: ${request.workEmail}`,
    `Phone: ${request.phone}`,
    `Company: ${request.company}`,
    `Location: ${request.city}, ${request.state}`,
    `Estimated annual import volume: ${request.annualVolume}`,
    `Submission ID: ${request.submissionId}`,
  ].join("\n");
}
