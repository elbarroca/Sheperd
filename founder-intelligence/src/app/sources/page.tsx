import type { Metadata } from "next";
import { UnavailableState } from "@/components/report-accordion";
import {
  getResearchSourceExplorer,
  getResearchSourceFacets,
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

function Status({ label, value }: { label: string; value: string | undefined }) {
  return <span className={`status-badge status-${value ?? "unknown"}`}>{label}: {value ?? "unknown"}</span>;
}

function CitationLinks({ urls }: { urls: string[] }) {
  return urls.filter(safeUrl).map((url, index) => (
    <a key={`${url}-${index}`} href={url} target="_blank" rel="noreferrer" className="citation-link">
      Citation {index + 1}
    </a>
  ));
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
  return (
    <article className="source-card">
      <div className="source-card-heading">
        <div>
          <p className="eyebrow">{source.region ?? "global"} · {source.language_code ?? "und"} · {source.lane}</p>
          <h2><a href={source.url} target="_blank" rel="noreferrer">{source.title}</a></h2>
          <p className="muted">{source.publisher || "Unknown publisher"} · {source.authority_tier ?? "unknown authority"} · {source.source_type ?? "unknown type"}</p>
        </div>
        <Status label="Evidence" value={source.evidence_status} />
      </div>
      <p className="card-meta">Published {dateLabel(source.published_at)} · Retrieved {dateLabel(source.retrieved_at)}</p>
      <div className="status-row">
        <Status label="Freshness" value={source.freshness_status} />
        <Status label="Extraction" value={source.extraction_status} />
        <Status label="Translation" value={distillation?.translation_status} />
      </div>
      <p className="source-snippet">{source.normalized_snippet_en ?? source.snippet ?? "No summary snippet recorded."}</p>
      {source.normalized_snippet_en && source.normalized_snippet_en !== source.snippet ? <p className="muted">Original: {source.snippet}</p> : null}
      <details className="report-section">
        <summary>Article findings</summary>
        <div className="report-section-body">
          {distillation ? (
            <>
              <h3>English summary</h3>
              <p>{distillation.summary}</p>
              <h3>Original-language summary</h3>
              <p className="muted">{distillation.summary_original || "Not recorded."}</p>
              <h3>Key points</h3>
              {distillation.key_points.length > 0 ? <ul>{distillation.key_points.map((point) => <li key={point}>{point}</li>)}</ul> : <p className="muted">None recorded.</p>}
              {distillation.key_points_original?.length ? <><h3>Original key points</h3><ul>{distillation.key_points_original.map((point) => <li key={point}>{point}</li>)}</ul></> : null}
              <p className="muted">Model {distillation.model_id} · evidence {distillation.evidence_status} · translation {distillation.translation_status ?? "unknown"}</p>
              {distillation.limitations.length > 0 ? <p className="muted">Limitations: {distillation.limitations.join("; ")}</p> : null}
            </>
          ) : <p className="muted">No distillation persisted for this source.</p>}
        </div>
      </details>
      <details className="report-section">
        <summary>Claims and evidence ({mergedClaims.length})</summary>
        <div className="report-section-body">
          <ClaimList claims={mergedClaims} />
          {distillation?.evidence_excerpts?.length ? <p>Excerpts: {distillation.evidence_excerpts.join(" / ")}</p> : null}
          {distillation?.evidence_locators?.length ? <p>Locators: {distillation.evidence_locators.join(" / ")}</p> : null}
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
        <p>{pageData.total} persisted sources · page {pageData.page}</p>
        <div className="pagination">
          {pageData.page > 1 ? <a href={pageHref(filters, pageData.page - 1)}>Previous</a> : <span className="muted">Previous</span>}
          {pageData.has_more ? <a href={pageHref(filters, pageData.page + 1)}>Next</a> : <span className="muted">Next</span>}
        </div>
      </div>
      <section className="source-grid" aria-label="Persisted research sources">
        {pageData.items.length > 0 ? pageData.items.map((item) => <SourceCard key={item.source.url} item={item} />) : <div className="empty-state"><h2>No sources matched</h2><p>Run an agent check or research run, then reload.</p></div>}
      </section>
    </div>
  );
}
