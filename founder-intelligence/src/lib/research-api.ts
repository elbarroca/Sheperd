import "server-only";

export type EvidenceStatus =
  | "verified"
  | "partially-supported"
  | "contradicted"
  | "unverified"
  | "mixed"
  | string;

export interface ReportBullet {
  text: string;
  source_urls: string[];
  evidence_status: EvidenceStatus;
  why_it_matters?: string;
  next_step?: string;
}

export interface WeeklyBrief {
  run_id: string;
  title: string;
  covered_from: string;
  covered_until: string;
  summary: string;
  source_urls: string[];
  limitations: string[];
  review_state: string;
  evidence_status: EvidenceStatus;
  model_id: string;
  prompt_version: string;
  executive_bullets: ReportBullet[];
  developments: ReportBullet[];
  risks: ReportBullet[];
  opportunities: ReportBullet[];
  uncertainties: ReportBullet[];
  follow_up_questions: string[];
}

export interface ResearchSource {
  url: string;
  title: string;
  publisher: string;
  published_at: string | null;
  retrieved_at: string;
  source_kind: string;
  snippet: string;
  topics: string[];
  geographies: string[];
  lane: string;
  is_seed: boolean;
  evidence_status: EvidenceStatus;
  region?: string;
  language_code?: string;
  language_confidence?: number;
  authority_tier?: string;
  catalog_source_id?: string | null;
  source_type?: string;
  freshness_status?: string;
  freshness_days?: number | null;
  extraction_status?: string;
  extraction_error_code?: string | null;
  normalized_title_en?: string | null;
  normalized_snippet_en?: string | null;
  period_status?: string;
  period_basis?: string;
  eligible_for_weekly?: boolean;
  page_type?: string;
  direct_content?: boolean;
  search_published_at?: string | null;
  page_published_at?: string | null;
  publication_date_basis?: string;
  publication_date_locator?: string | null;
  parent_navigation_url?: string | null;
}

export interface ResearchClaim {
  claim: string;
  source_urls: string[];
  evidence_status: EvidenceStatus;
  confidence: string;
  support_locator: string | null;
  conflicts: string[];
  original_claim?: string | null;
  evidence_excerpt?: string | null;
  independent_source_count?: number;
  citation_status?: string;
  verification_basis?: string | null;
}

export type InsightStatus = "supported" | "not_observed" | "uncertain";

export interface ArticleInsight {
  status: InsightStatus;
  statement: string;
  why_it_matters: string;
  next_step: string;
  evidence_excerpt?: string | null;
  evidence_locator?: string | null;
}

export interface DecisionScore {
  sheperd_relevance: number;
  operational_impact: number;
  actionability: number;
  recency: number;
  source_authority: number;
  total: number;
  priority: string;
  rationale: Record<string, string>;
}

export interface ReaderArticle {
  source_url: string;
  headline: string;
  publisher: string;
  published_at: string | null;
  event_at: string | null;
  date_basis: string;
  date_locator: string | null;
  retrieved_at: string;
  page_type: string;
  score: DecisionScore | null;
  key_points: string[];
  what_changed: string;
  why_sheperd_cares: string;
  recommended_action: string;
  risk: string | null;
  opportunity: string | null;
  limitations: string[];
  lane: string;
  region: string;
  eligible_for_weekly: boolean;
  validation_status: string;
}

export interface ReaderSourceIndexEntry {
  url: string;
  title: string;
  publisher: string;
  published_at: string | null;
  date_basis: string;
  page_type: string;
  eligible_for_weekly: boolean;
  validation_status: string;
}

export interface ReaderReport {
  run_id: string;
  title: string;
  covered_from: string;
  covered_until: string;
  report_status: string;
  validation_status: string;
  readiness_status: string;
  canonical_hash: string;
  three_things: string[];
  top_action: string;
  ranked_articles: ReaderArticle[];
  watchlist: ReaderArticle[];
  background_articles: ReaderArticle[];
  source_index: ReaderSourceIndexEntry[];
}

export interface ResearchSignal {
  event_id: string;
  run_id: string;
  event_type: string;
  summary: string;
  headline: string;
  what_changed: string;
  geographies: string[];
  ports: string[];
  carriers: string[];
  event_at: string | null;
  published_at: string | null;
  retrieved_at: string | null;
  period_status: string | null;
  period_basis: string | null;
  eligible_for_weekly: boolean;
  region: string;
  lane: string;
  source_urls: string[];
  evidence_locator: string | null;
  impact: string;
  risk: string;
  opportunity: string;
  next_step: string;
  limitations: string[];
  evidence_status: EvidenceStatus;
}

export interface ArticleDistillation {
  source_url: string;
  headline?: string;
  event_type?: string;
  event_at?: string | null;
  event_at_locator?: string | null;
  summary: string;
  key_points: string[];
  entities: string[];
  signals: string[];
  claims: ResearchClaim[];
  limitations: string[];
  published_at: string | null;
  model_id: string;
  prompt_version: string;
  evidence_status: EvidenceStatus;
  content_hash: string | null;
  source_language?: string;
  summary_original?: string;
  key_points_original?: string[];
  translation_status?: string;
  evidence_excerpts?: string[];
  evidence_locators?: string[];
  what_happened?: string;
  why_it_matters?: string;
  risk_assessment?: ArticleInsight | null;
  opportunity_assessment?: ArticleInsight | null;
  uncertainties?: string[];
  next_steps?: string[];
  quality_status?: string;
  quality_issues?: string[];
  decision_score?: DecisionScore | null;
  insight_packet?: Record<string, unknown>;
}

export interface ArticleFulfillment {
  source_url: string;
  status: string;
  complete: boolean;
  source_persisted: boolean;
  extracted: boolean;
  distillation_persisted: boolean;
  claims_persisted: boolean;
  claim_count: number;
  citation_count: number;
  citation_complete: boolean;
  ui_displayable: boolean;
  missing_fields: string[];
  quality_issues: string[];
}

export interface QualitySnapshot {
  ready: boolean;
  readiness_status: string;
  blocking_reasons: string[];
  quality_ready: boolean;
  article_count: number;
  complete_article_count: number;
  article_insight_completeness: number;
  article_quality_issues: Record<string, string[]>;
  source_distillation_coverage: number;
  report_section_count: number;
  report_sections_complete: number;
  report_section_completeness: number;
  report_quality_issues: string[];
  article_fulfillment?: ArticleFulfillment[];
}

export interface ToolCallReceipt {
  agent_name?: string;
  lane?: string;
  attempt?: number;
  call_index?: number;
  tool_name: string;
  sanitized_args?: Record<string, string | number | boolean | null>;
  query?: string | null;
  urls?: string[];
  input_hash?: string | null;
  result_hash?: string | null;
  result_count?: number | null;
  latency_ms?: number | null;
  status: string;
  error_code?: string | null;
  created_at?: string | null;
}

export interface ValidationReport {
  run_id: string;
  status: string;
  citation_coverage: number;
  lane_coverage: string[];
  checks: Array<{
    name: string;
    status: string;
    observed?: string | number | boolean | null;
    expected?: string | number | boolean | null;
    message: string;
  }>;
}

export interface AgentStep {
  agent_name: string;
  status: string;
  lane: string;
  attempt: number;
  duration_ms: number | null;
  error_code: string | null;
  input_hash?: string | null;
  output_hash?: string | null;
  prompt_version?: string | null;
  request_id?: string | null;
  wall_clock_ms?: number | null;
  tool_calls?: number | null;
  capability_manifest_hash?: string | null;
  required_tools?: string[];
  requested_model?: string | null;
  resolved_model?: string | null;
  fallback_reason?: string | null;
  input_tokens?: number | null;
  output_tokens?: number | null;
  total_tokens?: number | null;
  created_at?: string | null;
}

export interface ReportPayload {
  brief: WeeklyBrief;
  run: {
    run_id: string;
    status: string;
    as_of: string;
    error?: string | null;
    error_code?: string | null;
    neon_branch_id: string | null;
    migration_version: string | null;
    validation_profile?: string;
    archived?: boolean;
    archived_at?: string | null;
    archive_reason?: string | null;
    run_kind: string;
    parent_run_id: string | null;
    repair_round: number | null;
    context_version: string;
    research_timezone: string;
  } | null;
  validation: ValidationReport | null;
  lane_coverage: string[];
  models: string[];
  requested_models?: string[];
  resolved_models?: string[];
  steps: AgentStep[];
  tool_calls?: ToolCallReceipt[];
  sources: ResearchSource[];
  source_hashes: string[];
  source_hash_by_url: Record<string, string>;
  distillations: ArticleDistillation[];
  claims: ResearchClaim[];
  signals: ResearchSignal[];
  as_of: string;
  covered_from: string;
  covered_until: string;
  quality?: QualitySnapshot;
  ready?: boolean;
  readiness_status?: string;
  blocking_reasons?: string[];
  period_counts?: Record<string, number>;
  source_periods?: Record<string, {
    period_status: string;
    period_basis: string;
    eligible_for_weekly: boolean;
  }>;
  cost_estimate?: CostEstimate;
  pdf: PdfArtifact;
  canonical_hash: string;
  reader_report: ReaderReport;
}

export interface CostEstimate {
  model: string;
  input_tokens: number;
  output_tokens: number;
  llm_estimated_usd: number;
  tavily: {
    search_calls: number;
    extracted_urls: number;
    search_credits: number;
    extract_credits: number;
    credits: number;
    estimated_usd: number;
    free_allowance_credits: number;
  };
  estimated_provider_usd: number;
  rate_card: {
    retrieved_at: string;
    openai: {
      model: string;
      input_usd_per_million_tokens: number;
      output_usd_per_million_tokens: number;
      source_url: string;
      basis: string;
    };
    tavily: {
      search_credits_per_call: number;
      extract_urls_per_credit: number;
      usd_per_credit: number;
      free_credits_per_month: number;
      credits_source_url: string;
      pricing_source_url: string;
    };
    vercel: {
      pricing_source_url: string;
      blob_pricing_source_url: string;
    };
  };
}

export interface PdfArtifact {
  available: boolean;
  url: string | null;
  uploaded_at: string | null;
  content_hash: string | null;
  canonical_hash: string;
  unavailable_reason: string | null;
}

export interface MonthlyRollup {
  month: string;
  date?: string;
  signals: number;
  runs: number;
  geographies: string[];
  region?: string;
  language?: string;
  lane?: string;
  authority?: string;
  signal?: string;
  evidence?: string;
}

export interface WeeklyReportSummary {
  run_id: string;
  title: string;
  covered_from: string;
  covered_until: string;
  review_state: string;
  run_status: string;
  validation_status: string;
  validation_profile?: string | null;
  source_count: number;
  distillation_count: number;
  claim_count: number;
  signal_count: number;
  regions: string[];
  languages: string[];
  lane_coverage: string[];
  models: string[];
  as_of: string;
  archived?: boolean;
  archived_at?: string | null;
  archive_reason?: string | null;
  readiness_status?: string;
  decision_ready?: boolean;
  quality_ready?: boolean;
  quality_report_ready?: boolean;
  quality_readiness_status?: string;
  quality_blocking_reasons?: string[];
  blocking_reasons?: string[];
  article_count?: number;
  article_insight_completeness?: number;
  report_section_completeness?: number;
  complete_article_count?: number;
  report_section_count?: number;
  report_sections_complete?: number;
}

export interface SourceExplorerItem {
  source: ResearchSource;
  distillation: ArticleDistillation | null;
  claims: ResearchClaim[];
  source_hash: string | null;
  fulfillment?: ArticleFulfillment;
}

export interface SourceExplorerPage {
  items: SourceExplorerItem[];
  page: number;
  page_size: number;
  total: number;
  has_more: boolean;
}

export interface SourceFacets {
  regions: string[];
  languages: string[];
  freshness: string[];
  authority: string[];
  source_types: string[];
  lanes: string[];
  evidence_states: string[];
}

type WeeklyReportEntry = WeeklyReportSummary | ReportPayload;

export interface WeeklyResponse {
  reports: WeeklyReportEntry[];
  count: number;
  total?: number;
  limit?: number;
  offset?: number;
  has_more?: boolean;
}

interface MonthlyResponse {
  rollups: MonthlyRollup[];
}

interface SourcesResponse {
  sources: ResearchSource[];
}

interface DistillationsResponse {
  distillations: ArticleDistillation[];
}

interface ClaimsResponse {
  claims: ResearchClaim[];
}

interface RegionsResponse {
  regions: string[];
}

interface SourceFacetsResponse extends SourceFacets {
  status: string;
}

export interface ResearchHealth {
  status: string;
  migration_version: string | null;
  expected_migration_version?: string;
  branch_id: string | null;
  database: string;
  blocking_reasons?: string[];
}

export type ResearchResponse<T> =
  | { status: "ok"; data: T }
  | { status: "unavailable"; error: string };

const API_BASE = (process.env.RESEARCH_API_BASE_URL ?? "http://127.0.0.1:8787").replace(
  /\/$/u,
  "",
);

type JsonRecord = Record<string, unknown>;
type JsonParser<T> = (value: unknown) => T | null;

function isRecord(value: unknown): value is JsonRecord {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function isString(value: unknown): value is string {
  return typeof value === "string";
}

const INSIGHT_STATUSES: ReadonlySet<string> = new Set([
  "supported",
  "not_observed",
  "uncertain",
]);

const PLACEHOLDER_TEXT = new Set([
  "",
  "null",
  "none",
  "n/a",
  "na",
  "not recorded",
  "not available",
  "tbd",
  "to be determined",
  "unknown",
  "unsupported",
]);

function isMeaningfulText(value: unknown): value is string {
  if (!isString(value)) return false;
  const normalized = value.trim().toLowerCase().replace(/\.+$/u, "").replace(/\s+/gu, " ");
  return normalized.length > 0
    && !PLACEHOLDER_TEXT.has(normalized)
    && !normalized.startsWith("not recorded ")
    && !normalized.startsWith("not available ");
}

function isNullableMeaningfulText(value: unknown): value is string | null {
  return value === null || isMeaningfulText(value);
}

function isInsightStatus(value: unknown): value is InsightStatus {
  return isString(value) && INSIGHT_STATUSES.has(value);
}

function isNullableString(value: unknown): value is string | null {
  return value === null || isString(value);
}

function isStringArray(value: unknown): value is string[] {
  return Array.isArray(value) && value.every(isString);
}

function isNumber(value: unknown): value is number {
  return typeof value === "number" && Number.isFinite(value);
}

function isRatio(value: unknown): value is number {
  return isNumber(value) && value >= 0 && value <= 1;
}

function isNullableNumber(value: unknown): value is number | null {
  return value === null || isNumber(value);
}

function isBoolean(value: unknown): value is boolean {
  return typeof value === "boolean";
}

function isStringArrayRecord(value: unknown): value is Record<string, string[]> {
  return isRecord(value)
    && Object.values(value).every((candidate) => isStringArray(candidate));
}

function isStringRecord(value: unknown): value is Record<string, string> {
  return isRecord(value) && Object.values(value).every(isString);
}

function isSha256(value: unknown): value is string {
  return isString(value) && /^[a-f0-9]{64}$/u.test(value);
}

function isNonNegativeInteger(value: unknown): value is number {
  return typeof value === "number" && Number.isInteger(value) && value >= 0;
}

function hasStrings(value: JsonRecord, fields: string[]): boolean {
  return fields.every((field) => isString(value[field]));
}

function isOptional(
  value: JsonRecord,
  field: string,
  predicate: (candidate: unknown) => boolean,
): boolean {
  return !(field in value) || predicate(value[field]);
}

function isPrimitive(value: unknown): boolean {
  return value === null || isString(value) || typeof value === "boolean" || isNumber(value);
}

function isReportBullet(value: unknown): value is ReportBullet {
  return isRecord(value)
    && isMeaningfulText(value.text)
    && isString(value.evidence_status)
    && isStringArray(value.source_urls)
    && isOptional(value, "why_it_matters", isMeaningfulText)
    && isOptional(value, "next_step", isMeaningfulText);
}

function isWeeklyBrief(value: unknown): value is WeeklyBrief {
  return isRecord(value)
    && hasStrings(value, [
      "run_id",
      "title",
      "covered_from",
      "covered_until",
      "summary",
      "review_state",
      "evidence_status",
      "model_id",
      "prompt_version",
    ])
    && isStringArray(value.source_urls)
    && isStringArray(value.limitations)
    && Array.isArray(value.uncertainties)
    && value.uncertainties.every(isReportBullet)
    && isStringArray(value.follow_up_questions)
    && Array.isArray(value.executive_bullets)
    && value.executive_bullets.every(isReportBullet)
    && Array.isArray(value.developments)
    && value.developments.every(isReportBullet)
    && Array.isArray(value.risks)
    && value.risks.every(isReportBullet)
    && Array.isArray(value.opportunities)
    && value.opportunities.every(isReportBullet);
}

function isReportRun(value: unknown): boolean {
  return isRecord(value)
    && hasStrings(value, [
      "run_id",
      "status",
      "as_of",
      "run_kind",
      "context_version",
      "research_timezone",
    ])
    && isOptional(value, "error", isNullableString)
    && isOptional(value, "error_code", isNullableString)
    && isNullableString(value.neon_branch_id)
    && isNullableString(value.migration_version)
    && isOptional(value, "validation_profile", isString)
    && isOptional(value, "archived", (candidate) => typeof candidate === "boolean")
    && isOptional(value, "archived_at", isNullableString)
    && isOptional(value, "archive_reason", isNullableString)
    && isNullableString(value.parent_run_id)
    && isNullableNumber(value.repair_round);
}

function isValidationCheck(value: unknown): boolean {
  return isRecord(value)
    && hasStrings(value, ["name", "status", "message"])
    && isOptional(value, "observed", isPrimitive)
    && isOptional(value, "expected", isPrimitive);
}

function isValidation(value: unknown): value is ValidationReport {
  return isRecord(value)
    && hasStrings(value, ["run_id", "status"])
    && isNumber(value.citation_coverage)
    && isStringArray(value.lane_coverage)
    && Array.isArray(value.checks)
    && value.checks.every(isValidationCheck);
}

function isAgentStep(value: unknown): value is AgentStep {
  return isRecord(value)
    && hasStrings(value, ["agent_name", "status", "lane"])
    && isNonNegativeInteger(value.attempt)
    && isNullableNumber(value.duration_ms)
    && isNullableString(value.error_code)
    && isOptional(value, "input_hash", isNullableString)
    && isOptional(value, "output_hash", isNullableString)
    && isOptional(value, "prompt_version", isNullableString)
    && isOptional(value, "request_id", isNullableString)
    && isOptional(value, "wall_clock_ms", isNullableNumber)
    && isOptional(value, "tool_calls", isNullableNumber)
    && isOptional(value, "capability_manifest_hash", isNullableString)
    && isOptional(value, "required_tools", isStringArray)
    && isOptional(value, "requested_model", isNullableString)
    && isOptional(value, "resolved_model", isNullableString)
    && isOptional(value, "fallback_reason", isNullableString)
    && isOptional(value, "input_tokens", isNullableNumber)
    && isOptional(value, "output_tokens", isNullableNumber)
    && isOptional(value, "total_tokens", isNullableNumber)
    && isOptional(value, "created_at", isNullableString);
}

function isSafeArgs(value: unknown): boolean {
  return isRecord(value) && Object.values(value).every(isPrimitive);
}

function isToolCall(value: unknown): value is ToolCallReceipt {
  return isRecord(value)
    && hasStrings(value, ["tool_name", "status"])
    && isOptional(value, "agent_name", isNullableString)
    && isOptional(value, "lane", isNullableString)
    && isOptional(value, "attempt", isNullableNumber)
    && isOptional(value, "call_index", isNullableNumber)
    && isOptional(value, "sanitized_args", isSafeArgs)
    && isOptional(value, "query", isNullableString)
    && isOptional(value, "urls", isStringArray)
    && isOptional(value, "input_hash", isNullableString)
    && isOptional(value, "result_hash", isNullableString)
    && isOptional(value, "result_count", isNullableNumber)
    && isOptional(value, "latency_ms", isNullableNumber)
    && isOptional(value, "error_code", isNullableString)
    && isOptional(value, "created_at", isNullableString);
}

function isResearchSource(value: unknown): value is ResearchSource {
  return isRecord(value)
    && hasStrings(value, [
      "url",
      "title",
      "publisher",
      "retrieved_at",
      "source_kind",
      "snippet",
      "lane",
      "evidence_status",
    ])
    && isNullableString(value.published_at)
    && isStringArray(value.topics)
    && isStringArray(value.geographies)
    && typeof value.is_seed === "boolean"
    && isOptional(value, "region", isString)
    && isOptional(value, "language_code", isString)
    && isOptional(value, "language_confidence", isNumber)
    && isOptional(value, "authority_tier", isString)
    && isOptional(value, "catalog_source_id", isNullableString)
    && isOptional(value, "source_type", isString)
    && isOptional(value, "freshness_status", isString)
    && isOptional(value, "freshness_days", isNullableNumber)
    && isOptional(value, "extraction_status", isString)
    && isOptional(value, "extraction_error_code", isNullableString)
    && isOptional(value, "normalized_title_en", isNullableString)
    && isOptional(value, "normalized_snippet_en", isNullableString)
    && isOptional(value, "period_status", isString)
    && isOptional(value, "period_basis", isString)
    && isOptional(value, "eligible_for_weekly", isBoolean)
    && isOptional(value, "page_type", isString)
    && isOptional(value, "direct_content", isBoolean)
    && isOptional(value, "search_published_at", isNullableString)
    && isOptional(value, "page_published_at", isNullableString)
    && isOptional(value, "publication_date_basis", isString)
    && isOptional(value, "publication_date_locator", isNullableString)
    && isOptional(value, "parent_navigation_url", isNullableString);
}

function isResearchClaim(value: unknown): value is ResearchClaim {
  return isRecord(value)
    && isMeaningfulText(value.claim)
    && hasStrings(value, ["evidence_status", "confidence"])
    && isStringArray(value.source_urls)
    && isNullableMeaningfulText(value.support_locator)
    && isStringArray(value.conflicts)
    && isOptional(value, "original_claim", isNullableString)
    && isOptional(value, "evidence_excerpt", isNullableMeaningfulText)
    && isOptional(value, "independent_source_count", isNonNegativeInteger)
    && isOptional(value, "citation_status", isString)
    && isOptional(value, "verification_basis", isNullableString);
}

function isResearchSignal(value: unknown): value is ResearchSignal {
  return isRecord(value)
    && hasStrings(value, [
      "event_id",
      "run_id",
      "event_type",
      "summary",
      "headline",
      "what_changed",
      "region",
      "lane",
      "impact",
      "risk",
      "opportunity",
      "next_step",
      "evidence_status",
    ])
    && isStringArray(value.geographies)
    && isStringArray(value.ports)
    && isStringArray(value.carriers)
    && isNullableString(value.event_at)
    && isNullableString(value.published_at)
    && isNullableString(value.retrieved_at)
    && isNullableString(value.period_status)
    && isNullableString(value.period_basis)
    && isBoolean(value.eligible_for_weekly)
    && isStringArray(value.source_urls)
    && isNullableString(value.evidence_locator)
    && isStringArray(value.limitations);
}

function isArticleInsight(value: unknown): value is ArticleInsight {
  if (!(
    isRecord(value)
    && isInsightStatus(value.status)
    && isMeaningfulText(value.statement)
    && isMeaningfulText(value.why_it_matters)
    && isMeaningfulText(value.next_step)
    && isOptional(value, "evidence_excerpt", isNullableMeaningfulText)
    && isOptional(value, "evidence_locator", isNullableMeaningfulText)
  )) return false;
  if (value.status !== "supported") return true;
  return Boolean(
    typeof value.evidence_excerpt === "string" && value.evidence_excerpt.trim()
    || typeof value.evidence_locator === "string" && value.evidence_locator.trim(),
  );
}

function isDecisionScore(value: unknown): value is DecisionScore {
  if (!isRecord(value) || !isString(value.priority) || !isStringRecord(value.rationale)) {
    return false;
  }
  const components = [
    value.sheperd_relevance,
    value.operational_impact,
    value.actionability,
    value.recency,
    value.source_authority,
  ];
  return components.every(isNonNegativeInteger)
    && isNonNegativeInteger(value.total)
    && components.reduce((sum, component) => sum + component, 0) === value.total;
}

function isReaderArticle(value: unknown): value is ReaderArticle {
  return isRecord(value)
    && hasStrings(value, [
      "source_url",
      "headline",
      "publisher",
      "date_basis",
      "retrieved_at",
      "page_type",
      "what_changed",
      "why_sheperd_cares",
      "recommended_action",
      "lane",
      "region",
      "validation_status",
    ])
    && isNullableString(value.published_at)
    && isNullableString(value.event_at)
    && isNullableString(value.date_locator)
    && (value.score === null || isDecisionScore(value.score))
    && isStringArray(value.key_points)
    && isNullableString(value.risk)
    && isNullableString(value.opportunity)
    && isStringArray(value.limitations)
    && isBoolean(value.eligible_for_weekly);
}

function isReaderSourceIndexEntry(value: unknown): value is ReaderSourceIndexEntry {
  return isRecord(value)
    && hasStrings(value, [
      "url",
      "title",
      "publisher",
      "date_basis",
      "page_type",
      "validation_status",
    ])
    && isNullableString(value.published_at)
    && isBoolean(value.eligible_for_weekly);
}

function isReaderReport(value: unknown): value is ReaderReport {
  return isRecord(value)
    && hasStrings(value, [
      "run_id",
      "title",
      "covered_from",
      "covered_until",
      "report_status",
      "validation_status",
      "readiness_status",
      "top_action",
    ])
    && isSha256(value.canonical_hash)
    && isStringArray(value.three_things)
    && Array.isArray(value.ranked_articles)
    && value.ranked_articles.every(isReaderArticle)
    && Array.isArray(value.watchlist)
    && value.watchlist.every(isReaderArticle)
    && Array.isArray(value.background_articles)
    && value.background_articles.every(isReaderArticle)
    && Array.isArray(value.source_index)
    && value.source_index.every(isReaderSourceIndexEntry);
}

function isArticleDistillation(value: unknown): value is ArticleDistillation {
  return isRecord(value)
    && hasStrings(value, ["source_url", "summary", "model_id", "prompt_version", "evidence_status"])
    && isStringArray(value.key_points)
    && isStringArray(value.entities)
    && isStringArray(value.signals)
    && Array.isArray(value.claims)
    && value.claims.every(isResearchClaim)
    && isStringArray(value.limitations)
    && isNullableString(value.published_at)
    && isNullableString(value.content_hash)
    && isOptional(value, "headline", isString)
    && isOptional(value, "event_type", isString)
    && isOptional(value, "event_at", isNullableString)
    && isOptional(value, "event_at_locator", isNullableString)
    && isOptional(value, "source_language", isString)
    && isOptional(value, "summary_original", isString)
    && isOptional(value, "key_points_original", isStringArray)
    && isOptional(value, "translation_status", isString)
    && isOptional(value, "evidence_excerpts", isStringArray)
    && isOptional(value, "evidence_locators", isStringArray)
    && isOptional(value, "what_happened", isString)
    && isOptional(value, "why_it_matters", isString)
    && isOptional(value, "risk_assessment", (candidate) =>
      candidate === null || isArticleInsight(candidate)
    )
    && isOptional(value, "opportunity_assessment", (candidate) =>
      candidate === null || isArticleInsight(candidate)
    )
    && isOptional(value, "uncertainties", isStringArray)
    && isOptional(value, "next_steps", isStringArray)
    && isOptional(value, "quality_status", isString)
    && isOptional(value, "quality_issues", isStringArray)
    && isOptional(value, "decision_score", (candidate) =>
      candidate === null || isDecisionScore(candidate)
    )
    && isOptional(value, "insight_packet", isRecord);
}

function isArticleFulfillment(value: unknown): value is ArticleFulfillment {
  return isRecord(value)
    && hasStrings(value, ["source_url", "status"])
    && isBoolean(value.complete)
    && isBoolean(value.source_persisted)
    && isBoolean(value.extracted)
    && isBoolean(value.distillation_persisted)
    && isBoolean(value.claims_persisted)
    && isNonNegativeInteger(value.claim_count)
    && isNonNegativeInteger(value.citation_count)
    && isBoolean(value.citation_complete)
    && isBoolean(value.ui_displayable)
    && isStringArray(value.missing_fields)
    && isStringArray(value.quality_issues);
}

function isQualitySnapshot(value: unknown): value is QualitySnapshot {
  return isRecord(value)
    && isBoolean(value.ready)
    && isString(value.readiness_status)
    && isStringArray(value.blocking_reasons)
    && isBoolean(value.quality_ready)
    && isNonNegativeInteger(value.article_count)
    && isNonNegativeInteger(value.complete_article_count)
    && isRatio(value.article_insight_completeness)
    && isStringArrayRecord(value.article_quality_issues)
    && isRatio(value.source_distillation_coverage)
    && isNonNegativeInteger(value.report_section_count)
    && isNonNegativeInteger(value.report_sections_complete)
    && isRatio(value.report_section_completeness)
    && isStringArray(value.report_quality_issues)
    && isOptional(value, "article_fulfillment", (candidate) =>
      Array.isArray(candidate) && candidate.every(isArticleFulfillment)
    );
}

function isReportPayload(value: unknown): value is ReportPayload {
  return isRecord(value)
    && isWeeklyBrief(value.brief)
    && (value.run === null || isReportRun(value.run))
    && (value.validation === null || isValidation(value.validation))
    && isStringArray(value.lane_coverage)
    && isStringArray(value.models)
    && isOptional(value, "requested_models", isStringArray)
    && isOptional(value, "resolved_models", isStringArray)
    && Array.isArray(value.steps)
    && value.steps.every(isAgentStep)
    && isOptional(value, "tool_calls", (candidate) => Array.isArray(candidate) && candidate.every(isToolCall))
    && Array.isArray(value.sources)
    && value.sources.every(isResearchSource)
    && isStringArray(value.source_hashes)
    && isStringRecord(value.source_hash_by_url)
    && Array.isArray(value.distillations)
    && value.distillations.every(isArticleDistillation)
    && Array.isArray(value.claims)
    && value.claims.every(isResearchClaim)
    && Array.isArray(value.signals)
    && value.signals.every(isResearchSignal)
    && hasStrings(value, ["as_of", "covered_from", "covered_until"])
    && isOptional(value, "quality", isQualitySnapshot)
    && isOptional(value, "ready", isBoolean)
    && isOptional(value, "readiness_status", isString)
    && isOptional(value, "blocking_reasons", isStringArray)
    && isOptional(value, "period_counts", (candidate) =>
      isRecord(candidate) && Object.values(candidate).every(isNonNegativeInteger)
    )
    && isOptional(value, "source_periods", isRecord)
    && isOptional(value, "cost_estimate", isCostEstimate)
    && isPdfArtifact(value.pdf)
    && isSha256(value.canonical_hash)
    && isReaderReport(value.reader_report)
    && value.reader_report.run_id === value.brief.run_id
    && value.reader_report.canonical_hash === value.canonical_hash
    && value.pdf.canonical_hash === value.canonical_hash;
}

function isPdfArtifact(value: unknown): value is PdfArtifact {
  return isRecord(value)
    && isBoolean(value.available)
    && isNullableString(value.url)
    && isNullableString(value.uploaded_at)
    && isNullableString(value.content_hash)
    && isSha256(value.canonical_hash)
    && isNullableString(value.unavailable_reason);
}

function isCostEstimate(value: unknown): value is CostEstimate {
  if (!isRecord(value) || !isString(value.model)) return false;
  if (!isNonNegativeInteger(value.input_tokens)
    || !isNonNegativeInteger(value.output_tokens)
    || !isNumber(value.llm_estimated_usd)
    || !isNumber(value.estimated_provider_usd)
    || !isRecord(value.tavily)
    || !isRecord(value.rate_card)
    || !isString(value.rate_card.retrieved_at)
    || !isRecord(value.rate_card.openai)
    || !isRecord(value.rate_card.tavily)
    || !isRecord(value.rate_card.vercel)) return false;
  return isNonNegativeInteger(value.tavily.search_calls)
    && isNonNegativeInteger(value.tavily.extracted_urls)
    && isNonNegativeInteger(value.tavily.search_credits)
    && isNonNegativeInteger(value.tavily.extract_credits)
    && isNonNegativeInteger(value.tavily.credits)
    && isNumber(value.tavily.estimated_usd)
    && isNonNegativeInteger(value.tavily.free_allowance_credits)
    && isString(value.rate_card.openai.model)
    && isNumber(value.rate_card.openai.input_usd_per_million_tokens)
    && isNumber(value.rate_card.openai.output_usd_per_million_tokens)
    && isString(value.rate_card.openai.source_url)
    && isString(value.rate_card.openai.basis)
    && isNumber(value.rate_card.tavily.search_credits_per_call)
    && isNumber(value.rate_card.tavily.extract_urls_per_credit)
    && isNumber(value.rate_card.tavily.usd_per_credit)
    && isNonNegativeInteger(value.rate_card.tavily.free_credits_per_month)
    && isString(value.rate_card.tavily.credits_source_url)
    && isString(value.rate_card.tavily.pricing_source_url)
    && isString(value.rate_card.vercel.pricing_source_url)
    && isString(value.rate_card.vercel.blob_pricing_source_url);
}

function hasConsistentReportIdentities(value: ReportPayload): boolean {
  return value.run?.run_id === value.brief.run_id
    && (value.validation === null || value.validation.run_id === value.brief.run_id);
}

function isWeeklyReportSummary(value: unknown): value is WeeklyReportSummary {
  return isRecord(value)
    && hasStrings(value, [
      "run_id",
      "title",
      "covered_from",
      "covered_until",
      "review_state",
      "run_status",
      "validation_status",
      "as_of",
    ])
    && isNonNegativeInteger(value.source_count)
    && isNonNegativeInteger(value.distillation_count)
    && isNonNegativeInteger(value.claim_count)
    && isNonNegativeInteger(value.signal_count)
    && isStringArray(value.regions)
    && isStringArray(value.languages)
    && isStringArray(value.lane_coverage)
    && isStringArray(value.models)
    && isOptional(value, "readiness_status", isString)
    && isOptional(value, "validation_profile", (candidate) =>
      candidate === null || isString(candidate)
    )
    && isOptional(value, "decision_ready", isBoolean)
    && isOptional(value, "quality_ready", isBoolean)
    && isOptional(value, "quality_report_ready", isBoolean)
    && isOptional(value, "quality_readiness_status", isString)
    && isOptional(value, "quality_blocking_reasons", isStringArray)
    && isOptional(value, "blocking_reasons", isStringArray)
    && isOptional(value, "article_count", isNonNegativeInteger)
    && isOptional(value, "article_insight_completeness", isRatio)
    && isOptional(value, "report_section_completeness", isRatio)
    && isOptional(value, "complete_article_count", isNonNegativeInteger)
    && isOptional(value, "report_section_count", isNonNegativeInteger)
    && isOptional(value, "report_sections_complete", isNonNegativeInteger)
    && isOptional(value, "archived", (candidate) => typeof candidate === "boolean")
    && isOptional(value, "archived_at", isNullableString)
    && isOptional(value, "archive_reason", isNullableString);
}

function isReportForRun(value: unknown, runId: string): value is ReportPayload {
  return isReportPayload(value)
    && value.brief.run_id === runId
    && value.run?.run_id === runId
    && value.validation?.run_id === runId;
}

function isHealthPayload(value: unknown): value is ResearchHealth {
  return isRecord(value)
    && (value.status === "pass" || value.status === "blocked")
    && isNullableString(value.migration_version)
    && isOptional(value, "expected_migration_version", isString)
    && isNullableString(value.branch_id)
    && isString(value.database)
    && isOptional(value, "blocking_reasons", isStringArray);
}

function isWeeklyResponse(value: unknown): value is WeeklyResponse {
  return isRecord(value)
    && isNonNegativeInteger(value.count)
    && Array.isArray(value.reports)
    && value.reports.every(
      (report) =>
        isWeeklyReportSummary(report)
        || (isReportPayload(report) && hasConsistentReportIdentities(report)),
    )
    && isOptional(value, "total", isNonNegativeInteger)
    && isOptional(value, "limit", isNonNegativeInteger)
    && isOptional(value, "offset", isNonNegativeInteger)
    && isOptional(value, "has_more", (candidate) => typeof candidate === "boolean");
}

function isMonthlyRollup(value: unknown): value is MonthlyRollup {
  return isRecord(value)
    && hasStrings(value, ["month"])
    && isOptional(value, "date", isString)
    && isNonNegativeInteger(value.signals)
    && isNonNegativeInteger(value.runs)
    && isStringArray(value.geographies)
    && isOptional(value, "region", isString)
    && isOptional(value, "language", isString)
    && isOptional(value, "lane", isString)
    && isOptional(value, "authority", isString)
    && isOptional(value, "signal", isString)
    && isOptional(value, "evidence", isString);
}

function isMonthlyResponse(value: unknown): value is MonthlyResponse {
  return isRecord(value)
    && Array.isArray(value.rollups)
    && value.rollups.every(isMonthlyRollup);
}

function isSourcesResponse(value: unknown): value is SourcesResponse {
  return isRecord(value) && Array.isArray(value.sources) && value.sources.every(isResearchSource);
}

function isDistillationsResponse(value: unknown): value is DistillationsResponse {
  return isRecord(value)
    && Array.isArray(value.distillations)
    && value.distillations.every(isArticleDistillation);
}

function isClaimsResponse(value: unknown): value is ClaimsResponse {
  return isRecord(value) && Array.isArray(value.claims) && value.claims.every(isResearchClaim);
}

function isSourceExplorerItem(value: unknown): value is SourceExplorerItem {
  return isRecord(value)
    && isResearchSource(value.source)
    && (value.distillation === null || isArticleDistillation(value.distillation))
    && Array.isArray(value.claims)
    && value.claims.every(isResearchClaim)
    && isNullableString(value.source_hash)
    && isOptional(value, "fulfillment", isArticleFulfillment);
}

function isSourceExplorerPage(value: unknown): value is SourceExplorerPage {
  return isRecord(value)
    && Array.isArray(value.items)
    && value.items.every(isSourceExplorerItem)
    && isNonNegativeInteger(value.page)
    && isNonNegativeInteger(value.page_size)
    && isNonNegativeInteger(value.total)
    && typeof value.has_more === "boolean";
}

function isSourceFacetsResponse(value: unknown): value is SourceFacetsResponse {
  return isRecord(value)
    && isString(value.status)
    && isStringArray(value.regions)
    && isStringArray(value.languages)
    && isStringArray(value.freshness)
    && isStringArray(value.authority)
    && isStringArray(value.source_types)
    && isStringArray(value.lanes)
    && isStringArray(value.evidence_states);
}

async function getJson<T>(path: string, parse: JsonParser<T>): Promise<ResearchResponse<T>> {
  try {
    const response = await fetch(`${API_BASE}${path}`, { cache: "no-store" });
    if (!response.ok) return { status: "unavailable", error: `API returned ${response.status}` };
    const data: unknown = await response.json();
    const parsed = parse(data);
    return parsed === null
      ? { status: "unavailable", error: "Research API returned malformed data" }
      : { status: "ok", data: parsed };
  } catch {
    return { status: "unavailable", error: "Research API is unavailable" };
  }
}

export interface ReportListFilters {
  status?: "all" | "ready" | "draft" | "partial" | "failed";
  archive_scope?: "active" | "archived" | "all";
  limit?: number;
  offset?: number;
}

function reportListPath(path: string, filters: ReportListFilters = {}): string {
  const params = new URLSearchParams();
  if (filters.status === "ready") params.set("ready", "true");
  if (filters.status === "draft") params.set("review", "draft");
  if (filters.status === "partial" || filters.status === "failed") {
    params.set("run_status", filters.status);
  }
  if (filters.archive_scope) params.set("archive_scope", filters.archive_scope);
  if (filters.limit !== undefined) params.set("limit", String(filters.limit));
  if (filters.offset !== undefined) params.set("offset", String(filters.offset));
  const suffix = params.toString() ? `?${params.toString()}` : "";
  return `${path}${suffix}`;
}

export function getWeeklyReports(
  filters: ReportListFilters = {},
): Promise<ResearchResponse<WeeklyResponse>> {
  return getJson(reportListPath("/api/reports/weekly", filters), (value) => isWeeklyResponse(value) ? value : null);
}

export function getDailyReports(
  filters: ReportListFilters = {},
): Promise<ResearchResponse<WeeklyResponse>> {
  return getJson(reportListPath("/api/reports/daily", filters), (value) => isWeeklyResponse(value) ? value : null);
}

export function getWeeklyReport(
  runId: string,
  archiveScope: "active" | "archived" | "all" = "active",
): Promise<ResearchResponse<ReportPayload>> {
  const query = archiveScope === "active" ? "" : `?archive_scope=${archiveScope}`;
  return getJson(
    `/api/reports/weekly/${encodeURIComponent(runId)}${query}`,
    (value) => isReportForRun(value, runId) ? value : null,
  );
}

export function getMonthlyRollups(
  filters: { region?: string; language?: string; evidence?: string; limit?: number; offset?: number } = {},
): Promise<ResearchResponse<MonthlyResponse>> {
  const params = new URLSearchParams({ limit: String(filters.limit ?? 1000) });
  for (const [key, value] of Object.entries(filters)) if (value !== undefined && value !== "") params.set(key, String(value));
  return getJson(`/api/reports/monthly?${params.toString()}`, (value) => isMonthlyResponse(value) ? value : null);
}

export function getResearchHealth(): Promise<ResearchResponse<ResearchHealth>> {
  return getJson("/api/health", (value) => isHealthPayload(value) ? value : null);
}

export function getResearchSources(
  filters: {
    query?: string;
    lane?: string;
    geography?: string;
    evidence?: string;
    region?: string;
    language?: string;
    freshness?: string;
    authority_tier?: string;
    source_type?: string;
  } = {},
): Promise<ResearchResponse<SourcesResponse>> {
  const params = new URLSearchParams();
  for (const [key, value] of Object.entries(filters)) if (value) params.set(key, value);
  const suffix = params.toString() ? `?${params.toString()}` : "";
  return getJson(`/api/sources${suffix}`, (value) => isSourcesResponse(value) ? value : null);
}

export function getResearchSourceExplorer(
  filters: {
    query?: string;
    lane?: string;
    geography?: string;
    evidence?: string;
    region?: string;
    language?: string;
    freshness?: string;
    authority_tier?: string;
    source_type?: string;
    page?: number;
    page_size?: number;
  } = {},
): Promise<ResearchResponse<SourceExplorerPage>> {
  const params = new URLSearchParams({
    page: String(filters.page ?? 1),
    page_size: String(filters.page_size ?? 24),
  });
  for (const [key, value] of Object.entries(filters)) {
    if (value !== undefined && value !== "" && key !== "page" && key !== "page_size") {
      params.set(key, String(value));
    }
  }
  return getJson(
    `/api/sources/explorer?${params.toString()}`,
    (value) => isSourceExplorerPage(value) ? value : null,
  );
}

export function getResearchSourceFacets(): Promise<ResearchResponse<SourceFacets>> {
  return getJson(
    "/api/sources/facets",
    (value) => isSourceFacetsResponse(value) ? value : null,
  );
}

export function getResearchDistillations(
  filters: { region?: string; language?: string } = {},
): Promise<ResearchResponse<DistillationsResponse>> {
  const params = new URLSearchParams({ limit: "100" });
  for (const [key, value] of Object.entries(filters)) if (value) params.set(key, value);
  return getJson(
    `/api/distillations?${params.toString()}`,
    (value) => isDistillationsResponse(value) ? value : null,
  );
}

export function getResearchClaims(
  filters: { verification_basis?: string; independent_source_min?: string } = {},
): Promise<ResearchResponse<ClaimsResponse>> {
  const params = new URLSearchParams({ limit: "100" });
  for (const [key, value] of Object.entries(filters)) if (value) params.set(key, value);
  return getJson(`/api/claims?${params.toString()}`, (value) => isClaimsResponse(value) ? value : null);
}

export function getResearchRegions(): Promise<ResearchResponse<RegionsResponse>> {
  return getJson("/api/regions", (value) => {
    if (!isRecord(value) || !isStringArray(value.regions)) return null;
    return { regions: value.regions };
  });
}
