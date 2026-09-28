from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from typing import Literal, Self

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from .settings import (
    DEFAULT_OPENAI_MODEL,
    STRICT_OPENROUTER_MODEL,
    is_free_openrouter_model,
    is_openai_model,
)


def utc_now() -> datetime:
    return datetime.now(UTC)


def is_free_model(model: str) -> bool:
    return is_openai_model(model) or is_free_openrouter_model(model)


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


class RunKind(StrEnum):
    RESEARCH = "research"
    REPAIR = "repair"


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


class PeriodStatus(StrEnum):
    IN_PERIOD = "in_period"
    BACKGROUND = "background"
    UNDATED = "undated"
    FUTURE = "future"
    EXCLUDED = "excluded"


class PeriodBasis(StrEnum):
    PUBLISHED_AT = "published_at"
    EVENT_AT = "event_at"
    RETRIEVED_AT = "retrieved_at"
    RUN_AS_OF = "run_as_of"
    UNKNOWN = "unknown"


class PageType(StrEnum):
    ARTICLE = "article"
    OFFICIAL_DOCUMENT = "official_document"
    ARCHIVE = "archive"
    INDEX = "index"
    CATEGORY = "category"
    LANDING = "landing"
    UNKNOWN = "unknown"


class PublicationDateBasis(StrEnum):
    MATCHED = "matched"
    PAGE = "page"
    SEARCH = "search"
    CONFLICT = "conflict"
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


class DecisionScore(ContractModel):
    sheperd_relevance: int = Field(ge=0, le=30)
    operational_impact: int = Field(ge=0, le=25)
    actionability: int = Field(ge=0, le=20)
    recency: int = Field(ge=0, le=15)
    source_authority: int = Field(ge=0, le=10)
    total: int = Field(ge=0, le=100)
    priority: str = "watch"
    rationale: dict[str, str] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_total(self) -> Self:
        expected = (
            self.sheperd_relevance
            + self.operational_impact
            + self.actionability
            + self.recency
            + self.source_authority
        )
        if self.total != expected:
            raise ValueError("decision score total must equal the sum of its components")
        self.priority = "high" if self.total >= 75 else "medium" if self.total >= 50 else "watch"
        return self


class ReaderArticle(ContractModel):
    source_url: str
    headline: str
    publisher: str
    published_at: datetime | None = None
    event_at: datetime | None = None
    date_basis: PublicationDateBasis = PublicationDateBasis.UNKNOWN
    date_locator: str | None = None
    retrieved_at: datetime
    page_type: PageType
    score: DecisionScore | None = None
    key_points: list[str] = Field(default_factory=list, max_length=3)
    what_changed: str
    why_sheperd_cares: str
    recommended_action: str
    risk: str | None = None
    opportunity: str | None = None
    limitations: list[str] = Field(default_factory=list, max_length=8)
    lane: str
    region: str
    eligible_for_weekly: bool
    validation_status: str


class ReaderSourceIndexEntry(ContractModel):
    url: str
    title: str
    publisher: str
    published_at: datetime | None = None
    date_basis: PublicationDateBasis = PublicationDateBasis.UNKNOWN
    page_type: PageType = PageType.UNKNOWN
    eligible_for_weekly: bool = False
    validation_status: str


class ReaderReport(ContractModel):
    run_id: str
    title: str
    covered_from: datetime
    covered_until: datetime
    report_status: str
    validation_status: str
    readiness_status: str
    canonical_hash: str
    three_things: list[str] = Field(default_factory=list, max_length=3)
    top_action: str
    ranked_articles: list[ReaderArticle] = Field(default_factory=list, max_length=8)
    watchlist: list[ReaderArticle] = Field(default_factory=list)
    background_articles: list[ReaderArticle] = Field(default_factory=list)
    source_index: list[ReaderSourceIndexEntry] = Field(default_factory=list)


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
    period_status: PeriodStatus = PeriodStatus.UNDATED
    period_basis: PeriodBasis = PeriodBasis.UNKNOWN
    eligible_for_weekly: bool = False
    page_type: PageType = PageType.UNKNOWN
    direct_content: bool = False
    search_published_at: datetime | None = None
    page_published_at: datetime | None = None
    publication_date_basis: PublicationDateBasis = PublicationDateBasis.UNKNOWN
    publication_date_locator: str | None = Field(default=None, max_length=300)
    parent_navigation_url: str | None = None

    @field_validator("url")
    @classmethod
    def validate_url(cls, value: str) -> str:
        if not value.startswith(("https://", "http://")):
            raise ValueError("source URL must use http or https")
        return value

    @field_validator(
        "published_at",
        "retrieved_at",
        "search_published_at",
        "page_published_at",
    )
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
    headline: str = ""
    event_type: str = "other"
    event_at: datetime | None = None
    event_at_locator: str | None = None
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
    decision_score: DecisionScore | None = None
    insight_packet: dict[str, object] = Field(default_factory=dict)

    @field_validator("source_language")
    @classmethod
    def validate_source_language(cls, value: str) -> str:
        normalized = value.strip().lower()
        if normalized != "und" and (not normalized.isalpha() or len(normalized) not in {2, 3}):
            raise ValueError("source_language must be ISO-639-1/2 or und")
        return normalized

    @field_validator("published_at", "event_at")
    @classmethod
    def require_date_timezone(cls, value: datetime | None) -> datetime | None:
        if value is not None and value.tzinfo is None:
            raise ValueError("distillation timestamps must include a timezone")
        return value

    @model_validator(mode="after")
    def populate_insight_packet(self) -> Self:
        if not self.insight_packet:
            self.insight_packet = {
                "headline": self.headline,
                "event_type": self.event_type,
                "event_at": self.event_at.isoformat() if self.event_at else None,
                "event_at_locator": self.event_at_locator,
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
                "decision_score": (
                    self.decision_score.model_dump(mode="json")
                    if self.decision_score is not None
                    else None
                ),
            }
        return self


class SignalEvent(ContractModel):
    event_id: str
    run_id: str
    event_type: str
    summary: str = Field(min_length=1)
    headline: str = ""
    what_changed: str = ""
    geographies: list[str] = Field(default_factory=list)
    ports: list[str] = Field(default_factory=list)
    carriers: list[str] = Field(default_factory=list)
    event_at: datetime | None = None
    published_at: datetime | None = None
    retrieved_at: datetime | None = None
    period_status: PeriodStatus | None = None
    period_basis: PeriodBasis | None = None
    eligible_for_weekly: bool = False
    region: str = ""
    lane: str = ""
    source_urls: list[str] = Field(min_length=1)
    evidence_locator: str | None = None
    impact: str = ""
    risk: str = ""
    opportunity: str = ""
    next_step: str = ""
    limitations: list[str] = Field(default_factory=list, max_length=8)
    evidence_status: EvidenceStatus = EvidenceStatus.UNVERIFIED

    @field_validator("event_at", "published_at", "retrieved_at")
    @classmethod
    def require_date_timezone(cls, value: datetime | None) -> datetime | None:
        if value is not None and value.tzinfo is None:
            raise ValueError("signal event timestamps must include a timezone")
        return value


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
    research_scope: Literal["global", "us-mexico"] = "global"
    new_findings_only: bool = False
    cadence: ResearchCadence = ResearchCadence.WEEKLY
    as_of: datetime = Field(default_factory=utc_now)
    since: datetime | None = None
    max_sources: int = Field(default=25, ge=1, le=100)
    model: str = DEFAULT_OPENAI_MODEL
    seed_urls: list[str] = Field(default_factory=list)
    include_topic_seeds: bool = True
    validation_profile: str = "full"
    context_version: str = Field(default="legacy-unknown", min_length=1)
    research_timezone: str = Field(default="Europe/Lisbon", min_length=1)
    run_kind: RunKind = RunKind.RESEARCH
    parent_run_id: str | None = Field(default=None, min_length=1)
    repair_round: int | None = Field(default=None, ge=1, le=3)
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
                "model must be a valid OpenAI model identifier or legacy OpenRouter :free model; "
                f"legacy default is {STRICT_OPENROUTER_MODEL}"
            )
        return value

    @field_validator("validation_profile")
    @classmethod
    def require_known_validation_profile(cls, value: str) -> str:
        if value not in {"full", "canary", "global-canary", "repair"}:
            raise ValueError(
                "validation_profile must be full, canary, global-canary, or repair"
            )
        return value

    @model_validator(mode="after")
    def validate_window(self) -> Self:
        if self.since is not None and self.since > self.as_of:
            raise ValueError("since must not be after as_of")
        if self.allow_external_actions:
            raise ValueError("external actions are disabled for research runs")
        if self.run_kind is RunKind.REPAIR:
            if self.parent_run_id is None:
                raise ValueError("repair runs require parent_run_id")
            if self.repair_round is None:
                raise ValueError("repair runs require repair_round")
            if self.validation_profile != "repair":
                raise ValueError("repair runs require the repair validation profile")
        elif self.parent_run_id is not None or self.repair_round is not None:
            raise ValueError("research runs cannot declare repair lineage")
        elif self.validation_profile == "repair":
            raise ValueError("the repair validation profile requires a repair run")
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
    error_code: str | None = None
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
    blocking_reasons: list[str] = Field(default_factory=list)
