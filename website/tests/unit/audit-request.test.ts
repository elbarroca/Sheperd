import { describe, expect, it } from "vitest";

import {
  createAuditEmailText,
  parseAuditRequest,
} from "../../lib/audit-request";

const validRequest = {
  submissionId: "123e4567-e89b-42d3-a456-426614174000",
  fullName: "Jane Smith",
  workEmail: "jane@example.com",
  phone: "555-000-0000",
  company: "Example Imports",
  city: "Los Angeles",
  state: "CA",
  annualVolume: "Under 1,000",
  website: "",
};

describe("audit request boundary", () => {
  it("accepts a complete request and formats the delivery text", () => {
    const result = parseAuditRequest(validRequest);
    expect(result.success).toBe(true);

    if (!result.success) return;

    const text = createAuditEmailText(result.data);
    expect(text).toContain("New free container invoice audit request");
    expect(text).toContain("Company: Example Imports");
    expect(text).toContain("Estimated annual import volume: Under 1,000");
  });

  it("rejects malformed email and unknown volume values", () => {
    expect(
      parseAuditRequest({
        ...validRequest,
        workEmail: "not-an-email",
        annualVolume: "Unlimited",
      }).success,
    ).toBe(false);
  });

  it("rejects missing fields, invalid identifiers, and control characters", () => {
    expect(parseAuditRequest({ ...validRequest, company: "" }).success).toBe(
      false,
    );
    expect(
      parseAuditRequest({ ...validRequest, submissionId: "not-a-uuid" }).success,
    ).toBe(false);
    expect(
      parseAuditRequest({ ...validRequest, fullName: "Jane\u0000Smith" }).success,
    ).toBe(false);
    expect(
      parseAuditRequest({ ...validRequest, company: "Example\nBcc: someone" })
        .success,
    ).toBe(false);
  });

  it("retains a populated honeypot so the API can silently accept bots", () => {
    const result = parseAuditRequest({ ...validRequest, website: "spam.test" });
    expect(result.success).toBe(true);
    if (result.success) expect(result.data.website).toBe("spam.test");
  });
});
