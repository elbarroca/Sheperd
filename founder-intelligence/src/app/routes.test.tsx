import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it, vi } from "vitest";
import type { MonthlyRollup, ReportPayload } from "@/lib/research-api";

const api = vi.hoisted(() => ({
  getDailyReports: vi.fn(),
  getMonthlyRollups: vi.fn(),
  getResearchHealth: vi.fn(),
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
});
