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

function ReportGroup({
  label,
  description,
  reports,
}: {
  label: string;
  description: string;
  reports: WeeklyReportSummary[];
}) {
  return (
    <section className="report-group" aria-labelledby={`${label.toLowerCase()}-heading`}>
      <div className="section-heading">
        <div>
          <p className="eyebrow">{label}</p>
          <h2 id={`${label.toLowerCase()}-heading`}>{description}</h2>
        </div>
        <span className="count-label">{reports.length} available</span>
      </div>
      {reports.length > 0 ? (
        <div className="report-grid">
          {reports.map((report) => (
            <ReportLink key={report.run_id} runId={report.run_id} summary={report} />
          ))}
        </div>
      ) : (
        <div className="empty-state">
          <strong>No {label.toLowerCase()} briefs yet.</strong>
          <p>Run the research service, then reload this page. The UI never invents fallback data.</p>
        </div>
      )}
    </section>
  );
}

export default async function HomePage() {
  const [health, weekly, daily] = await Promise.all([
    getResearchHealth(),
    getWeeklyReports(),
    getDailyReports(),
  ]);

  if (weekly.status === "unavailable") return <UnavailableState error={weekly.error} />;

  const weeklyReports = weekly.data.reports.map(asSummary);
  const dailyReports = daily.status === "ok" ? daily.data.reports.map(asSummary) : [];
  const latest = weeklyReports[0] ?? dailyReports[0];

  return (
    <div className="dashboard-page">
      <section className="hero-panel">
        <div className="hero-copy">
          <p className="eyebrow">SheperD research desk</p>
          <h1>Evidence in. Decisions out.</h1>
          <p className="hero-lede">
            Daily evidence and weekly synthesis from bounded Tavily, LangGraph, LangChain, and OpenRouter agents.
          </p>
          <div className="hero-actions">
            <Link className="primary-action" href="#weekly">Read weekly briefs</Link>
            <Link className="secondary-action" href="/sources">Browse sources</Link>
          </div>
        </div>
        <div className="system-panel" aria-label="Research system status">
          <div className="system-panel-heading">
            <span className="status-mark" aria-hidden="true" />
            <span>System status</span>
          </div>
          <strong>{health.status === "ok" ? "Neon main is reachable" : "Research API unavailable"}</strong>
          <p>{health.status === "ok" ? `Migration ${health.data.migration_version}` : health.error}</p>
          <dl className="system-facts">
            <div><dt>Latest brief</dt><dd>{latest ? dateLabel(latest.as_of) : "None"}</dd></div>
            <div><dt>Primary model</dt><dd>{latest?.models[0] ?? "Not recorded"}</dd></div>
            <div><dt>Write policy</dt><dd>Drafts only</dd></div>
          </dl>
        </div>
      </section>

      <section className="workflow-strip" aria-labelledby="workflow-heading">
        <div className="section-heading compact-heading">
          <div>
            <p className="eyebrow">How the desk works</p>
            <h2 id="workflow-heading">Search, distill, review.</h2>
          </div>
        </div>
        <ol className="workflow-list">
          <li><strong>Discover</strong><span>Three bounded lanes search and extract public sources.</span></li>
          <li><strong>Distill</strong><span>OpenRouter structures summaries, claims, signals, and citations.</span></li>
          <li><strong>Reconcile</strong><span>Validators and a critic mark gaps before a brief stays a draft.</span></li>
        </ol>
      </section>

      <div id="weekly" className="anchor-target" />
      <ReportGroup label="Weekly briefs" description="The reviewed reading window for the industry." reports={weeklyReports} />
      <ReportGroup label="Daily briefs" description="Fresh evidence collected for the next synthesis." reports={dailyReports} />

      {daily.status === "unavailable" ? <p className="inline-note">Daily endpoint unavailable: {daily.error}</p> : null}
    </div>
  );
}
