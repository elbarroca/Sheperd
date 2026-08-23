import type { Metadata } from "next";
import { UnavailableState } from "@/components/report-accordion";
import {
  getResearchSourceExplorer,
  getResearchSourceFacets,
  type ArticleInsight,
  type ResearchClaim,
  type SourceExplorerItem,
  type SourceFacets,
} from "@/lib/research-api";

export const metadata: Metadata = { title: "Sources" };

const PAGE_SIZE = 24;
type FilterKey = "query" | "lane" | "geography" | "evidence" | "region" | "language" | "freshness" | "authority_tier" | "source_type";
type SearchParams = Partial<Record<FilterKey | "page", string>>;

function dateLabel(value: string | null): string {
  return value
    ? new Intl.DateTimeFormat("en", { dateStyle: "medium" }).format(new Date(value))
    : "Undated";
}

function safeUrl(value: string): boolean {
  return value.startsWith("https://") || value.startsWith("http://");
}

function statusClass(value: string | undefined): string {
  return (value ?? "unknown").replaceAll(/[^a-zA-Z0-9_-]/gu, "-");
}

function statusLabel(value: string | undefined): string {
  return value
    ? value.replaceAll("_", " ").replace(/^\w/u, (letter) => letter.toUpperCase())
    : "Unavailable";
}

function Status({ label, value }: { label: string; value: string | undefined }) {
  return <span className={`status-badge status-${statusClass(value)}`}>{label}: {statusLabel(value)}</span>;
}

function CitationLinks({ urls }: { urls: string[] }) {
  return urls.filter(safeUrl).map((url, index) => (
    <a key={`${url}-${index}`} href={url} target="_blank" rel="noreferrer" className="citation-link">
      Citation {index + 1}
    </a>
  ));
}

function Insight({ label, value }: { label: string; value?: ArticleInsight | null }) {
  if (!value) return <div><strong>{label}</strong><p className="muted">Not recorded in this run.</p></div>;
  return (
    <div>
      <div className="bullet-meta"><strong>{label}</strong><Status label="Status" value={value.status} /></div>
      <p>{value.statement}</p>
      <p><strong>Why it matters:</strong> {value.why_it_matters}</p>
      <p><strong>Next step:</strong> {value.next_step}</p>
      {value.evidence_excerpt ? <small>Evidence: {value.evidence_excerpt}</small> : null}
      {value.evidence_locator ? <small>Locator: {value.evidence_locator}</small> : null}
    </div>
  );
}

function ClaimList({ claims }: { claims: ResearchClaim[] }) {
  if (claims.length === 0) return <p className="muted">No claims recorded.</p>;
  return (
    <ul className="source-list">
      {claims.map((claim, index) => (
        <li key={`${claim.claim}-${index}`}>
          <span>{claim.claim}</span>
          <span className="bullet-meta">
            <span className={`evidence-badge evidence-${claim.evidence_status}`}>{claim.evidence_status}</span>
            <span>{claim.citation_status ?? "uncited"}</span>
            <CitationLinks urls={claim.source_urls} />
          </span>
          {claim.evidence_excerpt ? <small>Evidence: {claim.evidence_excerpt}</small> : null}
          {claim.support_locator ? <small>Locator: {claim.support_locator}</small> : null}
        </li>
      ))}
    </ul>
  );
}

function SourceCard({ item }: { item: SourceExplorerItem }) {
  const { source, distillation, claims } = item;
  const mergedClaims = distillation?.claims.length ? distillation.claims : claims;
  const snippet = source.normalized_snippet_en?.trim() || source.snippet.trim();
  return (
    <article className="source-row">
      <div className="source-card-heading">
        <div>
          <p className="eyebrow">{source.region ?? "global"} / {source.language_code ?? "und"} / {source.lane}</p>
          <h2><a href={source.url} target="_blank" rel="noreferrer">{source.title}</a></h2>
          {source.normalized_title_en && source.normalized_title_en !== source.title ? <p className="source-normalized-title">English title: {source.normalized_title_en}</p> : null}
          <p className="muted">{source.publisher || "Unknown publisher"} / {source.authority_tier ?? "unknown authority"} / {source.source_type ?? "unknown type"}</p>
        </div>
        <Status label="Evidence" value={source.evidence_status} />
      </div>
      <p className="card-meta">Published {dateLabel(source.published_at)} / Retrieved {dateLabel(source.retrieved_at)}</p>
      <div className="status-row">
        <Status label="Freshness" value={source.freshness_status} />
        <Status label="Extraction" value={source.extraction_status} />
        <Status label="Translation" value={distillation?.translation_status} />
      </div>
      <p className="source-snippet">Snippet: {snippet || "Not recorded in this run."}</p>
      {source.normalized_snippet_en && source.normalized_snippet_en !== source.snippet ? <p className="muted">Original: {source.snippet}</p> : null}
      {source.extraction_error_code ? <p className="muted">Extraction error: {source.extraction_error_code}</p> : null}
      {item.fulfillment ? <p className="muted">Fulfillment: {item.fulfillment.status} · {item.fulfillment.claim_count} claims · {item.fulfillment.citation_count} cited · UI {item.fulfillment.ui_displayable ? "ready" : "not ready"}{item.fulfillment.missing_fields.length ? ` · missing ${item.fulfillment.missing_fields.join(", ")}` : ""}</p> : <p className="muted">Fulfillment: legacy, not recorded in this run.</p>}
      <details className="report-section">
        <summary>Article findings</summary>
        <div className="report-section-body">
          {distillation ? (
            <>
              <h3>Research summary</h3>
              <p>{distillation.summary?.trim() || "Not recorded in this run."}</p>
              <h3>Original-language summary</h3>
              <p className="muted">{distillation.summary_original?.trim() || "Not recorded in this run."}</p>
              <h3>Key points</h3>
              {distillation.key_points.length > 0 ? <ul>{distillation.key_points.map((point) => <li key={point}>{point}</li>)}</ul> : <p className="muted">Not recorded in this run.</p>}
              {distillation.key_points_original?.length ? <><h3>Original key points</h3><ul>{distillation.key_points_original.map((point) => <li key={point}>{point}</li>)}</ul></> : null}
              <h3>What happened</h3>
              <p>{distillation.what_happened?.trim() || "Not recorded in this run."}</p>
              <h3>Why it matters</h3>
              <p>{distillation.why_it_matters?.trim() || "Not recorded in this run."}</p>
              <div className="insight-grid">
                <Insight label="Risk assessment" value={distillation.risk_assessment} />
                <Insight label="Opportunity assessment" value={distillation.opportunity_assessment} />
              </div>
              <h3>Next steps</h3>
              {distillation.next_steps?.length ? <ul>{distillation.next_steps.map((step) => <li key={step}>{step}</li>)}</ul> : <p className="muted">Not recorded in this run.</p>}
              <h3>Uncertainty</h3>
              {distillation.uncertainties?.length ? <ul>{distillation.uncertainties.map((item) => <li key={item}>{item}</li>)}</ul> : <p className="muted">Not recorded in this run.</p>}
              {distillation.signals.length > 0 ? <><h3>Signals</h3><ul>{distillation.signals.map((signal) => <li key={signal}>{signal}</li>)}</ul></> : null}
              <p className="muted">Model {distillation.model_id} / evidence {distillation.evidence_status} / translation {distillation.translation_status ?? "unknown"} / quality {distillation.quality_status ?? "incomplete"}</p>
              {distillation.quality_issues?.length ? <p className="muted">Quality issues: {distillation.quality_issues.join(", ")}</p> : null}
              {distillation.limitations.length > 0 ? <p className="muted">Limitations: {distillation.limitations.join("; ")}</p> : null}
            </>
          ) : <p className="muted">No distillation persisted for this source.</p>}
        </div>
      </details>
      <details className="report-section">
        <summary>Claims and evidence ({mergedClaims.length})</summary>
        <div className="report-section-body">
          <ClaimList claims={mergedClaims} />
          {distillation?.evidence_excerpts?.length ? <p>Excerpts: {distillation.evidence_excerpts.join(" / ")}</p> : <p className="muted">Evidence excerpts: Not recorded in this run.</p>}
          {distillation?.evidence_locators?.length ? <p>Locators: {distillation.evidence_locators.join(" / ")}</p> : <p className="muted">Evidence locators: Not recorded in this run.</p>}
        </div>
      </details>
      <p className="hash-line">Content hash: <code>{item.source_hash ?? "not recorded"}</code></p>
      <a href={source.url} target="_blank" rel="noreferrer">Open canonical source</a>
    </article>
  );
}

function SelectFilter({
  name,
  label,
  value,
  options,
}: {
  name: string;
  label: string;
  value?: string;
  options: string[];
}) {
  return (
    <label>
      <span>{label}</span>
      <select name={name} defaultValue={value ?? ""}>
        <option value="">All</option>
        {options.map((option) => <option value={option} key={option}>{option}</option>)}
      </select>
    </label>
  );
}

function pageHref(filters: SearchParams, page: number): string {
  const params = new URLSearchParams();
  for (const [key, value] of Object.entries(filters)) {
    if (key !== "page" && value) params.set(key, value);
  }
  params.set("page", String(page));
  return `/sources?${params.toString()}`;
}

export default async function SourcesPage({
  searchParams,
}: {
  searchParams: Promise<SearchParams>;
}) {
  const filters = await searchParams;
  const page = Number.parseInt(filters.page ?? "1", 10) || 1;
  const [sourcesResponse, facetsResponse] = await Promise.all([
    getResearchSourceExplorer({ ...filters, page, page_size: PAGE_SIZE }),
    getResearchSourceFacets(),
  ]);
  if (sourcesResponse.status === "unavailable") return <UnavailableState error={sourcesResponse.error} />;
  if (facetsResponse.status === "unavailable") return <UnavailableState error={facetsResponse.error} />;
  const facets: SourceFacets = facetsResponse.data;
  const pageData = sourcesResponse.data;

  return (
    <div className="page-stack">
      <div className="page-intro">
        <p className="eyebrow">Evidence explorer</p>
        <h1>Every persisted source, in context.</h1>
        <p>Neon is canonical. Cards retain failed, partial, undated, and seed records so quality boundaries remain visible.</p>
      </div>
      <form className="source-filter-form" method="get">
        <label className="filter-search"><span>Search</span><input name="query" defaultValue={filters.query} placeholder="Title, publisher, or indexed text" maxLength={160} /></label>
        <SelectFilter name="region" label="Region" value={filters.region} options={facets.regions} />
        <SelectFilter name="language" label="Language" value={filters.language} options={facets.languages} />
        <SelectFilter name="freshness" label="Freshness" value={filters.freshness} options={facets.freshness} />
        <SelectFilter name="authority_tier" label="Authority" value={filters.authority_tier} options={facets.authority} />
        <SelectFilter name="source_type" label="Type" value={filters.source_type} options={facets.source_types} />
        <SelectFilter name="lane" label="Lane" value={filters.lane} options={facets.lanes} />
        <SelectFilter name="evidence" label="Evidence" value={filters.evidence} options={facets.evidence_states} />
        <button type="submit">Apply filters</button>
      </form>
      <div className="explorer-toolbar">
        <p>{pageData.total} persisted sources / page {pageData.page} / {PAGE_SIZE} per page</p>
        <div className="pagination" aria-label="Source pages">
          {pageData.page > 1 ? <a href={pageHref(filters, pageData.page - 1)}>Previous</a> : <span className="muted">Previous</span>}
          {pageData.has_more ? <a href={pageHref(filters, pageData.page + 1)}>Next</a> : <span className="muted">Next</span>}
        </div>
      </div>
      <section className="source-listing" aria-label="Persisted research sources">
        {pageData.items.length > 0 ? pageData.items.map((item) => <SourceCard key={item.source.url} item={item} />) : <div className="empty-state"><h2>No sources matched</h2><p>Run an agent check or research run, then reload.</p></div>}
      </section>
    </div>
  );
}
