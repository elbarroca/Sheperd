import type { Metadata } from "next";
import { UnavailableState } from "@/components/report-accordion";
import {
  getResearchDistillations,
  getResearchClaims,
  getResearchSources,
  type ArticleDistillation,
  type ResearchClaim,
  type ResearchSource,
} from "@/lib/research-api";

export const metadata: Metadata = { title: "Sources" };

function dateLabel(value: string | null): string {
  return value ? new Intl.DateTimeFormat("en", { dateStyle: "medium" }).format(new Date(value)) : "Unknown date";
}

function CitationLinks({ urls }: { urls: string[] }) {
  return urls.filter((url) => url.startsWith("https://") || url.startsWith("http://")).map((url) => (
    <a key={url} href={url} target="_blank" rel="noreferrer" className="citation-link">Citation</a>
  ));
}

function Distillation({ value, claims }: { value: ArticleDistillation | undefined; claims: ResearchClaim[] }) {
  if (!value) return <p className="muted">No distillation persisted for this source.</p>;
  const persistedClaims = value.claims.length > 0 ? value.claims : claims;
  return (
    <div className="source-distillation">
      <p>{value.summary}</p>
      {value.summary_original && value.summary_original !== value.summary ? <p className="muted">Original-language summary: {value.summary_original}</p> : null}
      {value.key_points.length > 0 ? <ul>{value.key_points.map((point) => <li key={point}>{point}</li>)}</ul> : null}
      <p className="muted">Model: {value.model_id} / Prompt: {value.prompt_version} / Evidence: {value.evidence_status} / Language: {value.source_language ?? "und"} / Translation: {value.translation_status ?? "unknown"}</p>
      {value.signals.length > 0 ? <p>Signals: {value.signals.join("; ")}</p> : null}
      {persistedClaims.length > 0 ? <ul>{persistedClaims.map((claim) => <li key={claim.claim}>{claim.claim} <span className={`evidence-badge evidence-${claim.evidence_status}`}>{claim.evidence_status}</span> <CitationLinks urls={claim.source_urls} /></li>)}</ul> : null}
      {value.evidence_excerpts?.length ? <p>Evidence excerpts: {value.evidence_excerpts.join(" / ")}</p> : null}
      <p className="muted">Distillation hash: {value.content_hash ?? "none recorded"}</p>
      {value.limitations.length > 0 ? <p className="muted">Limitations: {value.limitations.join("; ")}</p> : null}
    </div>
  );
}

function SourceCard({ source, distillation, claims }: { source: ResearchSource; distillation: ArticleDistillation | undefined; claims: ResearchClaim[] }) {
  return (
    <article className="source-card">
      <div className="source-card-heading">
        <div>
          <p className="eyebrow">{source.region ?? "global"} / {source.language_code ?? "und"} / {source.lane} / {source.evidence_status}</p>
          <h2><a href={source.url} target="_blank" rel="noreferrer">{source.title}</a></h2>
          <p className="muted">{source.publisher} / {source.authority_tier ?? "unknown authority"} / {source.source_type ?? "unknown type"} / Published {dateLabel(source.published_at)} / Retrieved {dateLabel(source.retrieved_at)}</p>
        </div>
        <span className={`status-badge status-${source.extraction_status === "succeeded" ? "pass" : "blocked"}`}>{source.extraction_status ?? "unknown"}</span>
      </div>
      <details className="report-section" open>
        <summary>Distillation</summary>
        <div className="report-section-body"><Distillation value={distillation} claims={claims} /></div>
      </details>
      <p className="source-snippet">{source.normalized_snippet_en ?? source.snippet}</p>
      {source.normalized_snippet_en && source.normalized_snippet_en !== source.snippet ? <p className="muted">Original: {source.snippet}</p> : null}
      <a href={source.url} target="_blank" rel="noreferrer">Open canonical source</a>
    </article>
  );
}

export default async function SourcesPage({
  searchParams,
}: {
  searchParams: Promise<{
    query?: string;
    lane?: string;
    geography?: string;
    evidence?: string;
    region?: string;
    language?: string;
    freshness?: string;
    authority_tier?: string;
    source_type?: string;
  }>;
}) {
  const filters = await searchParams;
  const [sourcesResponse, distillationsResponse, claimsResponse] = await Promise.all([
    getResearchSources(filters),
    getResearchDistillations(),
    getResearchClaims(),
  ]);
  if (sourcesResponse.status === "unavailable") return <UnavailableState error={sourcesResponse.error} />;
  if (distillationsResponse.status === "unavailable") return <UnavailableState error={distillationsResponse.error} />;
  if (claimsResponse.status === "unavailable") return <UnavailableState error={claimsResponse.error} />;
  const distillations = new Map(distillationsResponse.data.distillations.map((item) => [item.source_url, item]));
  const claimsBySource = new Map<string, ResearchClaim[]>();
  for (const claim of claimsResponse.data.claims) {
    for (const url of claim.source_urls) {
      claimsBySource.set(url, [...(claimsBySource.get(url) ?? []), claim]);
    }
  }
  return (
    <div className="page-stack">
      <div className="page-intro">
        <p className="eyebrow">Evidence explorer</p>
        <h1>Sources and distillations.</h1>
        <p>Every card is read from Neon. Search and filters narrow persisted source metadata; no browser credential or stale fallback is used.</p>
      </div>
      <form className="source-filter-form" method="get">
        <input name="query" defaultValue={filters.query} placeholder="Search title, publisher, or summary" maxLength={160} />
        <input name="lane" defaultValue={filters.lane} placeholder="Lane e.g. mexico" maxLength={80} />
        <input name="geography" defaultValue={filters.geography} placeholder="Geography" maxLength={80} />
        <input name="evidence" defaultValue={filters.evidence} placeholder="Evidence state" maxLength={40} />
        <input name="region" defaultValue={filters.region} placeholder="Region e.g. Europe" maxLength={40} />
        <input name="language" defaultValue={filters.language} placeholder="Language e.g. es" maxLength={12} />
        <input name="freshness" defaultValue={filters.freshness} placeholder="Freshness" maxLength={20} />
        <input name="authority_tier" defaultValue={filters.authority_tier} placeholder="Authority tier" maxLength={24} />
        <input name="source_type" defaultValue={filters.source_type} placeholder="Source type" maxLength={32} />
        <button type="submit">Filter</button>
      </form>
      <section className="source-grid" aria-label="Persisted research sources">
        {sourcesResponse.data.sources.length > 0 ? sourcesResponse.data.sources.map((source) => (
          <SourceCard key={source.url} source={source} distillation={distillations.get(source.url)} claims={claimsBySource.get(source.url) ?? []} />
        )) : <div className="empty-state"><h2>No sources matched</h2><p>Run an agent check or research run, then reload.</p></div>}
      </section>
    </div>
  );
}
