import type { Metadata } from "next";
import { PageHeader } from "@/components/page-header";
import { ResearchSearch } from "@/components/research-search";
import { getKnowledgeSummary } from "@/lib/knowledge";

export const metadata: Metadata = { title: "Evidence" };

export default function ResearchPage() {
  const summary = getKnowledgeSummary();

  return (
    <>
      <PageHeader
        eyebrow="Evidence"
        title="Ask the work. Inspect the source."
        description="Search the committed research corpus locally, then verify the original section, evidence state, and interpretation layer."
        meta={<><span>Retrieval method</span><strong>Local TF-IDF sparse v1</strong></>}
      />
      <dl className="corpus-strip" aria-label="Knowledge corpus summary">
        <div><dt>Source files</dt><dd>{summary.sourceFiles}</dd></div>
        <div><dt>Section chunks</dt><dd>{summary.chunks}</dd></div>
        <div><dt>Vector terms</dt><dd>{summary.vocabulary}</dd></div>
        <div><dt>External calls</dt><dd>0</dd></div>
      </dl>
      <ResearchSearch />
      <section className="method-note section-block" aria-labelledby="method-title">
        <p className="eyebrow">Retrieval boundary</p>
        <h2 id="method-title">Reproducible and deliberately limited</h2>
        <p>{summary.boundary}. This is lexical similarity, not an answer generator, legal interpretation, or evidence promotion mechanism.</p>
        <details>
          <summary>Inspect corpus layers</summary>
          <div className="layer-counts">
            {Object.entries(summary.layerCounts).sort((left, right) => right[1] - left[1]).map(([layer, count]) => (
              <span key={layer}><strong>{count}</strong>{layer.replaceAll("-", " ")}</span>
            ))}
          </div>
        </details>
      </section>
    </>
  );
}
