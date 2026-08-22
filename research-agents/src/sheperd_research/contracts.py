from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from typing import Self

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from .settings import STRICT_OPENROUTER_MODEL, is_free_openrouter_model


def utc_now() -> datetime:
    return datetime.now(UTC)


def is_free_model(model: str) -> bool:
    return is_free_openrouter_model(model)


class EvidenceStatus(StrEnum):
    VERIFIED = "verified"
    PARTIALLY_SUPPORTED = "partially-supported"
    CONTRADICTED = "contradicted"
    COMPANY_CLAIM = "company-claim"
    INTERNAL_PROPOSAL = "internal-proposal"
    INTERNAL_OBSERVATION = "internal-observation"
    INTERNAL_DATA = "internal-data"
    INTERNAL_DECISION = "internal-decision"
    INFERENCE = "inference"
    UNVERIFIED = "unverified"
    MIXED = "mixed"
    POLICY = "policy"


class ReviewState(StrEnum):
    DRAFT = "draft"
    NEEDS_REVIEW = "needs_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    SUPERSEDED = "superseded"


class RunStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    PARTIAL = "partial"
    FAILED = "failed"


class ValidationStatus(StrEnum):
    PASS = "pass"
    PARTIAL = "partial"
    BLOCKED = "blocked"
    FAILED = "failed"


class ResearchCadence(StrEnum):
    DAILY = "daily"
    WEEKLY = "weekly"


class FreshnessStatus(StrEnum):
    CURRENT = "current"
    STALE = "stale"
    UNDATED = "undated"
    FUTURE = "future"
    UNKNOWN = "unknown"


class ExtractionStatus(StrEnum):
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    NOT_ATTEMPTED = "not_attempted"


class TranslationStatus(StrEnum):
    NOT_NEEDED = "not_needed"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


class InsightStatus(StrEnum):
    SUPPORTED = "supported"
    NOT_OBSERVED = "not_observed"
    UNCERTAIN = "uncertain"


class DistillationQualityStatus(StrEnum):
    COMPLETE = "complete"
    INCOMPLETE = "incomplete"
    FAILED = "failed"


class ContractModel(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class SourceCandidate(ContractModel):
    url: str
    title: str = "Untitled source"
    publisher: str = "Unknown publisher"
    published_at: datetime | None = None
    retrieved_at: datetime = Field(default_factory=utc_now)
    source_kind: str = "discovery"
    snippet: str = ""
    topics: list[str] = Field(default_factory=list)
    geographies: list[str] = Field(default_factory=list)
    lane: str = "unassigned"
    is_seed: bool = False
    evidence_status: EvidenceStatus = EvidenceStatus.UNVERIFIED
    region: str = "global"
    language_code: str = "und"
    language_confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    authority_tier: str = "unknown"
    catalog_source_id: str | None = None
    source_type: str = "unknown"
    freshness_status: FreshnessStatus = FreshnessStatus.UNKNOWN
    freshness_days: int | None = Field(default=None, ge=0)
    extraction_status: ExtractionStatus = ExtractionStatus.NOT_ATTEMPTED
    extraction_error_code: str | None = None
    normalized_title_en: str | None = None
    normalized_snippet_en: str | None = None

    @field_validator("url")
    @classmethod
    def validate_url(cls, value: str) -> str:
        if not value.startswith(("https://", "http://")):
            raise ValueError("source URL must use http or https")
        return value

    @field_validator("published_at", "retrieved_at")
    @classmethod
    def require_date_timezone(cls, value: datetime | None) -> datetime | None:
        if value is not None and value.tzinfo is None:
            raise ValueError("source timestamps must include a timezone")
        return value

    @field_validator("language_code")
    @classmethod
    def validate_language_code(cls, value: str) -> str:
        normalized = value.strip().lower()
        if normalized != "und" and (
            not normalized.isalpha() or len(normalized) not in {2, 3}
        ):
            raise ValueError("language_code must be ISO-639-1/2 or und")
        return normalized


class LaneDiscoveryPacket(ContractModel):
    source_urls: list[str] = Field(default_factory=list, max_length=25)
    selected_queries: list[str] = Field(default_factory=list, max_length=30)
    evidence_notes: list[str] = Field(default_factory=list, max_length=8)


class LaneDiscoveryResult(ContractModel):
    packet: LaneDiscoveryPacket
    sources: list[SourceCandidate] = Field(default_factory=list, max_length=25)
    content: dict[str, str] = Field(default_factory=dict)
    metadata: dict[str, object] = Field(default_factory=dict)


class ClaimDraft(ContractModel):
    claim: str = Field(min_length=1)
    source_urls: list[str] = Field(min_length=1)
    evidence_status: EvidenceStatus = EvidenceStatus.UNVERIFIED
    confidence: str = "low"
    support_locator: str | None = None
    conflicts: list[str] = Field(default_factory=list)
    original_claim: str | None = None
    evidence_excerpt: str | None = None
    independent_source_count: int = Field(default=0, ge=0)
    citation_status: str = "uncited"
    verification_basis: str | None = None

    @field_validator("evidence_excerpt")
    @classmethod
    def validate_evidence_excerpt(cls, value: str | None) -> str | None:
        if value is None:
            return None
        if len(value) > 320 or len(value.split()) > 40:
            raise ValueError("evidence_excerpt must be at most 320 characters and 40 words")
        return value


class ArticleInsight(ContractModel):
    status: InsightStatus
    statement: str = Field(min_length=1, max_length=600)
    why_it_matters: str = Field(min_length=1, max_length=600)
    next_step: str = Field(min_length=1, max_length=600)
    evidence_excerpt: str | None = Field(default=None, max_length=320)
    evidence_locator: str | None = Field(default=None, max_length=300)

    @field_validator("evidence_excerpt")
    @classmethod
    def validate_evidence_excerpt(cls, value: str | None) -> str | None:
        if value is not None and len(value.split()) > 40:
            raise ValueError("insight evidence_excerpt must be at most 40 words")
        return value

    @model_validator(mode="after")
    def require_supported_evidence(self) -> Self:
        if self.status is InsightStatus.SUPPORTED and not (
            self.evidence_excerpt or self.evidence_locator
        ):
            raise ValueError(
                "supported article insight requires an evidence excerpt or locator"
            )
        return self


class ArticleDistillation(ContractModel):
    source_url: str
    summary: str = Field(min_length=1)
    key_points: list[str] = Field(default_factory=list)
    entities: list[str] = Field(default_factory=list)
    signals: list[str] = Field(default_factory=list)
    claims: list[ClaimDraft] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)
    published_at: datetime | None = None
    model_id: str = "offline-fixture"
    prompt_version: str = "distill-v1"
    evidence_status: EvidenceStatus = EvidenceStatus.MIXED
    content_hash: str | None = None
    source_language: str = "und"
    summary_original: str = ""
    key_points_original: list[str] = Field(default_factory=list)
    translation_status: TranslationStatus = TranslationStatus.NOT_NEEDED
    evidence_excerpts: list[str] = Field(default_factory=list, max_length=8)
    evidence_locators: list[str] = Field(default_factory=list, max_length=8)
    # Legacy rows predate article insight packets. They remain readable as
    # incomplete evidence until a repair run creates a complete packet.
    what_happened: str = ""
    why_it_matters: str = ""
    risk_assessment: ArticleInsight | None = None
    opportunity_assessment: ArticleInsight | None = None
    uncertainties: list[str] = Field(default_factory=list, max_length=8)
    next_steps: list[str] = Field(default_factory=list, max_length=8)
    quality_status: DistillationQualityStatus = DistillationQualityStatus.INCOMPLETE
    quality_issues: list[str] = Field(default_factory=list, max_length=20)
    insight_packet: dict[str, object] = Field(default_factory=dict)

    @field_validator("source_language")
    @classmethod
    def validate_source_language(cls, value: str) -> str:
        normalized = value.strip().lower()
        if normalized != "und" and (not normalized.isalpha() or len(normalized) not in {2, 3}):
            raise ValueError("source_language must be ISO-639-1/2 or und")
        return normalized

    @model_validator(mode="after")
    def populate_insight_packet(self) -> Self:
        if not self.insight_packet:
            self.insight_packet = {
                "what_happened": self.what_happened,
                "why_it_matters": self.why_it_matters,
                "risk_assessment": (
                    self.risk_assessment.model_dump(mode="json")
                    if self.risk_assessment is not None
                    else None
                ),
                "opportunity_assessment": (
                    self.opportunity_assessment.model_dump(mode="json")
                    if self.opportunity_assessment is not None
                    else None
                ),
                "uncertainties": self.uncertainties,
                "next_steps": self.next_steps,
            }
        return self


class SignalEvent(ContractModel):
    event_id: str
    run_id: str
    event_type: str
    summary: str = Field(min_length=1)
    geographies: list[str] = Field(default_factory=list)
    ports: list[str] = Field(default_factory=list)
    carriers: list[str] = Field(default_factory=list)
    event_at: datetime | None = None
    source_urls: list[str] = Field(min_length=1)
    evidence_status: EvidenceStatus = EvidenceStatus.UNVERIFIED


class ReportBullet(ContractModel):
    text: str = Field(min_length=1, max_length=600)
    source_urls: list[str] = Field(min_length=1, max_length=8)
    evidence_status: EvidenceStatus = EvidenceStatus.MIXED
    why_it_matters: str | None = Field(default=None, min_length=1, max_length=600)
    next_step: str | None = Field(default=None, min_length=1, max_length=600)


class WeeklyBrief(ContractModel):
    run_id: str
    title: str = Field(min_length=1)
    covered_from: datetime
    covered_until: datetime
    summary: str = Field(min_length=1)
    signal_event_ids: list[str] = Field(default_factory=list)
    source_urls: list[str] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)
    review_state: ReviewState = ReviewState.DRAFT
    evidence_status: EvidenceStatus = EvidenceStatus.MIXED
    model_id: str = "offline-fixture"
    prompt_version: str = "weekly-brief-v1"
    content_hash: str | None = None
    executive_bullets: list[ReportBullet] = Field(default_factory=list)
    developments: list[ReportBullet] = Field(default_factory=list)
    risks: list[ReportBullet] = Field(default_factory=list)
    opportunities: list[ReportBullet] = Field(default_factory=list)
    uncertainties: list[ReportBullet] = Field(default_factory=list)
    follow_up_questions: list[str] = Field(default_factory=list, max_length=8)

    @model_validator(mode="after")
    def validate_period(self) -> Self:
        if self.covered_from > self.covered_until:
            raise ValueError("brief start must not be after brief end")
        return self


class RegionQueryPack(ContractModel):
    region: str
    countries: list[str] = Field(default_factory=list)
    ports: list[str] = Field(default_factory=list)
    signal_types: list[str] = Field(default_factory=list)
    query_families: list[str] = Field(min_length=1)
    language_hints: list[str] = Field(default_factory=list)
    required: bool = False
    freshness_days: int = Field(default=14, ge=1, le=365)
    authority_domains: list[str] = Field(default_factory=list)
    allow_open_discovery: bool = True


class TopicConfig(ContractModel):
    name: str
    description: str
    queries: list[str] = Field(min_length=1)
    seed_urls: list[str] = Field(default_factory=list)
    geographies: list[str] = Field(default_factory=list)
    include_domains: list[str] = Field(default_factory=list)
    exclude_domains: list[str] = Field(default_factory=list)
    lookback_days: int = Field(default=14, ge=1, le=365)
    region_packs: dict[str, RegionQueryPack] = Field(default_factory=dict)


class ResearchRunRequest(ContractModel):
    topic_set: str
    cadence: ResearchCadence = ResearchCadence.WEEKLY
    as_of: datetime = Field(default_factory=utc_now)
    since: datetime | None = None
    max_sources: int = Field(default=25, ge=1, le=100)
    model: str = STRICT_OPENROUTER_MODEL
    seed_urls: list[str] = Field(default_factory=list)
    include_topic_seeds: bool = True
    validation_profile: str = "full"
    review_state: ReviewState = ReviewState.DRAFT
    allow_external_actions: bool = False

    @field_validator("as_of", "since")
    @classmethod
    def require_timezone(cls, value: datetime | None) -> datetime | None:
        if value is not None and value.tzinfo is None:
            raise ValueError("timestamps must include a timezone")
        return value

    @field_validator("model")
    @classmethod
    def require_free_model(cls, value: str) -> str:
        if not is_free_model(value):
            raise ValueError(
                "model must be a valid OpenRouter :free model; "
                f"strict default is {STRICT_OPENROUTER_MODEL}"
            )
        return value

    @field_validator("validation_profile")
    @classmethod
    def require_known_validation_profile(cls, value: str) -> str:
        if value not in {"full", "canary", "global-canary"}:
            raise ValueError("validation_profile must be full, canary, or global-canary")
        return value

    @model_validator(mode="after")
    def validate_window(self) -> Self:
        if self.since is not None and self.since > self.as_of:
            raise ValueError("since must not be after as_of")
        if self.allow_external_actions:
            raise ValueError("external actions are disabled for research runs")
        return self


class RunResult(ContractModel):
    run_id: str
    status: RunStatus
    cadence: ResearchCadence = ResearchCadence.WEEKLY
    source_count: int = 0
    distillation_count: int = 0
    claim_count: int = 0
    brief_id: str | None = None
    error: str | None = None
    citation_coverage: float = 0.0
    validation_status: ValidationStatus = ValidationStatus.BLOCKED
    lane_statuses: dict[str, str] = Field(default_factory=dict)


class ValidationCheck(ContractModel):
    name: str
    status: ValidationStatus
    observed: str | int | float | bool | None = None
    expected: str | int | float | bool | None = None
    message: str = ""


class ValidationReport(ContractModel):
    run_id: str
    status: ValidationStatus
    source_count: int = 0
    unique_source_count: int = 0
    claim_count: int = 0
    cited_claim_count: int = 0
    citation_coverage: float = 0.0
    lane_coverage: list[str] = Field(default_factory=list)
    checks: list[ValidationCheck] = Field(default_factory=list)
    model_id: str = "unknown"
    prompt_version: str = "validation-v1"
    as_of: datetime | None = None
    content_hash: str | None = None
