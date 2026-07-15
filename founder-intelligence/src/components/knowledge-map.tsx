import type { KnowledgeLayer, KnowledgeLayerStat } from "@/lib/types";

const layerDescriptions: Record<KnowledgeLayer, string> = {
  "founder-context": "Founder vision, role, and relationship context",
  "operating-system": "GTM, product, AI, and execution playbooks",
  research: "Dossiers, workflow evidence, and research synthesis",
  "ricardo-interpretation": "Ricardo's recommendations and consequences",
  source: "Original captures and source material",
  "structured-data": "Decision, blocker, workflow, and measurement tables",
  template: "Reusable operating and interview structures",
};

function labelLayer(layer: KnowledgeLayer): string {
  return layer.replaceAll("-", " ");
}

export function KnowledgeMap({ stats }: { stats: KnowledgeLayerStat[] }) {
  const layerMemberships = stats.reduce((sum, stat) => sum + stat.files, 0);
  const totalSections = stats.reduce((sum, stat) => sum + stat.chunks, 0);

  return (
    <section className="knowledge-map section-block" aria-labelledby="knowledge-map-title">
      <div className="section-heading">
        <div><p className="eyebrow">Knowledge map</p><h2 id="knowledge-map-title">Seven layers keep context from collapsing into certainty</h2></div>
        <p>Files can participate in more than one layer. Section counts show where the corpus carries the most depth.</p>
      </div>
      <div className="knowledge-map-grid">
        <div className="knowledge-map-anchor">
          <span>Indexed intelligence</span>
          <strong>{totalSections}</strong>
          <p>traceable sections across {stats.length} knowledge layers</p>
          <small>{layerMemberships} file-to-layer memberships</small>
        </div>
        <ol>
          {stats.map((stat, index) => (
            <li key={stat.layer}>
              <span>{String(index + 1).padStart(2, "0")}</span>
              <div><h3>{labelLayer(stat.layer)}</h3><p>{layerDescriptions[stat.layer]}</p></div>
              <dl><div><dt>Files</dt><dd>{stat.files}</dd></div><div><dt>Sections</dt><dd>{stat.chunks}</dd></div></dl>
            </li>
          ))}
        </ol>
      </div>
    </section>
  );
}
