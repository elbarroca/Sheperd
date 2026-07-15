import type { Metadata } from "next";
import { KnowledgeMap } from "@/components/knowledge-map";
import { PageHeader } from "@/components/page-header";
import { ResearchSearch } from "@/components/research-search";
import { SourceLibrary } from "@/components/source-library";
import { getKnowledgeCatalog, getKnowledgeFile, getKnowledgeSummary } from "@/lib/knowledge";

export const metadata: Metadata = { title: "Evidence library" };

export default function ResearchPage() {
  const summary = getKnowledgeSummary();
  const files = getKnowledgeCatalog();
  const initialFile = files[0] ? getKnowledgeFile(files[0].path) : null;
  if (!initialFile) throw new Error("The admitted knowledge corpus is empty.");

  return (
    <>
      <PageHeader
        eyebrow="Evidence library"
        title="Every file, chart, and conclusion stays traceable."
        description="Browse all committed context, open full indexed sections, and search across the research without turning Ricardo's notes into company fact."
        meta={<><span>Retrieval method</span><strong>Local TF-IDF sparse v1</strong><small>No external model calls</small></>}
      />
      <dl className="corpus-strip" aria-label="Knowledge corpus summary">
        <div><dt>Source files</dt><dd>{summary.sourceFiles}</dd></div>
        <div><dt>Section chunks</dt><dd>{summary.chunks}</dd></div>
        <div><dt>Vault folders</dt><dd>{summary.folders}</dd></div>
        <div><dt>External calls</dt><dd>0</dd></div>
      </dl>
      <KnowledgeMap stats={summary.layerStats} />
      <SourceLibrary files={files} initialFile={initialFile} />
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
