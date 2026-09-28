import type { Metadata } from "next";
import { UnavailableState } from "@/components/report-accordion";
import { getMonthlyRollups, getResearchSourceFacets, type SourceFacets } from "@/lib/research-api";

export const metadata: Metadata = { title: "Monthly rollups" };

type SearchParams = { region?: string; language?: string; evidence?: string };

function SelectFilter({ name, label, value, options }: { name: keyof SearchParams; label: string; value?: string; options: string[] }) {
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

export default async function MonthlyPage({ searchParams }: { searchParams?: Promise<SearchParams> } = {}) {
  const filters = await (searchParams ?? Promise.resolve({} as SearchParams));
  const [response, facetsResponse] = await Promise.all([
    getMonthlyRollups(filters),
    getResearchSourceFacets(),
  ]);
  if (response.status === "unavailable") return <UnavailableState error={response.error} />;
  const facets: SourceFacets | null = facetsResponse?.status === "ok" ? facetsResponse.data : null;
  return (
    <div className="page-stack">
      <div className="page-intro">
        <p className="eyebrow">Deterministic aggregation</p>
        <h1>Monthly signal rollups.</h1>
        <p>Counts come directly from persisted signal events. No second LLM synthesis is used here.</p>
      </div>
      <form className="rollup-filter-form" method="get">
        <SelectFilter name="region" label="Region" value={filters.region} options={facets?.regions ?? []} />
        <SelectFilter name="language" label="Language" value={filters.language} options={facets?.languages ?? []} />
        <SelectFilter name="evidence" label="Evidence" value={filters.evidence} options={facets?.evidence_states ?? []} />
        <button type="submit">Apply filters</button>
      </form>
      {facetsResponse?.status === "unavailable" ? <p className="inline-note">Filter facets unavailable; showing unfiltered rollups.</p> : null}
      <div className="rollup-table">
        {response.data.rollups.length > 0 ? response.data.rollups.map((rollup, index) => (
          <article className="rollup-row" key={`${rollup.month}-${rollup.signal ?? "all"}-${rollup.region ?? "global"}-${index}`}>
            <div className="rollup-primary">
              <strong>{rollup.month}</strong>
              <span>{rollup.date ?? "Date not recorded"}</span>
            </div>
            <div className="rollup-stat"><strong>{rollup.signals}</strong><span>signals</span></div>
            <div className="rollup-stat"><strong>{rollup.runs}</strong><span>runs</span></div>
            <div className="rollup-stat"><strong>{rollup.signal ?? "All signals"}</strong><span>signal type</span></div>
            <dl className="rollup-meta">
              <div><dt>Region</dt><dd>{rollup.region ?? "Not recorded"}</dd></div>
              <div><dt>Language</dt><dd>{rollup.language ?? "Not recorded"}</dd></div>
              <div><dt>Lane</dt><dd>{rollup.lane ?? "Not recorded"}</dd></div>
              <div><dt>Geography</dt><dd>{rollup.geographies.join(", ") || "Not recorded"}</dd></div>
              <div><dt>Authority</dt><dd>{rollup.authority ?? "Not recorded"}</dd></div>
              <div><dt>Evidence</dt><dd>{rollup.evidence ?? "Not recorded"}</dd></div>
            </dl>
          </article>
        )) : <p className="empty-state">No persisted signal events yet.</p>}
      </div>
    </div>
  );
}
