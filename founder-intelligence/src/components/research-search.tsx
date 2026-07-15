"use client";

import { type FormEvent, useEffect, useRef, useState } from "react";
import Link from "next/link";
import type { KnowledgeLayer, SearchResult } from "@/lib/types";
import { researchFileHref } from "@/lib/content";
import { LayerBadge } from "./layer-badge";

const suggestedQueries = [
  "What blocks external activation?",
  "What evidence is missing for TAM?",
  "What does Michael own?",
  "Which competitor category owns recovery?",
];

interface SearchPayload {
  error?: string;
  results?: SearchResult[];
}

const knowledgeLayers = new Set<KnowledgeLayer>([
  "founder-context",
  "operating-system",
  "research",
  "ricardo-interpretation",
  "source",
  "structured-data",
  "template",
]);

function isSearchResult(value: unknown): value is SearchResult {
  if (typeof value !== "object" || value === null) return false;
  const candidate = value as Record<string, unknown>;

  return typeof candidate.id === "string"
    && typeof candidate.path === "string"
    && typeof candidate.title === "string"
    && typeof candidate.section === "string"
    && typeof candidate.layer === "string"
    && knowledgeLayers.has(candidate.layer as KnowledgeLayer)
    && typeof candidate.evidenceStatus === "string"
    && typeof candidate.text === "string"
    && typeof candidate.score === "number"
    && Number.isFinite(candidate.score);
}

function isSearchPayload(value: unknown): value is SearchPayload {
  if (typeof value !== "object" || value === null) return false;
  const candidate = value as Record<string, unknown>;

  return (candidate.error === undefined || typeof candidate.error === "string")
    && (candidate.results === undefined
      || (Array.isArray(candidate.results) && candidate.results.every(isSearchResult)));
}

export function ResearchSearch() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<SearchResult[]>([]);
  const [status, setStatus] = useState("Search returns sourced passages from the admitted corpus.");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [hasSearched, setHasSearched] = useState(false);
  const requestRef = useRef<AbortController | null>(null);

  useEffect(() => () => {
    requestRef.current?.abort();
    requestRef.current = null;
  }, []);

  async function runSearch(nextQuery: string): Promise<void> {
    const normalized = nextQuery.trim();
    if (normalized.length < 2) {
      setError("Enter at least two characters.");
      return;
    }

    requestRef.current?.abort();
    const controller = new AbortController();
    requestRef.current = controller;
    setLoading(true);
    setError(null);
    setHasSearched(true);
    setStatus("Searching the admitted evidence index.");

    try {
      const response = await fetch(`/api/search?q=${encodeURIComponent(normalized)}`, { signal: controller.signal });
      const rawPayload: unknown = await response.json();
      if (!isSearchPayload(rawPayload)) throw new Error("The search response was malformed.");
      if (!response.ok || !rawPayload.results) throw new Error(rawPayload.error ?? "Search failed.");
      setResults(rawPayload.results);
      setStatus(rawPayload.results.length === 0
        ? "No sourced sections matched this question."
        : `${rawPayload.results.length} sourced passages found. Open the document to validate the full context.`);
    } catch (caughtError) {
      if (caughtError instanceof DOMException && caughtError.name === "AbortError") return;
      setResults([]);
      setError(caughtError instanceof Error ? caughtError.message : "Search failed safely.");
      setStatus("Search unavailable.");
    } finally {
      if (requestRef.current === controller) {
        requestRef.current = null;
        setLoading(false);
      }
    }
  }

  function submit(event: FormEvent<HTMLFormElement>): void {
    event.preventDefault();
    void runSearch(query);
  }

  return (
    <section className="focus-section corpus-search" aria-labelledby="search-title" aria-busy={loading}>
      <div className="search-intro">
        <h2 id="search-title">Find the evidence behind a decision</h2>
        <p>Search finds relevant passages. It never upgrades an evidence state or turns a passage into a company claim.</p>
      </div>
      <form className="search-form" onSubmit={submit}>
        <label htmlFor="research-query">What do you want to verify?</label>
        <div className="search-control">
          <input
            id="research-query"
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            minLength={2}
            maxLength={160}
            placeholder="For example, what must be true before outreach?"
          />
          <button type="submit" disabled={loading}>{loading ? "Searching" : "Search"}</button>
        </div>
        <div className="query-chips" aria-label="Suggested questions">
          {suggestedQueries.map((suggestion) => (
            <button key={suggestion} type="button" onClick={() => { setQuery(suggestion); void runSearch(suggestion); }}>
              {suggestion}
            </button>
          ))}
        </div>
      </form>
      <p className="search-status" role="status">{status}</p>
      {error ? <p className="search-error" role="alert">{error}</p> : null}
      {loading ? <div className="loading-state" role="status"><span aria-hidden="true" />Reading the local index</div> : null}
      {!loading && hasSearched && !error && results.length === 0 ? (
        <div className="empty-state"><strong>No matching evidence found</strong><span>Try a broader founder, product, authority, or activation question.</span></div>
      ) : null}
      <div className="search-results">
        {results.map((result) => (
          <article key={result.id} className="search-result">
            <div className="result-meta">
              <LayerBadge layer={result.layer} />
              <span>{result.evidenceStatus.replaceAll("-", " ")}</span>
            </div>
            <h3>{result.title}</h3>
            <p className="result-section">{result.section}</p>
            <p className="result-excerpt">{result.text}</p>
            <Link className="result-source-link" href={researchFileHref(result.path)}>Read full document</Link>
          </article>
        ))}
      </div>
    </section>
  );
}
