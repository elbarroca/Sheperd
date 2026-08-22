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

export type InsightStatus = "supported" | "not_observed" | "uncertain" | string;

export interface ArticleInsight {
  status: InsightStatus;
  statement: string;
  why_it_matters: string;
  next_step: string;
  evidence_excerpt?: string | null;
  evidence_locator?: string | null;
}

export interface ResearchSignal {
  event_id: string;
  run_id: string;
  event_type: string;
  summary: string;
  geographies: string[];
  ports: string[];
  carriers: string[];
  event_at: string | null;
  source_urls: string[];
  evidence_status: EvidenceStatus;
}

export interface ArticleDistillation {
  source_url: string;
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
  insight_packet?: Record<string, unknown>;
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
    error: string | null;
    neon_branch_id: string | null;
    migration_version: string | null;
    archived?: boolean;
    archived_at?: string | null;
    archive_reason?: string | null;
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
  distillations: ArticleDistillation[];
  claims: ResearchClaim[];
  signals: ResearchSignal[];
  as_of: string;
  covered_from: string;
  covered_until: string;
}

export interface MonthlyRollup {
  month: string;
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
}

export interface SourceExplorerItem {
  source: ResearchSource;
  distillation: ArticleDistillation | null;
  claims: ResearchClaim[];
  source_hash: string | null;
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
  migration_version: string;
  branch_id: string | null;
  database: string;
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

function isNullableString(value: unknown): value is string | null {
  return value === null || isString(value);
}

function isStringArray(value: unknown): value is string[] {
  return Array.isArray(value) && value.every(isString);
}

function isNumber(value: unknown): value is number {
  return typeof value === "number" && Number.isFinite(value);
}

function isNullableNumber(value: unknown): value is number | null {
  return value === null || isNumber(value);
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
    && hasStrings(value, ["text", "evidence_status"])
    && isStringArray(value.source_urls)
    && isOptional(value, "why_it_matters", isString)
    && isOptional(value, "next_step", isString);
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
    && isStringArray(value.uncertainties)
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
    && hasStrings(value, ["run_id", "status", "as_of"])
    && isNullableString(value.error)
    && isNullableString(value.neon_branch_id)
    && isNullableString(value.migration_version)
    && isOptional(value, "archived", (candidate) => typeof candidate === "boolean")
    && isOptional(value, "archived_at", isNullableString)
    && isOptional(value, "archive_reason", isNullableString);
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
    && isOptional(value, "normalized_snippet_en", isNullableString);
}

function isResearchClaim(value: unknown): value is ResearchClaim {
  return isRecord(value)
    && hasStrings(value, ["claim", "evidence_status", "confidence"])
    && isStringArray(value.source_urls)
    && isNullableString(value.support_locator)
    && isStringArray(value.conflicts)
    && isOptional(value, "original_claim", isNullableString)
    && isOptional(value, "evidence_excerpt", isNullableString)
    && isOptional(value, "independent_source_count", isNonNegativeInteger)
    && isOptional(value, "citation_status", isString)
    && isOptional(value, "verification_basis", isNullableString);
}

function isResearchSignal(value: unknown): value is ResearchSignal {
  return isRecord(value)
    && hasStrings(value, ["event_id", "run_id", "event_type", "summary", "evidence_status"])
    && isStringArray(value.geographies)
    && isStringArray(value.ports)
    && isStringArray(value.carriers)
    && isNullableString(value.event_at)
    && isStringArray(value.source_urls);
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
    && isOptional(value, "source_language", isString)
    && isOptional(value, "summary_original", isString)
    && isOptional(value, "key_points_original", isStringArray)
    && isOptional(value, "translation_status", isString)
    && isOptional(value, "evidence_excerpts", isStringArray)
    && isOptional(value, "evidence_locators", isStringArray);
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
    && Array.isArray(value.distillations)
    && value.distillations.every(isArticleDistillation)
    && Array.isArray(value.claims)
    && value.claims.every(isResearchClaim)
    && Array.isArray(value.signals)
    && value.signals.every(isResearchSignal)
    && hasStrings(value, ["as_of", "covered_from", "covered_until"]);
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
    && value.status === "pass"
    && isString(value.migration_version)
    && isNullableString(value.branch_id)
    && isString(value.database);
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
    && isNullableString(value.source_hash);
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

export function getMonthlyRollups(): Promise<ResearchResponse<MonthlyResponse>> {
  return getJson("/api/reports/monthly", (value) => isMonthlyResponse(value) ? value : null);
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
