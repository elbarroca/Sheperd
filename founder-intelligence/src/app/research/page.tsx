import type { Metadata } from "next";
import { PageHeader } from "@/components/page-header";
import { ResearchSearch } from "@/components/research-search";
import { getKnowledgeSummary } from "@/lib/knowledge";

export const metadata: Metadata = { title: "Research" };

export default function ResearchPage() {
  const summary = getKnowledgeSummary();
  return (
    <>
      <PageHeader
        eyebrow="Research intelligence · traceable retrieval"
        title="Ask the work. Inspect the source."
        description="A committed local vector index condenses the admitted research without sending internal text to an embedding provider."
        meta={<><span>Method</span><strong>TF-IDF sparse v1</strong></>}
      />
      <section className="corpus-strip" aria-label="Knowledge corpus summary">
        <div><strong>{summary.sourceFiles}</strong><span>source files</span></div>
        <div><strong>{summary.chunks}</strong><span>section chunks</span></div>
        <div><strong>{summary.vocabulary}</strong><span>vector terms</span></div>
        <div><strong>0</strong><span>external calls</span></div>
      </section>
      <ResearchSearch />
      <section className="method-note section-block">
        <p className="eyebrow">Retrieval boundary</p>
        <h2>Useful, reproducible, and deliberately limited.</h2>
        <p>{summary.boundary}. This is lexical similarity—not an answer generator, legal interpretation, or evidence promotion mechanism.</p>
        <div className="layer-counts">
          {Object.entries(summary.layerCounts).sort((left, right) => right[1] - left[1]).map(([layer, count]) => (
            <span key={layer}><strong>{count}</strong>{layer.replaceAll("-", " ")}</span>
          ))}
        </div>
      </section>
    </>
  );
}
