import { describe, expect, it } from "vitest";

import {
  createPilotEmailText,
  parsePilotRequest,
} from "../../lib/pilot-request";

const validRequest = {
  submissionId: "123e4567-e89b-42d3-a456-426614174000",
  fullName: "Jane Smith",
  workEmail: "jane@example.com",
  company: "Example Imports",
  role: "Controller / AP leader",
  annualVolume: "1,000–5,000",
  reviewContext: "Recurring carrier charges need a clearer review path.",
  consent: "yes",
  website: "",
};

describe("pilot request boundary", () => {
  it("accepts a complete request and formats delivery text", () => {
    const result = parsePilotRequest(validRequest);
    expect(result.success).toBe(true);

    if (!result.success) return;

    const text = createPilotEmailText(result.data);
    expect(text).toContain("New SheperD pilot request");
    expect(text).toContain("Company: Example Imports");
    expect(text).toContain("Role: Controller / AP leader");
  });

  it("rejects malformed email, missing consent, and unknown volume", () => {
    expect(
      parsePilotRequest({
        ...validRequest,
        workEmail: "not-an-email",
      }).success,
    ).toBe(false);
    expect(
      parsePilotRequest({ ...validRequest, consent: "" }).success,
    ).toBe(false);
    expect(
      parsePilotRequest({ ...validRequest, annualVolume: "Unlimited" }).success,
    ).toBe(false);
  });

  it("rejects control characters and invalid identifiers", () => {
    expect(
      parsePilotRequest({ ...validRequest, submissionId: "not-a-uuid" }).success,
    ).toBe(false);
    expect(
      parsePilotRequest({ ...validRequest, company: "Example\nBcc: someone" })
        .success,
    ).toBe(false);
  });

  it("retains a populated honeypot for silent bot handling", () => {
    const result = parsePilotRequest({ ...validRequest, website: "spam.test" });
    expect(result.success).toBe(true);
    if (result.success) expect(result.data.website).toBe("spam.test");
  });
});
