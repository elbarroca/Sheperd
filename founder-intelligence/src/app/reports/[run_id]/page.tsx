import type { Metadata } from "next";
import { ReportAccordion, UnavailableState } from "@/components/report-accordion";
import { getWeeklyReport } from "@/lib/research-api";

export const metadata: Metadata = { title: "Weekly report" };

export default async function ReportPage({
  params,
  searchParams,
}: {
  params: Promise<{ run_id: string }>;
  searchParams?: Promise<{ archive_scope?: string }>;
}) {
  const { run_id: runId } = await params;
  const query = searchParams ? await searchParams : {};
  const archiveScope = query.archive_scope === "archived" ? "archived" : "active";
  const response = await getWeeklyReport(runId, archiveScope);
  if (response.status === "unavailable") return <UnavailableState error={response.error} />;
  return <ReportAccordion report={response.data} />;
}
