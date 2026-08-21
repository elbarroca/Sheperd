import type { Metadata } from "next";
import { ReportAccordion, UnavailableState } from "@/components/report-accordion";
import { getWeeklyReport } from "@/lib/research-api";

export const metadata: Metadata = { title: "Weekly report" };

export default async function ReportPage({ params }: { params: Promise<{ run_id: string }> }) {
  const { run_id: runId } = await params;
  const response = await getWeeklyReport(runId);
  if (response.status === "unavailable") return <UnavailableState error={response.error} />;
  return <ReportAccordion report={response.data} />;
}
