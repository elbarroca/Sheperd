import { roleOptions, volumeOptions } from "./content";

type PilotRole = (typeof roleOptions)[number];
type AnnualVolume = (typeof volumeOptions)[number];

export interface PilotRequest {
  submissionId: string;
  fullName: string;
  workEmail: string;
  company: string;
  role: PilotRole;
  annualVolume: AnnualVolume;
  reviewContext: string;
  consent: "yes";
  website: string;
}

type ParseResult =
  | { success: true; data: PilotRequest }
  | { success: false; message: string };

const FIELD_LIMITS = {
  submissionId: 36,
  fullName: 100,
  workEmail: 254,
  company: 120,
  role: 80,
  annualVolume: 20,
  reviewContext: 1000,
  consent: 3,
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

export function parsePilotRequest(value: unknown): ParseResult {
  if (!isRecord(value)) {
    return { success: false, message: "Invalid pilot request." };
  }

  const submissionId = readString(value, "submissionId");
  const fullName = readString(value, "fullName");
  const workEmail = readString(value, "workEmail");
  const company = readString(value, "company");
  const role = readString(value, "role");
  const annualVolume = readString(value, "annualVolume");
  const reviewContext = readString(value, "reviewContext");
  const consent = readString(value, "consent");
  const website = readString(value, "website");

  if (
    !submissionId ||
    !UUID_PATTERN.test(submissionId) ||
    !fullName ||
    !workEmail ||
    !EMAIL_PATTERN.test(workEmail) ||
    !company ||
    !role ||
    !roleOptions.some((option) => option === role) ||
    !annualVolume ||
    !volumeOptions.some((option) => option === annualVolume) ||
    !reviewContext ||
    !consent ||
    consent !== "yes" ||
    website === null
  ) {
    return { success: false, message: "Please check every pilot request field." };
  }

  return {
    success: true,
    data: {
      submissionId,
      fullName,
      workEmail,
      company,
      role: role as PilotRole,
      annualVolume: annualVolume as AnnualVolume,
      reviewContext,
      consent: "yes",
      website,
    },
  };
}

export function createPilotEmailText(request: PilotRequest): string {
  return [
    "New SheperD pilot request",
    "",
    `Name: ${request.fullName}`,
    `Work email: ${request.workEmail}`,
    `Company: ${request.company}`,
    `Role: ${request.role}`,
    `Estimated annual import volume: ${request.annualVolume}`,
    `Review context: ${request.reviewContext}`,
    `Submission ID: ${request.submissionId}`,
  ].join("\n");
}
