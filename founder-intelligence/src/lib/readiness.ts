import type { ReportPayload, WeeklyReportSummary } from "./research-api";

type ReadinessSummary = Pick<
  WeeklyReportSummary,
  | "run_status"
  | "validation_status"
  | "readiness_status"
  | "decision_ready"
  | "complete_article_count"
  | "article_insight_completeness"
  | "report_sections_complete"
  | "report_section_completeness"
>;

function isCompleteCount(value: number | undefined): boolean {
  return value !== undefined && Number.isInteger(value) && value > 0;
}

export function isDecisionReadySummary(summary: ReadinessSummary): boolean {
  return (summary.decision_ready === true || summary.readiness_status === "decision_ready")
    && summary.run_status === "succeeded"
    && summary.validation_status === "pass"
    && isCompleteCount(summary.complete_article_count)
    && summary.article_insight_completeness === 1
    && isCompleteCount(summary.report_sections_complete)
    && summary.report_section_completeness === 1;
}

export function readinessSummaryFromReport(report: ReportPayload): ReadinessSummary {
  return {
    run_status: report.run?.status ?? "missing",
    validation_status: report.validation?.status ?? "missing",
    readiness_status: report.readiness_status,
    decision_ready: report.ready,
    complete_article_count: report.quality?.complete_article_count,
    article_insight_completeness: report.quality?.article_insight_completeness,
    report_sections_complete: report.quality?.report_sections_complete,
    report_section_completeness: report.quality?.report_section_completeness,
  };
}
