import { beforeEach, describe, expect, it, vi } from "vitest";
import type { ReportPayload } from "./research-api";
import {
  getMonthlyRollups,
  getResearchHealth,
  getWeeklyReport,
  getWeeklyReports,
} from "./research-api";

const fetchMock = vi.fn<typeof fetch>();

const validReport: ReportPayload = {
  brief: {
    run_id: "run-1",
    title: "Weekly brief",
    covered_from: "2026-08-12T00:00:00Z",
    covered_until: "2026-08-19T00:00:00Z",
    summary: "Summary",
    source_urls: [],
    limitations: [],
    review_state: "draft",
    evidence_status: "mixed",
    model_id: "model",
    prompt_version: "v1",
    executive_bullets: [],
    developments: [],
    risks: [],
    opportunities: [],
    uncertainties: [],
    follow_up_questions: [],
  },
  run: {
    run_id: "run-1",
    status: "succeeded",
    as_of: "2026-08-19T00:00:00Z",
    error: null,
    neon_branch_id: null,
    migration_version: "0008_audit_surfaces",
  },
  validation: { run_id: "run-1", status: "pass", citation_coverage: 1, lane_coverage: [], checks: [] },
  lane_coverage: [],
  models: ["model"],
  steps: [],
  tool_calls: [],
  sources: [],
  source_hashes: [],
  distillations: [],
  claims: [],
  signals: [],
  as_of: "2026-08-19T00:00:00Z",
  covered_from: "2026-08-12T00:00:00Z",
  covered_until: "2026-08-19T00:00:00Z",
};

function jsonResponse(payload: unknown, status = 200): Response {
  return new Response(JSON.stringify(payload), {
    status,
    headers: { "content-type": "application/json" },
  });
}

describe("research API runtime validation", () => {
  beforeEach(() => {
    fetchMock.mockReset();
    vi.stubGlobal("fetch", fetchMock);
  });

  it("returns unavailable for malformed health and weekly list payloads", async () => {
    fetchMock
      .mockResolvedValueOnce(jsonResponse({ status: 42 }))
      .mockResolvedValueOnce(jsonResponse({ reports: [{}], count: 1 }));

    await expect(getResearchHealth()).resolves.toEqual({
      status: "unavailable",
      error: "Research API returned malformed data",
    });
    await expect(getWeeklyReports()).resolves.toEqual({
      status: "unavailable",
      error: "Research API returned malformed data",
    });
  });

  it("returns unavailable for malformed report detail and monthly payloads", async () => {
    fetchMock
      .mockResolvedValueOnce(jsonResponse({ brief: null }))
      .mockResolvedValueOnce(jsonResponse({ rollups: [{ month: "2026-08", signals: "1" }] }));

    await expect(getWeeklyReport("run-1")).resolves.toEqual({
      status: "unavailable",
      error: "Research API returned malformed data",
    });
    await expect(getMonthlyRollups()).resolves.toEqual({
      status: "unavailable",
      error: "Research API returned malformed data",
    });
  });

  it("accepts validated health, weekly, detail, and monthly payloads", async () => {
    fetchMock
      .mockResolvedValueOnce(
        jsonResponse({ status: "pass", migration_version: "0008", branch_id: null, database: "test" }),
      )
      .mockResolvedValueOnce(jsonResponse({ reports: [validReport], count: 1 }))
      .mockResolvedValueOnce(jsonResponse(validReport))
      .mockResolvedValueOnce(jsonResponse({ rollups: [{ month: "2026-08-01", signals: 1, runs: 1, geographies: [] }] }));

    await expect(getResearchHealth()).resolves.toMatchObject({ status: "ok" });
    await expect(getWeeklyReports()).resolves.toMatchObject({ status: "ok" });
    await expect(getWeeklyReport("run-1")).resolves.toMatchObject({ status: "ok" });
    await expect(getMonthlyRollups()).resolves.toMatchObject({ status: "ok" });
  });

  it("rejects report details whose brief, run, or validation belongs to another run", async () => {
    const mismatchedReports: ReportPayload[] = [
      { ...validReport, brief: { ...validReport.brief, run_id: "run-2" } },
      { ...validReport, run: validReport.run ? { ...validReport.run, run_id: "run-2" } : null },
      {
        ...validReport,
        validation: validReport.validation
          ? { ...validReport.validation, run_id: "run-2" }
          : null,
      },
      { ...validReport, validation: null },
    ];

    for (const report of mismatchedReports) {
      fetchMock.mockResolvedValueOnce(jsonResponse(report));
      await expect(getWeeklyReport("run-1")).resolves.toEqual({
        status: "unavailable",
        error: "Research API returned malformed data",
      });
    }
  });

  it("returns unavailable for an unavailable HTTP response", async () => {
    fetchMock.mockResolvedValueOnce(jsonResponse({ error: "offline" }, 503));

    await expect(getResearchHealth()).resolves.toEqual({
      status: "unavailable",
      error: "API returned 503",
    });
  });
});
