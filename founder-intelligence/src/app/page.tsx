import type { Metadata } from "next";
import Link from "next/link";
import {
  getDailyReports,
  getResearchHealth,
  getWeeklyReports,
  type ReportPayload,
  type WeeklyReportSummary,
} from "@/lib/research-api";
import { ReportLink, UnavailableState } from "@/components/report-accordion";

export const metadata: Metadata = { title: "Research briefs" };

type HomeSearchParams = { status?: string };
const STATUS_FILTERS = ["all", "ready", "draft", "partial", "failed"] as const;
type StatusFilter = (typeof STATUS_FILTERS)[number];

function dateLabel(value: string | undefined): string {
  return value ? new Intl.DateTimeFormat("en", { dateStyle: "medium" }).format(new Date(value)) : "Not recorded";
}

function asSummary(report: WeeklyReportSummary | ReportPayload): WeeklyReportSummary {
  if (!("brief" in report)) return report;
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
  };
}

function isReady(report: WeeklyReportSummary): boolean {
  return report.run_status === "succeeded" && report.validation_status === "pass";
}

function filterHref(status: StatusFilter): string {
  return status === "all" ? "/" : `/?status=${status}`;
}

function ReportSection({
  title,
  description,
  reports,
}: {
  title: string;
  description: string;
  reports: WeeklyReportSummary[];
}) {
  return (
    <section className="report-group" aria-labelledby={`${title.toLowerCase()}-heading`}>
      <div className="section-heading">
        <div><p className="eyebrow">{title}</p><h2 id={`${title.toLowerCase()}-heading`}>{description}</h2></div>
        <span className="count-label">{reports.length} shown</span>
      </div>
      {reports.length > 0 ? <div className="report-grid">{reports.map((report) => <ReportLink key={report.run_id} runId={report.run_id} summary={report} />)}</div> : <div className="empty-state"><strong>No {title.toLowerCase()} available.</strong><p>Run the research service, then reload. No stale report data is shown.</p></div>}
    </section>
  );
}

export default async function HomePage({
  searchParams,
}: {
  searchParams?: Promise<HomeSearchParams>;
} = {}) {
  const params = searchParams ? await searchParams : {};
  const selectedStatus: StatusFilter = STATUS_FILTERS.includes(params.status as StatusFilter) ? params.status as StatusFilter : "all";
  const [health, weekly, daily] = await Promise.all([
    getResearchHealth(),
    getWeeklyReports({ status: selectedStatus, limit: 20, offset: 0 }),
    getDailyReports({ limit: 6, offset: 0 }),
  ]);

  if (weekly.status === "unavailable") return <UnavailableState error={weekly.error} />;
  const weeklyReports = weekly.data.reports.map(asSummary);
  const dailyReports = daily.status === "ok" ? daily.data.reports.map(asSummary) : [];
  const readyReport = weeklyReports.find(isReady);
  const latest = readyReport ?? weeklyReports[0] ?? dailyReports[0];
  const history = weeklyReports.filter((report) => report.run_id !== readyReport?.run_id);

  return (
    <div className="dashboard-page">
      <section className="hero-panel">
        <div className="hero-copy">
          <p className="eyebrow">SheperD research desk</p>
          <h1>Evidence in. Decisions out.</h1>
          <p className="hero-lede">A private evidence desk for maritime and D&D intelligence: persisted sources, structured distillations, cited claims, and review-gated reports.</p>
          <div className="hero-actions"><Link className="primary-action" href="#weekly">Read weekly briefs</Link><Link className="secondary-action" href="/sources">Browse all sources</Link></div>
        </div>
        <div className="system-panel" aria-label="Research system status">
          <div className="system-panel-heading"><span className="status-mark" aria-hidden="true" /><span>System status</span></div>
          <strong>{health.status === "ok" ? "Neon main is reachable" : "Research API unavailable"}</strong>
          <p>{health.status === "ok" ? `Migration ${health.data.migration_version}` : health.error}</p>
          <dl className="system-facts">
            <div><dt>Latest decision-ready</dt><dd>{readyReport ? dateLabel(readyReport.as_of) : "None"}</dd></div>
            <div><dt>Observed model</dt><dd>{latest?.models[0] ?? "Not recorded"}</dd></div>
            <div><dt>Write policy</dt><dd>Drafts · human review</dd></div>
          </dl>
        </div>
      </section>

      {latest ? (
        <section className="featured-report" aria-labelledby="featured-heading">
          <div><p className="eyebrow">{readyReport ? "Decision-ready report" : "Latest persisted report"}</p><h2 id="featured-heading">{latest.title}</h2><p className="muted">{dateLabel(latest.covered_from)} to {dateLabel(latest.covered_until)}</p></div>
          <div className="metric-strip"><span>{latest.source_count} sources</span><span>{latest.distillation_count} distillations</span><span>{latest.claim_count} claims</span><span>{latest.signal_count} signals</span><span>{latest.regions.length} regions</span><span>{latest.languages.length} languages</span></div>
          <Link className="primary-action" href={`/reports/${encodeURIComponent(latest.run_id)}`}>Open report</Link>
        </section>
      ) : <div className="empty-state"><h2>No decision-ready report yet.</h2><p>Reports remain drafts until a successful run passes validation and receives human review.</p></div>}

      <section className="workflow-strip" aria-labelledby="workflow-heading">
        <div className="section-heading compact-heading"><div><p className="eyebrow">How the desk works</p><h2 id="workflow-heading">Search, distill, review.</h2></div></div>
        <ol className="workflow-list"><li><strong>Discover</strong><span>Three bounded lanes search and extract public sources.</span></li><li><strong>Distill</strong><span>OpenRouter structures summaries, claims, signals, and citations.</span></li><li><strong>Reconcile</strong><span>Validators and a critic mark gaps before approval.</span></li></ol>
      </section>

      <div id="weekly" className="anchor-target" />
      <section className="report-group">
        <div className="section-heading"><div><p className="eyebrow">Weekly archive</p><h2>Every run stays inspectable.</h2></div><div className="status-filters" aria-label="Report status filters">{STATUS_FILTERS.map((status) => <Link className={status === selectedStatus ? "active" : ""} href={filterHref(status)} key={status}>{status}</Link>)}</div></div>
        <ReportSection title="Historical reports" description="Drafts and failures remain visible, with readiness labeled honestly." reports={history} />
      </section>
      <ReportSection title="Daily briefs" description="Fresh evidence collected for the next synthesis." reports={dailyReports} />
      {daily.status === "unavailable" ? <p className="inline-note">Daily endpoint unavailable: {daily.error}</p> : null}
    </div>
  );
}
