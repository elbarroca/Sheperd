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
      {value.key_points.length > 0 ? <ul>{value.key_points.map((point) => <li key={point}>{point}</li>)}</ul> : null}
      <p className="muted">Model: {value.model_id} · Prompt: {value.prompt_version} · Evidence: {value.evidence_status}</p>
      {value.signals.length > 0 ? <p>Signals: {value.signals.join("; ")}</p> : null}
      {persistedClaims.length > 0 ? <ul>{persistedClaims.map((claim) => <li key={claim.claim}>{claim.claim} <span className={`evidence-badge evidence-${claim.evidence_status}`}>{claim.evidence_status}</span> <CitationLinks urls={claim.source_urls} /></li>)}</ul> : null}
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
          <p className="eyebrow">{source.lane} · {source.evidence_status}</p>
          <h2><a href={source.url} target="_blank" rel="noreferrer">{source.title}</a></h2>
          <p className="muted">{source.publisher} · Published {dateLabel(source.published_at)} · Retrieved {dateLabel(source.retrieved_at)}</p>
        </div>
        <span className="status-badge status-pass">Extracted</span>
      </div>
      <details className="report-section" open>
        <summary>Distillation</summary>
        <div className="report-section-body"><Distillation value={distillation} claims={claims} /></div>
      </details>
      <p className="source-snippet">{source.snippet}</p>
      <a href={source.url} target="_blank" rel="noreferrer">Open canonical source →</a>
    </article>
  );
}

export default async function SourcesPage({
  searchParams,
}: {
  searchParams: Promise<{ query?: string; lane?: string; geography?: string; evidence?: string }>;
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
