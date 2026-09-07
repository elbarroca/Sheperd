import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import type { NextApiRequest, NextApiResponse } from "next";

import pilotHandler from "../../pages/api/pilot";

const resend = vi.hoisted(() => ({
  client: vi.fn(),
  send: vi.fn(),
}));

vi.mock("resend", () => ({
  Resend: class MockResend {
    emails = {
      send: resend.send,
    };

    constructor(apiKey: string) {
      resend.client(apiKey);
    }
  },
}));

vi.mock(
  "@/lib/pilot-request",
  async () => import("../../lib/pilot-request"),
);

interface ApiResponse {
  ok: boolean;
  message?: string;
}

interface RecordedResponse {
  body: ApiResponse | undefined;
  headers: Record<string, string>;
  response: NextApiResponse<ApiResponse>;
  statusCode: number | undefined;
}

const validRequestBody = {
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

const expectedEmailText = [
  "New SheperD pilot request",
  "",
  "Name: Jane Smith",
  "Work email: jane@example.com",
  "Company: Example Imports",
  "Role: Controller / AP leader",
  "Estimated annual import volume: 1,000–5,000",
  "Review context: Recurring carrier charges need a clearer review path.",
  "Submission ID: 123e4567-e89b-42d3-a456-426614174000",
].join("\n");

const deliveryEnvironment = {
  PILOT_DELIVERY_ENABLED: "true",
  RESEND_API_KEY: "re_test_key",
  SHEPERD_PILOT_FROM_EMAIL: "SheperD Website <pilot@sheperd.io>",
  SHEPERD_PILOT_TO_EMAIL: "ops@sheperd.io",
};

function stubDeliveryEnvironment(
  overrides: Partial<typeof deliveryEnvironment> = {},
): void {
  const environment = { ...deliveryEnvironment, ...overrides };
  for (const [name, value] of Object.entries(environment)) {
    vi.stubEnv(name, value);
  }
}

function createRequest(
  overrides: Partial<
    Pick<NextApiRequest, "body" | "headers" | "method">
  > = {},
): NextApiRequest {
  return {
    body: validRequestBody,
    headers: {
      "x-sheperd-form": "pilot-request",
    },
    method: "POST",
    ...overrides,
  } as NextApiRequest;
}

function createResponse(): RecordedResponse {
  const recorded = {
    body: undefined,
    headers: {},
    statusCode: undefined,
  } as RecordedResponse;

  const response = {
    json(body: ApiResponse): NextApiResponse<ApiResponse> {
      recorded.body = body;
      return response;
    },
    setHeader(name: string, value: string): NextApiResponse<ApiResponse> {
      recorded.headers[name] = value;
      return response;
    },
    status(statusCode: number): NextApiResponse<ApiResponse> {
      recorded.statusCode = statusCode;
      return response;
    },
  } as unknown as NextApiResponse<ApiResponse>;

  recorded.response = response;
  return recorded;
}

async function invoke(
  requestOverrides: Partial<
    Pick<NextApiRequest, "body" | "headers" | "method">
  > = {},
): Promise<RecordedResponse> {
  const recorded = createResponse();
  await pilotHandler(createRequest(requestOverrides), recorded.response);
  return recorded;
}

describe("pilot API delivery boundary", () => {
  beforeEach(() => {
    vi.stubEnv("PILOT_DELIVERY_ENABLED", "false");
    vi.stubEnv("RESEND_API_KEY", "");
    vi.stubEnv("SHEPERD_PILOT_FROM_EMAIL", "");
    vi.stubEnv("SHEPERD_PILOT_TO_EMAIL", "");

    resend.client.mockReset();
    resend.send.mockReset();
  });

  afterEach(() => {
    vi.unstubAllEnvs();
  });

  it("rejects non-POST requests before constructing a delivery client", async () => {
    const result = await invoke({ method: "GET" });

    expect(result.statusCode).toBe(405);
    expect(result.headers).toEqual({ Allow: "POST" });
    expect(result.body).toEqual({
      ok: false,
      message: "Method not allowed.",
    });
    expect(resend.client).not.toHaveBeenCalled();
    expect(resend.send).not.toHaveBeenCalled();
  });

  it("rejects requests without the pilot form header before delivery", async () => {
    const result = await invoke({ headers: {} });

    expect(result.statusCode).toBe(403);
    expect(result.body).toEqual({
      ok: false,
      message: "Invalid form request.",
    });
    expect(resend.client).not.toHaveBeenCalled();
    expect(resend.send).not.toHaveBeenCalled();
  });

  it("does not construct or send through Resend while delivery is disabled", async () => {
    const result = await invoke();

    expect(result.statusCode).toBe(503);
    expect(result.body).toEqual({
      ok: false,
      message: "Pilot delivery is not configured.",
    });
    expect(resend.client).not.toHaveBeenCalled();
    expect(resend.send).not.toHaveBeenCalled();
  });

  it.each([
    ["the API key is missing", { RESEND_API_KEY: "" }],
    ["the from address is missing", { SHEPERD_PILOT_FROM_EMAIL: "" }],
    ["the recipient is missing", { SHEPERD_PILOT_TO_EMAIL: "" }],
  ])("does not construct Resend when %s", async (_caseName, missing) => {
    stubDeliveryEnvironment(missing);

    const result = await invoke();

    expect(result.statusCode).toBe(503);
    expect(result.body).toEqual({
      ok: false,
      message: "Pilot delivery is not configured.",
    });
    expect(resend.client).not.toHaveBeenCalled();
    expect(resend.send).not.toHaveBeenCalled();
  });

  it("rejects malformed payloads without constructing or sending", async () => {
    stubDeliveryEnvironment();

    const result = await invoke({
      body: {
        ...validRequestBody,
        workEmail: "not-an-email",
      },
    });

    expect(result.statusCode).toBe(400);
    expect(result.body).toEqual({
      ok: false,
      message: "Please check every pilot request field.",
    });
    expect(resend.client).not.toHaveBeenCalled();
    expect(resend.send).not.toHaveBeenCalled();
  });

  it("accepts a honeypot request without constructing or sending", async () => {
    stubDeliveryEnvironment();

    const result = await invoke({
      body: {
        ...validRequestBody,
        website: "https://spam.example",
      },
    });

    expect(result.statusCode).toBe(202);
    expect(result.body).toEqual({ ok: true });
    expect(resend.client).not.toHaveBeenCalled();
    expect(resend.send).not.toHaveBeenCalled();
  });

  it("sends the approved plain-text payload with routing and idempotency data", async () => {
    stubDeliveryEnvironment();
    resend.send.mockResolvedValue({
      data: { id: "email_123" },
      error: null,
    });

    const result = await invoke();

    expect(result.statusCode).toBe(200);
    expect(result.body).toEqual({ ok: true });
    expect(resend.client).toHaveBeenCalledWith("re_test_key");
    expect(resend.send).toHaveBeenCalledTimes(1);
    expect(resend.send).toHaveBeenCalledWith(
      {
        from: "SheperD Website <pilot@sheperd.io>",
        replyTo: validRequestBody.workEmail,
        subject: "SheperD pilot request — Example Imports",
        text: expectedEmailText,
        to: ["ops@sheperd.io"],
      },
      {
        idempotencyKey:
          "sheperd-pilot-123e4567-e89b-42d3-a456-426614174000",
      },
    );
  });

  it("returns a delivery failure when Resend reports an error", async () => {
    stubDeliveryEnvironment();
    resend.send.mockResolvedValue({
      data: null,
      error: { message: "provider rejected the request" },
    });

    const result = await invoke();

    expect(result.statusCode).toBe(502);
    expect(result.body).toEqual({
      ok: false,
      message: "The pilot request could not be delivered.",
    });
    expect(resend.send).toHaveBeenCalledTimes(1);
  });

  it("returns a delivery failure when Resend throws", async () => {
    stubDeliveryEnvironment();
    resend.send.mockRejectedValue(new Error("provider unavailable"));

    const result = await invoke();

    expect(result.statusCode).toBe(502);
    expect(result.body).toEqual({
      ok: false,
      message: "The pilot request could not be delivered.",
    });
    expect(resend.send).toHaveBeenCalledTimes(1);
  });
});
