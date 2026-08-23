import { renderToStaticMarkup } from "react-dom/server";
import { beforeEach, describe, expect, it, vi } from "vitest";
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
  ReportLink: ({ runId, summary }: { runId: string; summary: { title: string } }) => (
    <div data-testid="report-link">{runId} {summary.title}</div>
  ),
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
  beforeEach(() => {
    Object.values(api).forEach((mock) => mock.mockReset());
  });

  it("renders the weekly list and detail accordion from API data", async () => {
    api.getResearchHealth.mockResolvedValue({
      status: "ok",
      data: { status: "pass", migration_version: "0010", branch_id: "main", database: "neondb" },
    });
    api.getDailyReports.mockResolvedValue({ status: "ok", data: { reports: [], count: 0 } });
    api.getWeeklyReports.mockResolvedValue({ status: "ok", data: { reports: [validReport], count: 1 } });
    api.getWeeklyReport.mockResolvedValue({
      status: "ok",
      data: {
        ...validReport,
        brief: {
          ...validReport.brief,
          summary: "Ready summary",
          risks: [],
          opportunities: [],
          uncertainties: [],
        },
      },
    });

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
            extraction_error_code: null,
          },
          distillation: {
            source_url: "https://example.com/article",
            summary: "English summary",
            summary_original: "Original summary",
            key_points: ["First key point", "Second key point"],
            key_points_original: ["Primer punto"],
            entities: [],
            signals: [],
            claims: [{
              claim: "A cited claim",
              source_urls: ["https://example.com/article"],
              evidence_status: "verified",
              confidence: "high",
              support_locator: "paragraph 4",
              conflicts: [],
              evidence_excerpt: "Quoted evidence excerpt",
              citation_status: "cited",
            }],
            limitations: [],
            published_at: null,
            model_id: "google/gemma:free",
            prompt_version: "distill",
            evidence_status: "cited",
            content_hash: "hash",
            source_language: "en",
            translation_status: "not_needed",
            evidence_excerpts: ["Quoted evidence excerpt"],
            evidence_locators: ["paragraph 4"],
            what_happened: "A port authority changed the published fee.",
            why_it_matters: "Importers may face a new landed-cost assumption.",
            risk_assessment: {
              status: "supported",
              statement: "Costs may rise for affected cargo.",
              why_it_matters: "The fee affects the next shipment window.",
              next_step: "Check the tariff schedule.",
              evidence_excerpt: "fee effective immediately",
              evidence_locator: "paragraph 4",
            },
            opportunity_assessment: {
              status: "not_observed",
              statement: "No new opening was observed.",
              why_it_matters: "There is no expansion signal to act on.",
              next_step: "Recheck on the next weekly run.",
            },
            uncertainties: ["Whether carriers will pass through the fee."],
            next_steps: ["Compare the notice with carrier advisories."],
            quality_status: "incomplete",
            quality_issues: ["opportunity_not_observed"],
          },
          claims: [],
          source_hash: "hash",
          fulfillment: {
            source_url: "https://example.com/article",
            status: "incomplete",
            complete: false,
            source_persisted: true,
            extracted: true,
            distillation_persisted: true,
            claims_persisted: true,
            claim_count: 1,
            citation_count: 1,
            citation_complete: true,
            ui_displayable: true,
            missing_fields: ["opportunity_not_observed"],
            quality_issues: ["opportunity_not_observed"],
          },
        }],
        page: 1,
        page_size: 24,
        total: 25,
        has_more: true,
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

    const markup = renderToStaticMarkup(await SourcesPage({
      searchParams: Promise.resolve({ query: "fee", language: "en" }),
    }));
    expect(markup).toContain("Article title");
    expect(markup).toContain("English summary");
    expect(markup).toContain("Original summary");
    expect(markup).toContain("Costs may rise for affected cargo.");
    expect(markup).toContain("No new opening was observed.");
    expect(markup).toContain("Not observed");
    expect(markup).toContain("A cited claim");
    expect(markup).toContain("paragraph 4");
    expect(markup).toContain("Fulfillment: incomplete");
    expect(markup).toContain("24 per page");
    expect(markup).toContain("query=fee");
    expect(markup).toContain("language=en");
    expect(markup).toContain("page=2");
    expect(markup).toContain("hash");
  });

  it("renders empty source snippets as not recorded", async () => {
    api.getResearchSourceExplorer.mockResolvedValue({
      status: "ok",
      data: {
        items: [{
          source: {
            url: "https://example.com/empty-snippet",
            title: "Empty snippet source",
            publisher: "Example",
            published_at: null,
            retrieved_at: "2026-08-19T00:00:00Z",
            source_kind: "web",
            snippet: "",
            topics: [],
            geographies: ["US"],
            lane: "ports",
            is_seed: false,
            evidence_status: "unverified",
          },
          distillation: null,
          claims: [],
          source_hash: null,
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
        regions: [],
        languages: [],
        freshness: [],
        authority: [],
        source_types: [],
        lanes: [],
        evidence_states: [],
      },
    });

    const markup = renderToStaticMarkup(await SourcesPage({ searchParams: Promise.resolve({}) }));

    expect(markup).toContain("Snippet: Not recorded in this run.");
  });

  it("orders the homepage by decision readiness and exposes real readiness metrics", async () => {
    api.getResearchHealth.mockResolvedValue({
      status: "ok",
      data: { status: "pass", migration_version: "0010", branch_id: "main", database: "neondb" },
    });
    api.getDailyReports.mockResolvedValue({ status: "ok", data: { reports: [], count: 0 } });
    api.getWeeklyReports.mockResolvedValue({
      status: "ok",
      data: {
        reports: [
          {
            run_id: "partial-run",
            title: "Partial report",
            covered_from: "2026-08-01",
            covered_until: "2026-08-07",
            review_state: "draft",
            run_status: "partial",
            validation_status: "blocked",
            source_count: 3,
            distillation_count: 1,
            claim_count: 1,
            signal_count: 0,
            regions: ["us"],
            languages: ["en"],
            lane_coverage: ["ports"],
            models: ["model"],
            as_of: "2026-08-07T00:00:00Z",
            readiness_status: "incomplete",
            decision_ready: false,
            article_insight_completeness: 0.333333,
            complete_article_count: 1,
            report_section_completeness: 0.4,
            report_sections_complete: 2,
          },
          {
            run_id: "ready-run",
            title: "Ready report",
            covered_from: "2026-08-08",
            covered_until: "2026-08-14",
            review_state: "approved",
            run_status: "succeeded",
            validation_status: "pass",
            source_count: 3,
            distillation_count: 3,
            claim_count: 5,
            signal_count: 2,
            regions: ["us", "eu"],
            languages: ["en"],
            lane_coverage: ["ports"],
            models: ["model"],
            as_of: "2026-08-14T00:00:00Z",
            readiness_status: "decision_ready",
            decision_ready: true,
            article_insight_completeness: 0.666667,
            complete_article_count: 2,
            report_section_completeness: 1,
            report_sections_complete: 5,
          },
        ],
        count: 2,
      },
    });
    api.getWeeklyReport.mockResolvedValue({
      status: "ok",
      data: {
        ...validReport,
        brief: {
          ...validReport.brief,
          summary: "Ready summary",
          risks: [],
          opportunities: [],
          uncertainties: [],
        },
      },
    });

    const markup = renderToStaticMarkup(await HomePage());

    expect(markup.indexOf("Ready report")).toBeLessThan(markup.indexOf("Partial report"));
    expect(markup).toContain("2 complete article packets (67%)");
    expect(markup).toContain("5 complete report sections (100%)");
    expect(markup).toContain("Latest decision-ready report");
  });

  it("renders unknown homepage readiness metrics as not recorded", async () => {
    api.getResearchHealth.mockResolvedValue({
      status: "ok",
      data: { status: "pass", migration_version: "0010", branch_id: "main", database: "neondb" },
    });
    api.getDailyReports.mockResolvedValue({ status: "ok", data: { reports: [], count: 0 } });
    api.getWeeklyReports.mockResolvedValue({
      status: "ok",
      data: {
        reports: [{
          run_id: "legacy-run",
          title: "Legacy report",
          covered_from: "2026-08-08",
          covered_until: "2026-08-14",
          review_state: "approved",
          run_status: "succeeded",
          validation_status: "pass",
          source_count: 3,
          distillation_count: 3,
          claim_count: 5,
          signal_count: 2,
          regions: ["us"],
          languages: ["en"],
          lane_coverage: ["ports"],
          models: ["model"],
          as_of: "2026-08-14T00:00:00Z",
          readiness_status: "decision_ready",
          decision_ready: true,
        }],
        count: 1,
      },
    });
    api.getWeeklyReport.mockResolvedValue({
      status: "ok",
      data: {
        ...validReport,
        brief: {
          ...validReport.brief,
          summary: "Legacy summary",
          risks: [],
          opportunities: [],
          uncertainties: [],
        },
      },
    });

    const markup = renderToStaticMarkup(await HomePage());

    expect(markup).toContain("Article packets: Not recorded in this run");
    expect(markup).toContain("Report sections: Not recorded in this run");
    expect(markup).not.toContain("0/3 complete article packets");
    expect(markup).not.toContain("5 complete report sections");
  });
});
