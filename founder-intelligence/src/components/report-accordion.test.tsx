import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";
import type { ReportPayload } from "@/lib/research-api";
import { ReportAccordion, ReportLink } from "./report-accordion";

const report: ReportPayload = {
  brief: {
    run_id: "blocked-run",
    title: "Blocked weekly brief",
    covered_from: "2026-08-12T00:00:00Z",
    covered_until: "2026-08-19T00:00:00Z",
    summary: "DRAFT - HUMAN REVIEW REQUIRED",
    source_urls: ["https://example.com/source"],
    limitations: ["Validation did not pass."],
    review_state: "draft",
    evidence_status: "mixed",
    model_id: "google/gemma-4-26b-a4b-it:free",
    prompt_version: "weekly-brief-v4",
    executive_bullets: [],
    developments: [],
    risks: [],
    opportunities: [],
    uncertainties: [],
    follow_up_questions: [],
  },
  run: {
    run_id: "blocked-run",
    status: "failed",
    as_of: "2026-08-19T00:00:00Z",
    error: "validation: blocked",
    neon_branch_id: "main",
    migration_version: "0008_audit_surfaces",
    validation_profile: "full",
    run_kind: "research",
    parent_run_id: null,
    repair_round: null,
    context_version: "commit:manifest",
    research_timezone: "Europe/Lisbon",
  },
  validation: {
    run_id: "blocked-run",
    status: "blocked",
    citation_coverage: 0,
    lane_coverage: ["regulatory"],
    checks: [{ name: "lane_coverage", status: "failed", message: "missing lanes" }],
  },
  lane_coverage: ["regulatory"],
  models: ["google/gemma-4-26b-a4b-it:free"],
  steps: [{
    agent_name: "critic",
    status: "failed",
    lane: "system",
    attempt: 1,
    duration_ms: 41,
    error_code: "provider",
    requested_model: "google/gemma-4-26b-a4b-it:free",
    resolved_model: null,
    prompt_version: "critic-v4",
    input_hash: "input-hash",
    output_hash: null,
    input_tokens: 10,
    output_tokens: 0,
    total_tokens: 10,
    created_at: "2026-08-19T12:34:56Z",
  }],
  tool_calls: [{
    agent_name: "discovery:regulatory",
    lane: "regulatory",
    attempt: 1,
    call_index: 0,
    tool_name: "tavily_search",
    sanitized_args: { query: "fmc enforcement", url_count: 0 },
    input_hash: "tool-input",
    result_hash: null,
    result_count: 0,
    latency_ms: 22,
    status: "failed",
    error_code: "provider",
  }],
  sources: [{
    url: "https://example.com/source",
    title: "Example source",
    publisher: "Example",
    published_at: null,
    retrieved_at: "2026-08-19T00:00:00Z",
    source_kind: "web-discovery",
    snippet: "A source snippet.",
    topics: ["dnd"],
    geographies: ["Regulatory"],
    lane: "regulatory",
    is_seed: false,
    evidence_status: "unverified",
    period_status: "in_period",
    period_basis: "published_at",
    eligible_for_weekly: true,
  }, {
    url: "https://example.com/background",
    title: "Background source",
    publisher: "Archive",
    published_at: "2026-07-01T00:00:00Z",
    retrieved_at: "2026-08-19T00:00:00Z",
    source_kind: "web-discovery",
    snippet: "Background context.",
    topics: ["dnd"],
    geographies: ["Europe"],
    lane: "europe",
    is_seed: false,
    evidence_status: "verified",
    period_status: "background",
    period_basis: "published_at",
    eligible_for_weekly: false,
  }],
  distillations: [{
    source_url: "https://example.com/source",
    summary: "A source distillation.",
    key_points: ["A key point."],
    entities: [],
    signals: ["A signal."],
    claims: [],
    limitations: [],
    published_at: null,
    model_id: "google/gemma-4-26b-a4b-it:free",
    prompt_version: "distill-v4",
    evidence_status: "mixed",
    content_hash: "distillation-hash",
  }],
  claims: [{
    claim: "A claim from the persisted source.",
    source_urls: ["https://example.com/source"],
    evidence_status: "unverified",
    confidence: "low",
    support_locator: null,
    conflicts: [],
  }],
  signals: [{
    event_id: "signal-1",
    run_id: "blocked-run",
    event_type: "port-delay",
    summary: "A persisted signal.",
    geographies: ["Regulatory"],
    ports: [],
    carriers: [],
    event_at: null,
    source_urls: ["https://example.com/source"],
    evidence_status: "unverified",
    headline: "Port operations update",
    what_changed: "The port changed its published operating window.",
    published_at: "2026-08-18T12:00:00Z",
    retrieved_at: "2026-08-19T00:00:00Z",
    period_status: "in_period",
    period_basis: "published_at",
    eligible_for_weekly: true,
    region: "us",
    lane: "regulatory",
    evidence_locator: "paragraph 4",
    impact: "Operators may need to adjust schedules.",
    risk: "Late changes can cause missed windows.",
    opportunity: "Earlier notice can improve planning.",
    next_step: "Confirm the new operating window.",
    limitations: ["One public source."],
  }, {
    event_id: "signal-background",
    run_id: "blocked-run",
    event_type: "historical-context",
    summary: "Earlier guidance provides context.",
    headline: "Earlier port guidance",
    what_changed: "Historical guidance was recorded.",
    geographies: ["Europe"],
    ports: [],
    carriers: [],
    event_at: null,
    published_at: "2026-07-01T00:00:00Z",
    retrieved_at: "2026-08-19T00:00:00Z",
    period_status: "background",
    period_basis: "published_at",
    eligible_for_weekly: false,
    region: "europe",
    lane: "europe",
    source_urls: ["https://example.com/background"],
    evidence_locator: "section 2",
    impact: "Provides historical context.",
    risk: "Not current-week evidence.",
    opportunity: "Supports comparison.",
    next_step: "Keep separate from current findings.",
    limitations: ["Out of period."],
    evidence_status: "verified",
  }],
  source_hashes: ["source-hash"],
  source_hash_by_url: {
    "https://example.com/source": "source-hash",
    "https://example.com/background": "background-hash",
  },
  as_of: "2026-08-19T00:00:00Z",
  covered_from: "2026-08-12T00:00:00Z",
  covered_until: "2026-08-19T00:00:00Z",
  canonical_hash: "b".repeat(64),
  reader_report: {
    run_id: "blocked-run",
    title: "Blocked weekly brief",
    covered_from: "2026-08-12T00:00:00Z",
    covered_until: "2026-08-19T00:00:00Z",
    report_status: "draft",
    validation_status: "blocked",
    readiness_status: "review_required",
    canonical_hash: "b".repeat(64),
    three_things: ["Port operations update: Operators may need to adjust schedules."],
    top_action: "Confirm the new operating window.",
    ranked_articles: [{
      source_url: "https://example.com/source",
      headline: "Port operations update",
      publisher: "Example",
      published_at: "2026-08-18T12:00:00Z",
      event_at: null,
      date_basis: "search",
      date_locator: "tavily.search.published_date",
      retrieved_at: "2026-08-19T00:00:00Z",
      page_type: "article",
      score: {
        sheperd_relevance: 30,
        operational_impact: 25,
        actionability: 20,
        recency: 15,
        source_authority: 10,
        total: 100,
        priority: "high",
        rationale: {},
      },
      key_points: ["Window changed.", "Schedules may move.", "Confirmation is required."],
      what_changed: "The port changed its published operating window.",
      why_sheperd_cares: "Operators may need to adjust schedules.",
      recommended_action: "Confirm the new operating window.",
      risk: "Late changes can cause missed windows.",
      opportunity: null,
      limitations: ["One public source."],
      lane: "regulatory",
      region: "us",
      eligible_for_weekly: true,
      validation_status: "validated",
    }],
    watchlist: [],
    background_articles: [],
    source_index: [{
      url: "https://example.com/source",
      title: "Example source",
      publisher: "Example",
      published_at: "2026-08-18T12:00:00Z",
      date_basis: "search",
      page_type: "article",
      eligible_for_weekly: true,
      validation_status: "validated",
    }],
  },
  pdf: {
    available: false,
    url: null,
    uploaded_at: null,
    content_hash: null,
    canonical_hash: "b".repeat(64),
    unavailable_reason: "pdf_delivery_not_configured",
  },
};

describe("ReportAccordion", () => {
  it("renders persisted evidence and explicit failed and blocked audit states", () => {
    const markup = renderToStaticMarkup(<ReportAccordion report={report} />);

    expect(markup).toContain("failed");
    expect(markup).toContain("blocked");
    expect(markup).toContain("A source distillation.");
    expect(markup).toContain("A claim from the persisted source.");
    expect(markup).toContain("A persisted signal.");
    expect(markup).toContain("source-hash");
    expect(markup).toContain("fmc enforcement");
    expect(markup).toContain("critic-v4");
    expect(markup).toContain("Download Markdown");
    expect(markup).toContain("Run activity");
    expect(markup).toContain("Aug 19, 2026, 12:34:56 PM");
    expect(markup).toContain("Current event timeline");
    expect(markup).toContain("Background event timeline");
    expect(markup).toContain("Port operations update");
    expect(markup).toContain("Operators may need to adjust schedules.");
    expect(markup).toContain("Three things to know");
    expect(markup).toContain("Top action");
    expect(markup).toContain("Priority 100/100");
    expect(markup).toContain("SheperD relevance");
    expect(markup).toContain("30/30");
    expect(markup).toContain("paragraph 4");
    expect(markup).toContain("Current-week evidence");
    expect(markup).toContain("Background context");
    expect(markup).toContain("background-hash");
    expect(markup).toContain("PDF unavailable");
    expect(markup).toContain("pdf delivery not configured");
    expect(markup).toContain("b".repeat(64));
  });

  it("renders direct repair lineage without putting repair runs in report lists", () => {
    const markup = renderToStaticMarkup(
      <ReportAccordion
        report={{
          ...report,
          run: report.run ? {
            ...report.run,
            run_kind: "repair",
            parent_run_id: "legacy-parent",
            repair_round: 2,
          } : null,
        }}
      />,
    );

    expect(markup).toContain("Repair lineage");
    expect(markup).toContain("legacy-parent");
    expect(markup).toContain("Round 2");
  });

  it("renders the source-to-UI fulfillment audit when provided", () => {
    const markup = renderToStaticMarkup(
      <ReportAccordion
        report={{
          ...report,
          quality: {
            ready: false,
            readiness_status: "review_required",
            blocking_reasons: ["incomplete_article_insights"],
            quality_ready: false,
            article_count: 1,
            complete_article_count: 0,
            article_insight_completeness: 0,
            article_quality_issues: { "https://example.com/source": ["claims_incomplete"] },
            source_distillation_coverage: 1,
            report_section_count: 5,
            report_sections_complete: 0,
            report_section_completeness: 0,
            report_quality_issues: [],
            article_fulfillment: [{
              source_url: "https://example.com/source",
              status: "incomplete",
              complete: false,
              source_persisted: true,
              extracted: true,
              distillation_persisted: true,
              claims_persisted: false,
              claim_count: 0,
              citation_count: 0,
              citation_complete: false,
              ui_displayable: true,
              missing_fields: ["claims_incomplete"],
              quality_issues: ["claims_incomplete"],
            }],
          },
        }}
      />,
    );

    expect(markup).toContain("Fulfillment: incomplete");
    expect(markup).toContain("missing claims_incomplete");
  });

  it("renders duplicate distillation fulfillment issues", () => {
    const markup = renderToStaticMarkup(
      <ReportAccordion
        report={{
          ...report,
          quality: {
            ready: false,
            readiness_status: "review_required",
            blocking_reasons: ["incomplete_article_insights", "duplicate_distillation"],
            quality_ready: false,
            article_count: 1,
            complete_article_count: 0,
            article_insight_completeness: 0,
            article_quality_issues: { "https://example.com/source": ["duplicate_distillation"] },
            source_distillation_coverage: 1,
            report_section_count: 5,
            report_sections_complete: 0,
            report_section_completeness: 0,
            report_quality_issues: [],
            article_fulfillment: [{
              source_url: "https://example.com/source",
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
              missing_fields: ["duplicate_distillation"],
              quality_issues: ["duplicate_distillation"],
            }],
          },
        }}
      />,
    );

    expect(markup).toContain("Fulfillment: incomplete");
    expect(markup).toContain("missing duplicate_distillation");
  });

  it("renders report summaries as compact rows and labels archived reports", () => {
    const markup = renderToStaticMarkup(
      <ReportLink
        runId="failed-run"
        summary={{
          run_id: "failed-run",
          title: "Archived report",
          covered_from: "2026-08-12T00:00:00Z",
          covered_until: "2026-08-19T00:00:00Z",
          review_state: "draft",
          run_status: "partial",
          validation_status: "failed",
          source_count: 2,
          distillation_count: 2,
          claim_count: 3,
          signal_count: 1,
          regions: ["global"],
          languages: ["en"],
          lane_coverage: ["regulatory"],
          models: ["google/gemma-4-26b-a4b-it:free"],
          as_of: "2026-08-19T00:00:00Z",
          archived: true,
          archived_at: "2026-08-20T00:00:00Z",
          archive_reason: "validation_failed",
        }}
      />,
    );

    expect(markup).toContain("report-row");
    expect(markup).toContain("Archived");
    expect(markup).toContain("validation_failed");
  });

  it("does not label summaries decision-ready when completeness fields are missing", () => {
    const markup = renderToStaticMarkup(
      <ReportLink
        runId="legacy-ready-run"
        summary={{
          run_id: "legacy-ready-run",
          title: "Legacy ready flag",
          covered_from: "2026-08-12T00:00:00Z",
          covered_until: "2026-08-19T00:00:00Z",
          review_state: "approved",
          run_status: "succeeded",
          validation_status: "pass",
          validation_profile: "full",
          source_count: 2,
          distillation_count: 2,
          claim_count: 3,
          signal_count: 1,
          regions: ["global"],
          languages: ["en"],
          lane_coverage: ["regulatory"],
          models: ["model"],
          as_of: "2026-08-19T00:00:00Z",
          readiness_status: "decision_ready",
          decision_ready: true,
          blocking_reasons: [],
          quality_ready: true,
        }}
      />,
    );

    expect(markup).toContain("succeeded / review required");
    expect(markup).not.toContain("Decision-ready");
  });

  it("shows current quality failure instead of a stale stored pass", () => {
    const markup = renderToStaticMarkup(
      <ReportLink
        runId="stale-pass-run"
        summary={{
          run_id: "stale-pass-run",
          title: "Stale pass",
          covered_from: "2026-08-12T00:00:00Z",
          covered_until: "2026-08-19T00:00:00Z",
          review_state: "draft",
          run_status: "succeeded",
          validation_status: "pass",
          source_count: 3,
          distillation_count: 3,
          claim_count: 3,
          signal_count: 3,
          regions: ["global"],
          languages: ["en"],
          lane_coverage: ["regulatory"],
          models: ["model"],
          as_of: "2026-08-19T00:00:00Z",
          readiness_status: "review_required",
          decision_ready: false,
          blocking_reasons: ["incomplete_article_insights"],
          quality_ready: false,
          quality_blocking_reasons: ["incomplete_article_insights"],
          article_count: 3,
          complete_article_count: 2,
          article_insight_completeness: 2 / 3,
        }}
      />,
    );

    expect(markup).toContain("succeeded / quality blocked");
    expect(markup).toContain("2/3 complete / draft");
    expect(markup).not.toContain("succeeded / pass");
    expect(markup).not.toContain("pass / draft");
  });

  it("does not label summaries decision-ready when the canonical report ratio is missing", () => {
    const markup = renderToStaticMarkup(
      <ReportLink
        runId="missing-report-ratio-run"
        summary={{
          run_id: "missing-report-ratio-run",
          title: "Missing report ratio",
          covered_from: "2026-08-12T00:00:00Z",
          covered_until: "2026-08-19T00:00:00Z",
          review_state: "approved",
          run_status: "succeeded",
          validation_status: "pass",
          validation_profile: "full",
          source_count: 2,
          distillation_count: 2,
          claim_count: 3,
          signal_count: 1,
          regions: ["global"],
          languages: ["en"],
          lane_coverage: ["regulatory"],
          models: ["model"],
          as_of: "2026-08-19T00:00:00Z",
          readiness_status: "decision_ready",
          decision_ready: true,
          blocking_reasons: [],
          quality_ready: true,
          complete_article_count: 2,
          article_insight_completeness: 1,
          report_sections_complete: 5,
        }}
      />,
    );

    expect(markup).toContain("succeeded / review required");
    expect(markup).not.toContain("Decision-ready");
  });

  it("does not label summaries decision-ready when canonical denominators are missing", () => {
    const markup = renderToStaticMarkup(
      <ReportLink
        runId="missing-denominator-run"
        summary={{
          run_id: "missing-denominator-run",
          title: "Missing denominator",
          covered_from: "2026-08-12T00:00:00Z",
          covered_until: "2026-08-19T00:00:00Z",
          review_state: "approved",
          run_status: "succeeded",
          validation_status: "pass",
          source_count: 2,
          distillation_count: 2,
          claim_count: 3,
          signal_count: 1,
          regions: ["global"],
          languages: ["en"],
          lane_coverage: ["regulatory"],
          models: ["model"],
          as_of: "2026-08-19T00:00:00Z",
          readiness_status: "decision_ready",
          decision_ready: true,
          blocking_reasons: [],
          quality_ready: true,
          complete_article_count: 2,
          article_insight_completeness: 1,
          report_sections_complete: 5,
          report_section_completeness: 1,
        }}
      />,
    );

    expect(markup).toContain("succeeded / review required");
    expect(markup).not.toContain("Decision-ready");
  });

  it("labels summaries decision-ready only with canonical completeness fields", () => {
    const markup = renderToStaticMarkup(
      <ReportLink
        runId="ready-run"
        summary={{
          run_id: "ready-run",
          title: "Ready summary",
          covered_from: "2026-08-12T00:00:00Z",
          covered_until: "2026-08-19T00:00:00Z",
          review_state: "approved",
          run_status: "succeeded",
          validation_status: "pass",
          validation_profile: "full",
          source_count: 2,
          distillation_count: 2,
          claim_count: 3,
          signal_count: 1,
          regions: ["global"],
          languages: ["en"],
          lane_coverage: ["regulatory"],
          models: ["model"],
          as_of: "2026-08-19T00:00:00Z",
          readiness_status: "decision_ready",
          decision_ready: true,
          blocking_reasons: [],
          quality_ready: true,
          quality_report_ready: true,
          quality_readiness_status: "decision_ready",
          quality_blocking_reasons: [],
          article_count: 2,
          complete_article_count: 2,
          article_insight_completeness: 1,
          report_section_count: 5,
          report_sections_complete: 5,
          report_section_completeness: 1,
        }}
      />,
    );

    expect(markup).toContain("Decision-ready");
  });

  it("does not label canary or draft summaries decision-ready", () => {
    const baseSummary = {
      run_id: "gated-run",
      title: "Gated summary",
      covered_from: "2026-08-12T00:00:00Z",
      covered_until: "2026-08-19T00:00:00Z",
      review_state: "approved",
      run_status: "succeeded",
      validation_status: "pass",
      source_count: 2,
      distillation_count: 2,
      claim_count: 3,
      signal_count: 1,
      regions: ["global"],
      languages: ["en"],
      lane_coverage: ["regulatory"],
      models: ["model"],
      as_of: "2026-08-19T00:00:00Z",
      readiness_status: "decision_ready",
      decision_ready: true,
      blocking_reasons: [],
      quality_ready: true,
      quality_report_ready: true,
      quality_readiness_status: "decision_ready",
      quality_blocking_reasons: [],
      article_count: 2,
      complete_article_count: 2,
      article_insight_completeness: 1,
      report_section_count: 5,
      report_sections_complete: 5,
      report_section_completeness: 1,
      validation_profile: "full",
    };
    const canary = renderToStaticMarkup(
      <ReportLink
        runId="canary-run"
        summary={{ ...baseSummary, run_id: "canary-run", validation_profile: "canary" }}
      />,
    );
    const draft = renderToStaticMarkup(
      <ReportLink
        runId="draft-run"
        summary={{ ...baseSummary, run_id: "draft-run", review_state: "draft" }}
      />,
    );

    expect(canary).not.toContain("Decision-ready");
    expect(draft).not.toContain("Decision-ready");
  });

  it("blocks stale ready summaries when quality status fields are missing", () => {
    const markup = renderToStaticMarkup(
      <ReportLink
        runId="stale-quality-status-run"
        summary={{
          run_id: "stale-quality-status-run",
          title: "Stale quality status",
          covered_from: "2026-08-12T00:00:00Z",
          covered_until: "2026-08-19T00:00:00Z",
          review_state: "approved",
          run_status: "succeeded",
          validation_status: "pass",
          source_count: 2,
          distillation_count: 2,
          claim_count: 3,
          signal_count: 1,
          regions: ["global"],
          languages: ["en"],
          lane_coverage: ["regulatory"],
          models: ["model"],
          as_of: "2026-08-19T00:00:00Z",
          readiness_status: "decision_ready",
          decision_ready: true,
          blocking_reasons: [],
          quality_ready: true,
          article_count: 2,
          complete_article_count: 2,
          article_insight_completeness: 1,
          report_section_count: 5,
          report_sections_complete: 5,
          report_section_completeness: 1,
        }}
      />,
    );

    expect(markup).toContain("succeeded / review required");
    expect(markup).not.toContain("Decision-ready");
  });

  it("marks failed validation as non-decision-ready", () => {
    const failedValidationReport: ReportPayload = {
      ...report,
      run: report.run ? { ...report.run, status: "succeeded", error: null } : null,
      validation: report.validation ? { ...report.validation, status: "failed" } : null,
    };

    const markup = renderToStaticMarkup(<ReportAccordion report={failedValidationReport} />);

    expect(markup).toContain("Report is blocked, failed, or partial.");
    expect(markup).toContain("not decision-ready");
  });

  it("uses current reader validation in the primary status and audits the stored status", () => {
    const staleStoredPass: ReportPayload = {
      ...report,
      run: report.run ? { ...report.run, status: "succeeded", error: null } : null,
      validation: report.validation ? { ...report.validation, status: "pass" } : null,
      reader_report: { ...report.reader_report, validation_status: "failed" },
    };

    const markup = renderToStaticMarkup(<ReportAccordion report={staleStoredPass} />);

    expect(markup).toContain("Validation status: failed");
    expect(markup).toContain("Stored validation</dt><dd>pass");
    expect(markup).toContain("Current reader validation</dt><dd>failed");
  });

  it("marks missing validation as non-decision-ready", () => {
    const missingValidationReport: ReportPayload = {
      ...report,
      run: report.run ? { ...report.run, status: "succeeded", error: null } : null,
      validation: null,
    };

    const markup = renderToStaticMarkup(<ReportAccordion report={missingValidationReport} />);

    expect(markup).toContain("status-blocked");
    expect(markup).toContain("Report is blocked, failed, or partial.");
  });

  it("renders structured insight context and section completeness", () => {
    const detailedReport: ReportPayload = {
      ...report,
      brief: {
        ...report.brief,
        executive_bullets: [{
          text: "The source reports a measurable delay.",
          source_urls: ["https://example.com/source"],
          evidence_status: "partially-supported",
          why_it_matters: "The delay can increase importer exposure.",
          next_step: "Compare the signal with a primary port source.",
        }],
        risks: [{
          text: "The delay may increase importer exposure.",
          source_urls: ["https://example.com/source"],
          evidence_status: "partially-supported",
          why_it_matters: "The timing affects cost exposure.",
          next_step: "Check the next port update before changing routing.",
        }],
        follow_up_questions: ["Which primary source confirms the timing?"],
      },
    };

    const markup = renderToStaticMarkup(<ReportAccordion report={detailedReport} />);

    expect(markup).toContain("Why it matters:");
    expect(markup).toContain("Compare the signal with a primary port source.");
    expect(markup).toContain("Three things to know");
    expect(markup).toContain("Check the next port update before changing routing.");
    expect(markup).toContain("Which primary source confirms the timing?");
    expect(markup).toContain("Legacy quality snapshot");
    expect(markup).toContain("not recorded");
  });

  it("blocks every state except succeeded with pass validation", () => {
    const readyReport: ReportPayload = {
      ...report,
      brief: { ...report.brief, review_state: "approved" },
      run: report.run ? { ...report.run, status: "succeeded", error: null } : null,
      validation: report.validation ? { ...report.validation, status: "pass" } : null,
      ready: true,
      readiness_status: "decision_ready",
      blocking_reasons: [],
      quality: {
        ready: true,
        readiness_status: "decision_ready",
        blocking_reasons: [],
        quality_ready: true,
        article_count: 1,
        complete_article_count: 1,
        article_insight_completeness: 1,
        article_quality_issues: {},
        source_distillation_coverage: 1,
        report_section_count: 5,
        report_sections_complete: 5,
        report_section_completeness: 1,
        report_quality_issues: [],
      },
    };
    const blockedReports: ReportPayload[] = [
      { ...readyReport, run: readyReport.run ? { ...readyReport.run, status: "partial" } : null },
      { ...readyReport, run: readyReport.run ? { ...readyReport.run, status: "unknown" } : null },
      { ...readyReport, run: null },
      { ...readyReport, validation: readyReport.validation ? { ...readyReport.validation, status: "partial" } : null },
      { ...readyReport, validation: readyReport.validation ? { ...readyReport.validation, status: "unknown" } : null },
      { ...readyReport, validation: null },
    ];

    for (const blockedReport of blockedReports) {
      const markup = renderToStaticMarkup(<ReportAccordion report={blockedReport} />);
      expect(markup).toContain('role="alert"');
      expect(markup).toContain("not decision-ready");
    }

    const readyMarkup = renderToStaticMarkup(<ReportAccordion report={readyReport} />);
    expect(readyMarkup).not.toContain('role="alert"');
  });

  it("labels legacy reports when no quality snapshot was recorded", () => {
    const markup = renderToStaticMarkup(<ReportAccordion report={{ ...report, quality: undefined }} />);

    expect(markup).toContain("Legacy quality snapshot");
    expect(markup).toContain("Not recorded in this run");
  });

  it("blocks legacy decision-ready reports when quality completeness is missing", () => {
    const markup = renderToStaticMarkup(
      <ReportAccordion
        report={{
          ...report,
          run: report.run ? { ...report.run, status: "succeeded", error: null } : null,
          validation: report.validation ? { ...report.validation, status: "pass" } : null,
          readiness_status: "decision_ready",
          ready: true,
          quality: undefined,
        }}
      />,
    );

    expect(markup).toContain("Review required");
    expect(markup).toContain("Legacy quality snapshot");
    expect(markup).not.toContain("Decision-ready report");
  });

  it("routes report quality messaging through the canonical fail-closed predicate", () => {
    const staleReadyReport: ReportPayload = {
      ...report,
      run: report.run ? { ...report.run, status: "succeeded", error: null } : null,
      validation: report.validation ? { ...report.validation, status: "pass" } : null,
      ready: true,
      readiness_status: "decision_ready",
      blocking_reasons: [],
      quality: {
        ready: false,
        readiness_status: "review_required",
        blocking_reasons: ["quality_review_required"],
        quality_ready: false,
        article_count: 1,
        complete_article_count: 1,
        article_insight_completeness: 1,
        article_quality_issues: {},
        source_distillation_coverage: 1,
        report_section_count: 5,
        report_sections_complete: 5,
        report_section_completeness: 1,
        report_quality_issues: [],
      },
    };

    const markup = renderToStaticMarkup(<ReportAccordion report={staleReadyReport} />);

    expect(markup).toContain("Review required");
    expect(markup).toContain("This run requires review before it can be decision-ready.");
    expect(markup).not.toContain("All required insight sections and article packets are complete.");
    expect(markup).not.toContain("Decision-ready report");
  });
});
