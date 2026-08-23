import { beforeEach, describe, expect, it, vi } from "vitest";
import type { ReportPayload } from "./research-api";
import {
  getResearchSourceExplorer,
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

  it("reads the paginated source explorer with filters preserved", async () => {
    fetchMock.mockResolvedValueOnce(jsonResponse({
      items: [{
        source: {
          url: "https://example.com/source",
          title: "Source",
          publisher: "Example",
          published_at: null,
          retrieved_at: "2026-08-19T00:00:00Z",
          source_kind: "web",
          snippet: "Snippet",
          topics: [],
          geographies: ["US"],
          lane: "ports",
          is_seed: false,
          evidence_status: "unverified",
        },
        distillation: null,
        claims: [],
        source_hash: "hash",
      }],
      page: 2,
      page_size: 24,
      total: 25,
      has_more: false,
    }));

    const result = await getResearchSourceExplorer({
      page: 2,
      region: "us",
      language: "en",
    });

    expect(result.status).toBe("ok");
    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining("/api/sources/explorer?"),
      expect.anything(),
    );
    expect(fetchMock.mock.calls[0]?.[0]).toContain("page=2");
    expect(fetchMock.mock.calls[0]?.[0]).toContain("region=us");
    expect(fetchMock.mock.calls[0]?.[0]).toContain("language=en");
  });

  it("rejects malformed article insight packets in source explorer data", async () => {
    fetchMock.mockResolvedValueOnce(jsonResponse({
      items: [{
        source: {
          url: "https://example.com/source",
          title: "Source",
          publisher: "Example",
          published_at: null,
          retrieved_at: "2026-08-19T00:00:00Z",
          source_kind: "web",
          snippet: "Snippet",
          topics: [],
          geographies: ["US"],
          lane: "ports",
          is_seed: false,
          evidence_status: "unverified",
        },
        distillation: {
          source_url: "https://example.com/source",
          summary: "Summary",
          key_points: ["Point one", "Point two"],
          entities: [],
          signals: [],
          claims: [],
          limitations: [],
          published_at: null,
          model_id: "google/gemma:free",
          prompt_version: "distill-v6",
          evidence_status: "mixed",
          content_hash: "hash",
          risk_assessment: {
            status: "deferred",
            statement: "Bad status",
            why_it_matters: "Should be rejected",
            next_step: "Fix backend data",
          },
        },
        claims: [],
        source_hash: "hash",
      }],
      page: 1,
      page_size: 24,
      total: 1,
      has_more: false,
    }));

    await expect(getResearchSourceExplorer()).resolves.toEqual({
      status: "unavailable",
      error: "Research API returned malformed data",
    });
  });

  it("rejects supported article insights without evidence", async () => {
    fetchMock.mockResolvedValueOnce(jsonResponse({
      items: [{
        source: {
          url: "https://example.com/source",
          title: "Source",
          publisher: "Example",
          published_at: null,
          retrieved_at: "2026-08-19T00:00:00Z",
          source_kind: "web",
          snippet: "Snippet",
          topics: [],
          geographies: ["US"],
          lane: "ports",
          is_seed: false,
          evidence_status: "unverified",
        },
        distillation: {
          source_url: "https://example.com/source",
          summary: "Summary",
          key_points: ["Point one", "Point two"],
          entities: [],
          signals: [],
          claims: [],
          limitations: [],
          published_at: null,
          model_id: "google/gemma:free",
          prompt_version: "distill-v6",
          evidence_status: "mixed",
          content_hash: "hash",
          risk_assessment: {
            status: "supported",
            statement: "Supported risk",
            why_it_matters: "Requires evidence",
            next_step: "Add locator or excerpt",
          },
          opportunity_assessment: {
            status: "not_observed",
            statement: "No opening observed",
            why_it_matters: "No action yet",
            next_step: "Check next run",
          },
        },
        claims: [],
        source_hash: "hash",
      }],
      page: 1,
      page_size: 24,
      total: 1,
      has_more: false,
    }));

    await expect(getResearchSourceExplorer()).resolves.toEqual({
      status: "unavailable",
      error: "Research API returned malformed data",
    });
  });

  it("rejects article insights with placeholder or whitespace-only required text", async () => {
    fetchMock.mockResolvedValueOnce(jsonResponse({
      items: [{
        source: {
          url: "https://example.com/source",
          title: "Source",
          publisher: "Example",
          published_at: null,
          retrieved_at: "2026-08-19T00:00:00Z",
          source_kind: "web",
          snippet: "Snippet",
          topics: [],
          geographies: ["US"],
          lane: "ports",
          is_seed: false,
          evidence_status: "unverified",
        },
        distillation: {
          source_url: "https://example.com/source",
          summary: "Summary",
          key_points: ["Point one", "Point two"],
          entities: [],
          signals: [],
          claims: [],
          limitations: [],
          published_at: null,
          model_id: "google/gemma:free",
          prompt_version: "distill-v6",
          evidence_status: "mixed",
          content_hash: "hash",
          risk_assessment: {
            status: "uncertain",
            statement: "   ",
            why_it_matters: "Not recorded in this run.",
            next_step: "Check the next run",
          },
        },
        claims: [],
        source_hash: "hash",
      }],
      page: 1,
      page_size: 24,
      total: 1,
      has_more: false,
    }));

    await expect(getResearchSourceExplorer()).resolves.toEqual({
      status: "unavailable",
      error: "Research API returned malformed data",
    });
  });

  it("preserves explicit not observed and uncertain insight statuses", async () => {
    for (const status of ["not_observed", "uncertain"] as const) {
      fetchMock.mockResolvedValueOnce(jsonResponse({
        items: [{
          source: {
            url: "https://example.com/source",
            title: "Source",
            publisher: "Example",
            published_at: null,
            retrieved_at: "2026-08-19T00:00:00Z",
            source_kind: "web",
            snippet: "Snippet",
            topics: [],
            geographies: ["US"],
            lane: "ports",
            is_seed: false,
            evidence_status: "unverified",
          },
          distillation: {
            source_url: "https://example.com/source",
            summary: "Summary",
            key_points: ["Point one", "Point two"],
            entities: [],
            signals: [],
            claims: [],
            limitations: [],
            published_at: null,
            model_id: "google/gemma:free",
            prompt_version: "distill-v6",
            evidence_status: "mixed",
            content_hash: "hash",
            risk_assessment: {
              status,
              statement: "A clear statement.",
              why_it_matters: "The status is explicit.",
              next_step: "Review the next run.",
            },
          },
          claims: [],
          source_hash: "hash",
        }],
        page: 1,
        page_size: 24,
        total: 1,
        has_more: false,
      }));

      await expect(getResearchSourceExplorer()).resolves.toMatchObject({ status: "ok" });
    }
  });

  it("rejects incomplete as an article insight status", async () => {
    fetchMock.mockResolvedValueOnce(jsonResponse({
      items: [{
        source: {
          url: "https://example.com/source",
          title: "Source",
          publisher: "Example",
          published_at: null,
          retrieved_at: "2026-08-19T00:00:00Z",
          source_kind: "web",
          snippet: "Snippet",
          topics: [],
          geographies: ["US"],
          lane: "ports",
          is_seed: false,
          evidence_status: "unverified",
        },
        distillation: {
          source_url: "https://example.com/source",
          summary: "Summary",
          key_points: ["Point one", "Point two"],
          entities: [],
          signals: [],
          claims: [],
          limitations: [],
          published_at: null,
          model_id: "google/gemma:free",
          prompt_version: "distill-v6",
          evidence_status: "mixed",
          content_hash: "hash",
          risk_assessment: {
            status: "incomplete",
            statement: "A clear statement.",
            why_it_matters: "The status belongs to quality, not article insights.",
            next_step: "Review the quality status.",
          },
        },
        claims: [],
        source_hash: "hash",
      }],
      page: 1,
      page_size: 24,
      total: 1,
      has_more: false,
    }));

    await expect(getResearchSourceExplorer()).resolves.toEqual({
      status: "unavailable",
      error: "Research API returned malformed data",
    });
  });
});
