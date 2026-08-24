import type { ReportPayload, WeeklyReportSummary } from "./research-api";

type ReadinessSummary = Pick<
  WeeklyReportSummary,
  | "run_status"
  | "validation_status"
  | "validation_profile"
  | "review_state"
  | "readiness_status"
  | "decision_ready"
  | "quality_ready"
  | "quality_report_ready"
  | "quality_readiness_status"
  | "quality_blocking_reasons"
  | "blocking_reasons"
  | "article_count"
  | "complete_article_count"
  | "article_insight_completeness"
  | "report_section_count"
  | "report_sections_complete"
  | "report_section_completeness"
>;

function isCompleteCount(value: number | undefined): boolean {
  return value !== undefined && Number.isInteger(value) && value > 0;
}

function isCompleteMetric(
  complete: number | undefined,
  ratio: number | undefined,
  denominator: number | undefined,
): boolean {
  return isCompleteCount(complete)
    && ratio === 1
    && isCompleteCount(denominator)
    && complete === denominator;
}

function hasNoBlockingReasons(reasons: string[] | undefined): boolean {
  return reasons !== undefined && reasons.length === 0;
}

function hasQualitySnapshot(summary: ReadinessSummary): boolean {
  return summary.quality_ready !== undefined
    || summary.quality_report_ready !== undefined
    || summary.quality_readiness_status !== undefined
    || summary.quality_blocking_reasons !== undefined
    || summary.article_count !== undefined
    || summary.complete_article_count !== undefined
    || summary.article_insight_completeness !== undefined
    || summary.report_section_count !== undefined
    || summary.report_sections_complete !== undefined
    || summary.report_section_completeness !== undefined;
}

export function isDecisionReadySummary(summary: ReadinessSummary): boolean {
  const qualitySnapshotComplete = !hasQualitySnapshot(summary)
    || (summary.quality_report_ready === true
      && summary.quality_readiness_status === "decision_ready"
      && hasNoBlockingReasons(summary.quality_blocking_reasons));
  const qualityComplete = summary.quality_ready === true
    && qualitySnapshotComplete
    && isCompleteMetric(
      summary.complete_article_count,
      summary.article_insight_completeness,
      summary.article_count,
    )
    && isCompleteMetric(
      summary.report_sections_complete,
      summary.report_section_completeness,
      summary.report_section_count,
    );

  return summary.decision_ready === true
    && summary.readiness_status === "decision_ready"
    && summary.run_status === "succeeded"
    && summary.validation_status === "pass"
    && summary.validation_profile === "full"
    && summary.review_state === "approved"
    && hasNoBlockingReasons(summary.blocking_reasons)
    && qualityComplete;
}

export function readinessSummaryFromReport(report: ReportPayload): ReadinessSummary {
  const quality = report.quality;
  return {
    run_status: report.run?.status ?? "missing",
    validation_status: report.validation?.status ?? "missing",
    validation_profile: report.run?.validation_profile,
    review_state: report.brief.review_state,
    readiness_status: report.readiness_status,
    decision_ready: report.ready,
    blocking_reasons: report.blocking_reasons,
    quality_ready: quality?.quality_ready,
    quality_report_ready: quality?.ready,
    quality_readiness_status: quality?.readiness_status,
    quality_blocking_reasons: quality?.blocking_reasons,
    article_count: quality?.article_count,
    complete_article_count: quality?.complete_article_count,
    article_insight_completeness: quality?.article_insight_completeness,
    report_section_count: quality?.report_section_count,
    report_sections_complete: quality?.report_sections_complete,
    report_section_completeness: quality?.report_section_completeness,
  };
}
