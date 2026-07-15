"use client";

import { type FormEvent, useState } from "react";
import type { SearchResult } from "@/lib/types";
import { LayerBadge } from "./layer-badge";

const suggestedQueries = [
  "What blocks external activation?",
  "What does Michael own?",
  "Which claims remain unverified?",
  "What does the 16-week plan overstate?",
];

export function ResearchSearch() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<SearchResult[]>([]);
  const [status, setStatus] = useState("Ask across the admitted D0/D1 research corpus.");
  const [loading, setLoading] = useState(false);

  async function runSearch(nextQuery: string): Promise<void> {
    const normalized = nextQuery.trim();
    if (normalized.length < 2) {
      setStatus("Enter at least two characters.");
      return;
    }
    setLoading(true);
    setStatus("Searching the local vector index…");
    try {
      const response = await fetch(`/api/search?q=${encodeURIComponent(normalized)}`);
      const payload = (await response.json()) as { error?: string; results?: SearchResult[] };
      if (!response.ok || !payload.results) throw new Error(payload.error ?? "Search failed.");
      setResults(payload.results);
      setStatus(`${payload.results.length} sourced sections ranked by lexical similarity.`);
    } catch (error) {
      setResults([]);
      setStatus(error instanceof Error ? error.message : "Search failed safely.");
    } finally {
      setLoading(false);
    }
  }

  function submit(event: FormEvent<HTMLFormElement>): void {
    event.preventDefault();
    void runSearch(query);
  }

  return (
    <section className="search-workbench" aria-labelledby="search-title">
      <div className="search-intro">
        <p className="eyebrow">Local vector retrieval</p>
        <h2 id="search-title">Trace the answer, not just the summary.</h2>
        <p>Results retain their original path, section, layer, and evidence status. Similarity never upgrades evidence.</p>
      </div>
      <form className="search-form" onSubmit={submit}>
        <label htmlFor="research-query">Search the SheperD intelligence corpus</label>
        <div className="search-control">
          <input
            id="research-query"
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            minLength={2}
            maxLength={160}
            placeholder="e.g. What must be true before outreach?"
          />
          <button type="submit" disabled={loading}>{loading ? "Searching" : "Trace answer"}</button>
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
      <div className="search-results">
        {results.map((result) => (
          <article key={result.id} className="search-result">
            <div className="result-meta">
              <LayerBadge layer={result.layer} />
              <span>{result.evidenceStatus.replaceAll("-", " ")}</span>
              <span>{Math.round(result.score * 100)}% match</span>
            </div>
            <h3>{result.title}</h3>
            <p className="result-section">{result.section}</p>
            <p>{result.text}</p>
            <code>{result.path}</code>
          </article>
        ))}
      </div>
    </section>
  );
}
