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
}

export interface ResearchClaim {
  claim: string;
  source_urls: string[];
  evidence_status: EvidenceStatus;
  confidence: string;
  support_locator: string | null;
  conflicts: string[];
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
}

export interface ValidationReport {
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
  input_tokens?: number | null;
  output_tokens?: number | null;
  total_tokens?: number | null;
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
}

interface WeeklyResponse {
  reports: ReportPayload[];
  count: number;
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

export type ResearchResponse<T> =
  | { status: "ok"; data: T }
  | { status: "unavailable"; error: string };

const API_BASE = (process.env.RESEARCH_API_BASE_URL ?? "http://127.0.0.1:8787").replace(
  /\/$/u,
  "",
);

async function getJson<T>(path: string): Promise<ResearchResponse<T>> {
  try {
    const response = await fetch(`${API_BASE}${path}`, { cache: "no-store" });
    if (!response.ok) return { status: "unavailable", error: `API returned ${response.status}` };
    return { status: "ok", data: (await response.json()) as T };
  } catch {
    return { status: "unavailable", error: "Research API is unavailable" };
  }
}

export function getWeeklyReports(): Promise<ResearchResponse<WeeklyResponse>> {
  return getJson<WeeklyResponse>("/api/reports/weekly");
}

export function getWeeklyReport(runId: string): Promise<ResearchResponse<ReportPayload>> {
  return getJson<ReportPayload>(`/api/reports/weekly/${encodeURIComponent(runId)}`);
}

export function getMonthlyRollups(): Promise<ResearchResponse<MonthlyResponse>> {
  return getJson<MonthlyResponse>("/api/reports/monthly");
}

export function getResearchSources(
  filters: { query?: string; lane?: string; geography?: string; evidence?: string } = {},
): Promise<ResearchResponse<SourcesResponse>> {
  const params = new URLSearchParams();
  for (const [key, value] of Object.entries(filters)) if (value) params.set(key, value);
  const suffix = params.toString() ? `?${params.toString()}` : "";
  return getJson<SourcesResponse>(`/api/sources${suffix}`);
}

export function getResearchDistillations(): Promise<ResearchResponse<DistillationsResponse>> {
  return getJson<DistillationsResponse>("/api/distillations?limit=100");
}

export function getResearchClaims(): Promise<ResearchResponse<ClaimsResponse>> {
  return getJson<ClaimsResponse>("/api/claims?limit=100");
}
