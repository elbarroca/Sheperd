import type { Metadata } from "next";
import { ReportLink, UnavailableState } from "@/components/report-accordion";
import { getWeeklyReports } from "@/lib/research-api";

export const metadata: Metadata = { title: "Weekly reports" };

function period(from: string, until: string): string {
  return `${new Intl.DateTimeFormat("en", { dateStyle: "medium" }).format(new Date(from))} – ${new Intl.DateTimeFormat("en", { dateStyle: "medium" }).format(new Date(until))}`;
}

export default async function HomePage() {
  const response = await getWeeklyReports();
  if (response.status === "unavailable") return <UnavailableState error={response.error} />;
  return (
    <div className="page-stack">
      <div className="page-intro"><p className="eyebrow">Neon-backed research desk</p><h1>Weekly intelligence, kept reviewable.</h1><p>Read cited drafts produced by the bounded Tavily → LangGraph → OpenRouter workflow. Every report stays a draft until a human review decision is recorded.</p></div>
      <section className="report-grid" aria-label="Weekly reports">
        {response.data.reports.length > 0 ? response.data.reports.map((report) => <ReportLink key={report.brief.run_id} runId={report.brief.run_id} title={report.brief.title} period={period(report.brief.covered_from, report.brief.covered_until)} />) : <div className="empty-state"><h2>No weekly drafts yet</h2><p>Run the research service, then reload this page. The UI never invents fallback data.</p></div>}
      </section>
    </div>
  );
}
