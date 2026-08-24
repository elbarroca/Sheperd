import type { Metadata } from "next";
import Link from "next/link";
import {
  getDailyReports,
  getResearchHealth,
  getWeeklyReport,
  getWeeklyReports,
  type ReportPayload,
  type WeeklyReportSummary,
} from "@/lib/research-api";
import { isDecisionReadySummary } from "../lib/readiness";
import { ReportLink, UnavailableState } from "@/components/report-accordion";

export const metadata: Metadata = { title: "Research briefs" };

type ArchiveScope = "active" | "archived" | "all";
type HomeSearchParams = { scope?: string };

function dateLabel(value: string | undefined): string {
  return value
    ? new Intl.DateTimeFormat("en", { dateStyle: "medium" }).format(new Date(value))
    : "Not recorded";
}

function timestampLabel(value: string | undefined): string {
  if (!value) return "Not recorded";
  return new Intl.DateTimeFormat("en-US", {
    dateStyle: "medium",
    timeStyle: "short",
    timeZone: "UTC",
  }).format(new Date(value));
}

function asSummary(report: WeeklyReportSummary | ReportPayload): WeeklyReportSummary {
  if (!("brief" in report)) return report;
  const quality = report.quality;
  const blockingReasons = quality && report.blocking_reasons !== undefined
    ? [...new Set([...report.blocking_reasons, ...quality.blocking_reasons])]
    : report.blocking_reasons;
  const readinessStatus = quality && report.readiness_status !== quality.readiness_status
    ? "review_required"
    : report.readiness_status;
  return {
    run_id: report.brief.run_id,
    title: report.brief.title,
    covered_from: report.brief.covered_from,
    covered_until: report.brief.covered_until,
    review_state: report.brief.review_state,
    run_status: report.run?.status ?? "unknown",
    validation_status: report.validation?.status ?? "blocked",
    source_count: report.sources?.length ?? 0,
    distillation_count: report.distillations?.length ?? 0,
    claim_count: report.claims?.length ?? 0,
    signal_count: report.signals?.length ?? 0,
    regions: [...new Set((report.sources ?? []).map((source) => source.region ?? "global"))],
    languages: [...new Set((report.sources ?? []).map((source) => source.language_code ?? "und"))],
    lane_coverage: report.lane_coverage ?? [],
    models: report.models ?? [],
    as_of: report.as_of,
    archived: report.run?.archived,
    archived_at: report.run?.archived_at,
    archive_reason: report.run?.archive_reason,
    readiness_status: readinessStatus,
    decision_ready: report.ready,
    quality_report_ready: quality?.ready,
    quality_ready: quality
      ? quality.ready === true
        && quality.quality_ready === true
        && quality.readiness_status === "decision_ready"
      : undefined,
    quality_readiness_status: quality?.readiness_status,
    quality_blocking_reasons: quality?.blocking_reasons,
    blocking_reasons: blockingReasons,
    article_count: quality?.article_count,
    article_insight_completeness: quality?.article_insight_completeness,
    report_section_completeness: quality?.report_section_completeness,
    complete_article_count: quality?.complete_article_count,
    report_section_count: quality?.report_section_count,
    report_sections_complete: quality?.report_sections_complete,
  };
}

function isReady(report: WeeklyReportSummary): boolean {
  return isDecisionReadySummary(report);
}

function getScope(value: string | undefined): ArchiveScope {
  return value === "archived" || value === "all" ? value : "active";
}

function slugifyId(value: string): string {
  return value.trim().toLowerCase().replace(/[^a-z0-9]+/gu, "-").replace(/^-|-$/gu, "");
}

function nextSteps(report: ReportPayload): string[] {
  const seen = new Set<string>();
  return [...report.brief.risks, ...report.brief.opportunities, ...report.brief.uncertainties].flatMap((bullet) => {
    if (!bullet.next_step || seen.has(bullet.next_step)) return [];
    seen.add(bullet.next_step);
    return [bullet.next_step];
  }).slice(0, 3);
}

function readinessMetric(
  complete: number | undefined,
  denominator: number | undefined,
  ratio: number | undefined,
  label: string,
): string {
  if (complete === undefined || denominator === undefined || ratio === undefined) {
    return `${label}: Not recorded in this run`;
  }
  return `${complete}/${denominator} complete ${label.toLowerCase()} (${Math.round(ratio * 100)}%)`;
}

function scopeHref(scope: ArchiveScope): string {
  return scope === "active" ? "/" : `/?scope=${scope}`;
}

function ReportSection({
  title,
  reports,
}: {
  title: string;
  reports: WeeklyReportSummary[];
}) {
  const headingId = `${slugifyId(title)}-heading`;
  return (
    <section className="report-group" aria-labelledby={headingId}>
      <div className="section-heading">
        <div>
          <p className="eyebrow">{title}</p>
          <h2 id={headingId}>{reports.length} reports</h2>
        </div>
        <span className="count-label">Read-only archive</span>
      </div>
      {reports.length > 0 ? (
        <div className="report-list">
          {reports.map((report) => <ReportLink key={report.run_id} runId={report.run_id} summary={report} />)}
        </div>
      ) : (
        <div className="empty-state">
          <strong>No {title.toLowerCase()}.</strong>
          <p>Run the research service, then reload. No stale report data is shown.</p>
        </div>
      )}
    </section>
  );
}

export default async function HomePage({
  searchParams,
}: {
  searchParams?: Promise<HomeSearchParams>;
} = {}) {
  const params = searchParams ? await searchParams : {};
  const scope = getScope(params.scope);
  const [health, weekly, daily] = await Promise.all([
    getResearchHealth(),
    getWeeklyReports({ archive_scope: scope, limit: 50, offset: 0 }),
    getDailyReports({ archive_scope: scope, limit: 6, offset: 0 }),
  ]);

  if (weekly.status === "unavailable") return <UnavailableState error={weekly.error} />;

  const weeklyReports = weekly.data.reports.map(asSummary);
  const dailyReports = daily.status === "ok" ? daily.data.reports.map(asSummary) : [];
  const readyReport = weeklyReports.find(isReady);
  const featured = readyReport ?? (scope === "active" ? undefined : weeklyReports[0]);
  const history = weeklyReports.filter((report) => report.run_id !== featured?.run_id);
  const featuredDetail = featured ? await getWeeklyReport(featured.run_id, scope) : null;
  const featuredNextSteps = featuredDetail?.status === "ok" ? nextSteps(featuredDetail.data) : [];

  return (
    <div className="dashboard-page">
      <header className="research-header">
        <div>
          <p className="eyebrow">SheperD research desk</p>
          <h1>Research briefs</h1>
          <p className="header-lede">Cited maritime and D&amp;D intelligence, persisted in Neon and kept reviewable.</p>
        </div>
        <div className="system-status" aria-label="Research system status">
          <span className={`status-badge status-${health.status === "ok" ? "pass" : "blocked"}`}>
            {health.status === "ok" ? "API online" : "API unavailable"}
          </span>
          <span>{health.status === "ok" ? `Migration ${health.data.migration_version}` : health.error}</span>
        </div>
      </header>

      {featured ? (
        <section className="document-feature" aria-labelledby="featured-heading">
          <div>
            <p className="eyebrow">{isReady(featured) ? "Latest decision-ready report" : scope === "archived" ? "Archived failure report" : "Latest incomplete report"}</p>
            <h2 id="featured-heading">{featured.title}</h2>
            <p className="muted">{dateLabel(featured.covered_from)} to {dateLabel(featured.covered_until)}</p>
            <p className="report-as-of">As of {timestampLabel(featured.as_of)} UTC</p>
          </div>
          <div className="document-metrics">
            <span>{featured.source_count} sources</span>
            <span>{featured.distillation_count} distillations</span>
            <span>{featured.claim_count} claims</span>
            <span>{featured.signal_count} signals</span>
            <span>{featured.regions.length} regions</span>
            <span>{featured.languages.length} languages</span>
            <span>{readinessMetric(featured.complete_article_count, featured.article_count, featured.article_insight_completeness, "Article packets")}</span>
            <span>{readinessMetric(featured.report_sections_complete, featured.report_section_count, featured.report_section_completeness, "Report sections")}</span>
            <span>Readiness: {featured.readiness_status ?? "legacy"}</span>
          </div>
          <Link
            className="text-action"
            href={`/reports/${encodeURIComponent(featured.run_id)}${featured.archived ? "?archive_scope=archived" : ""}`}
          >
            Open report
          </Link>
        </section>
      ) : (
        <div className="empty-state">
          <strong>No decision-ready report yet.</strong>
          <p>Reports remain drafts until a successful run passes validation and receives human review.</p>
        </div>
      )}

      {featured && featuredDetail?.status === "ok" ? (
        <section className="featured-readout" aria-labelledby="featured-readout-heading">
          <div>
            <p className="eyebrow">Quick read</p>
            <h2 id="featured-readout-heading">Conclusion</h2>
            <p>{featuredDetail.data.brief.summary}</p>
          </div>
          <div>
            <p className="eyebrow">Next steps</p>
            {featuredNextSteps.length > 0 ? (
              <ol className="decision-list">
                {featuredNextSteps.map((step, index) => <li key={`${step}-${index}`}><span>{step}</span></li>)}
              </ol>
            ) : <p className="muted">No next step was recorded.</p>}
          </div>
        </section>
      ) : featured ? (
        <p className="inline-note">Report detail is unavailable. Open the report to retry.</p>
      ) : null}

      <nav className="archive-nav" aria-label="Report archive scope">
        {(["active", "archived", "all"] as const).map((item) => (
          <Link className={scope === item ? "active" : ""} href={scopeHref(item)} key={item}>
            {item === "active" ? "Active reports" : item === "archived" ? "Archived failures" : "All records"}
          </Link>
        ))}
      </nav>

      <ReportSection title={scope === "archived" ? "Archived failures" : "Weekly archive"} reports={history} />
      <ReportSection title="Daily briefs" reports={dailyReports} />
      {daily.status === "unavailable" ? <p className="inline-note">Daily endpoint unavailable: {daily.error}</p> : null}
    </div>
  );
}
