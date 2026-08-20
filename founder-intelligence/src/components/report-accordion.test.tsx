import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";
import type { ReportPayload } from "@/lib/research-api";
import { ReportAccordion } from "./report-accordion";

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
  },
  validation: {
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
  }],
  source_hashes: ["source-hash"],
  as_of: "2026-08-19T00:00:00Z",
  covered_from: "2026-08-12T00:00:00Z",
  covered_until: "2026-08-19T00:00:00Z",
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
  });
});
