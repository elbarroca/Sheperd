import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it, vi } from "vitest";
import type { MonthlyRollup, ReportPayload } from "@/lib/research-api";

const api = vi.hoisted(() => ({
  getDailyReports: vi.fn(),
  getMonthlyRollups: vi.fn(),
  getResearchHealth: vi.fn(),
  getResearchSourceExplorer: vi.fn(),
  getResearchSourceFacets: vi.fn(),
  getWeeklyReport: vi.fn(),
  getWeeklyReports: vi.fn(),
}));

vi.mock("@/lib/research-api", () => api);
vi.mock("@/components/report-accordion", () => ({
  ReportAccordion: ({ report }: { report: ReportPayload }) => (
    <div data-testid="report-accordion">{report.brief.run_id}</div>
  ),
  ReportLink: ({ runId }: { runId: string }) => <div data-testid="report-link">{runId}</div>,
  UnavailableState: ({ error }: { error: string }) => <div role="alert">{error}</div>,
}));

import HomePage from "./page";
import MonthlyPage from "./monthly/page";
import ReportPage from "./reports/[run_id]/page";
import SourcesPage from "./sources/page";

const validReport = {
  brief: { run_id: "run-1", title: "Report", covered_from: "2026-08-01", covered_until: "2026-08-07" },
} as ReportPayload;

describe("production report routes", () => {
  it("renders the weekly list and detail accordion from API data", async () => {
    api.getResearchHealth.mockResolvedValue({
      status: "ok",
      data: { status: "pass", migration_version: "0010", branch_id: "main", database: "neondb" },
    });
    api.getDailyReports.mockResolvedValue({ status: "ok", data: { reports: [], count: 0 } });
    api.getWeeklyReports.mockResolvedValue({ status: "ok", data: { reports: [validReport], count: 1 } });
    api.getWeeklyReport.mockResolvedValue({ status: "ok", data: validReport });

    expect(renderToStaticMarkup(await HomePage())).toContain("run-1");
    expect(renderToStaticMarkup(await ReportPage({ params: Promise.resolve({ run_id: "run-1" }) }))).toContain("report-accordion");
  });

  it("renders an explicit unavailable state for each production route", async () => {
    const unavailable = { status: "unavailable", error: "Research API is unavailable" } as const;
    api.getResearchHealth.mockResolvedValue(unavailable);
    api.getDailyReports.mockResolvedValue(unavailable);
    api.getWeeklyReports.mockResolvedValue(unavailable);
    api.getWeeklyReport.mockResolvedValue(unavailable);
    api.getMonthlyRollups.mockResolvedValue(unavailable);

    expect(renderToStaticMarkup(await HomePage())).toContain("Research API is unavailable");
    expect(renderToStaticMarkup(await ReportPage({ params: Promise.resolve({ run_id: "run-1" }) }))).toContain("Research API is unavailable");
    expect(renderToStaticMarkup(await MonthlyPage())).toContain("Research API is unavailable");
  });

  it("renders monthly data from the API without fallback content", async () => {
    const rollup: MonthlyRollup = { month: "2026-08-01", signals: 2, runs: 1, geographies: ["US"] };
    api.getMonthlyRollups.mockResolvedValue({ status: "ok", data: { rollups: [rollup] } });

    expect(renderToStaticMarkup(await MonthlyPage())).toContain("2026-08-01");
  });

  it("renders the paginated source explorer from Neon records", async () => {
    api.getResearchSourceExplorer.mockResolvedValue({
      status: "ok",
      data: {
        items: [{
          source: {
            url: "https://example.com/article",
            title: "Article title",
            publisher: "Example",
            published_at: null,
            retrieved_at: "2026-08-19T00:00:00Z",
            source_kind: "web",
            snippet: "Original summary",
            topics: [],
            geographies: ["US"],
            lane: "ports",
            is_seed: false,
            evidence_status: "cited",
            region: "us",
            language_code: "en",
            freshness_status: "current",
            extraction_status: "succeeded",
          },
          distillation: {
            source_url: "https://example.com/article",
            summary: "English summary",
            summary_original: "Original summary",
            key_points: ["Key point"],
            key_points_original: [],
            entities: [],
            signals: [],
            claims: [],
            limitations: [],
            published_at: null,
            model_id: "google/gemma:free",
            prompt_version: "distill",
            evidence_status: "cited",
            content_hash: "hash",
            source_language: "en",
            translation_status: "not_needed",
          },
          claims: [],
          source_hash: "hash",
        }],
        page: 1,
        page_size: 24,
        total: 1,
        has_more: false,
      },
    });
    api.getResearchSourceFacets.mockResolvedValue({
      status: "ok",
      data: {
        regions: ["us"],
        languages: ["en"],
        freshness: ["current"],
        authority: ["secondary"],
        source_types: ["trade_media"],
        lanes: ["ports"],
        evidence_states: ["cited"],
      },
    });

    const markup = renderToStaticMarkup(await SourcesPage({ searchParams: Promise.resolve({}) }));
    expect(markup).toContain("Article title");
    expect(markup).toContain("English summary");
    expect(markup).toContain("hash");
  });
});
