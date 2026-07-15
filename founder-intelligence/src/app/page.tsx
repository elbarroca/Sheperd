import Link from "next/link";
import { DecisionFlow } from "@/components/decision-flow";
import { EvidenceTide } from "@/components/evidence-tide";
import { ExecutiveReadout } from "@/components/executive-readout";
import { IntelligenceCharts } from "@/components/intelligence-charts";
import { PageHeader } from "@/components/page-header";
import { ResearchSynthesis } from "@/components/research-synthesis";
import { ScoreGrid } from "@/components/score-grid";
import { DirectionalArrow } from "@/components/ui-icons";
import { phases } from "@/lib/content";
import { getOverviewData } from "@/lib/data";
import { getKnowledgeSummary } from "@/lib/knowledge";

export default function FounderBriefPage() {
  const overview = getOverviewData();
  const knowledge = getKnowledgeSummary();
  const internallyAllowed = Object.entries(overview.experimentStates)
    .filter(([state]) => state === "prepare-now" || state === "synthetic-only")
    .reduce((sum, [, count]) => sum + count, 0);
  const verifiedSources = overview.sourceStates.verified ?? 0;

  return (
    <>
      <PageHeader
        eyebrow="Private founder brief"
        title="Prepared to learn. Not cleared to scale."
        description="The research system and GTM design are strong. Market proof, authority, and safe execution are not. This brief shows what founders must decide and what Michael can prepare now."
        actions={<><Link className="primary-action" href="/research">Explore all sources <DirectionalArrow /></Link><Link className="secondary-action" href="/improvements">Review open gates</Link></>}
        meta={<><span>Current posture</span><strong>Hold external activation</strong><small>Evidence snapshot {overview.sourceDate}</small></>}
      />

      <section className="decision-snapshot" aria-labelledby="decision-snapshot-title">
        <div className="posture-block">
          <span>Current posture</span>
          <strong id="decision-snapshot-title">Hold external activation</strong>
          <p>Twelve authority, evidence, safety, and capacity gates remain unresolved.</p>
        </div>
        <dl className="decision-facts">
          <div><dt>Open gates</dt><dd>{overview.counts.blockers}</dd></div>
          <div><dt>Internal tests</dt><dd>{internallyAllowed}</dd></div>
          <div><dt>External tests</dt><dd>0</dd></div>
          <div><dt>Verified sources</dt><dd>{verifiedSources}/{overview.counts.sources}</dd></div>
        </dl>
        <div className="next-decision">
          <span>Next founder decision</span>
          <h2>Run the truth and gates workshop</h2>
          <p>Admit, reject, or keep incomplete every gate. Record one external activation go or no-go.</p>
          <Link href="/improvements">Open the decision map <span aria-hidden="true">→</span></Link>
        </div>
      </section>

      <ExecutiveReadout scores={overview.scores} />

      <ResearchSynthesis />

      <DecisionFlow />

      <section className="section-block" aria-labelledby="score-heading">
        <div className="section-heading">
          <div><p className="eyebrow">Planning signal</p><h2 id="score-heading">Separate system quality from market proof</h2></div>
          <p>Strong preparation does not cancel weak external evidence.</p>
        </div>
        <ScoreGrid scores={overview.scores} />
      </section>

      <IntelligenceCharts scores={overview.scores} layerStats={knowledge.layerStats} sourceStates={overview.sourceStates} />

      <section className="source-portal section-block" aria-labelledby="source-portal-title">
        <div className="source-portal-copy">
          <p className="eyebrow">Research control room</p>
          <h2 id="source-portal-title">From every file to the founder consequence</h2>
          <p>Browse the full corpus, read every indexed section, filter by layer, and search across the evidence without sending company context to an external service.</p>
          <Link href="/research">Open the evidence library <DirectionalArrow /></Link>
        </div>
        <dl className="source-portal-metrics">
          <div><dt>Source files</dt><dd>{knowledge.sourceFiles}</dd></div>
          <div><dt>Indexed sections</dt><dd>{knowledge.chunks}</dd></div>
          <div><dt>Vault folders</dt><dd>{knowledge.folders}</dd></div>
          <div><dt>External retrieval calls</dt><dd>0</dd></div>
        </dl>
      </section>

      <EvidenceTide counts={overview.sourceStates} />

      <section className="section-block" aria-labelledby="timeline-title">
        <div className="section-heading">
          <div><p className="eyebrow">Gated operating path</p><h2 id="timeline-title">The sixteen-week plan advances only with evidence</h2></div>
          <p>Time does not open the next phase. An explicit decision does.</p>
        </div>
        <ol className="gated-timeline">
          {phases.map((phase, index) => (
            <li key={phase.period}>
              <span className="timeline-index">{String(index + 1).padStart(2, "0")}</span>
              <div><span>{phase.period}</span><h3>{phase.admittedLabel}</h3><p>{phase.detail}</p></div>
              <strong className={`state-pill state-${phase.state}`}>{phase.state.replaceAll("-", " ")}</strong>
            </li>
          ))}
        </ol>
      </section>

      <section className="layer-contract section-block" aria-labelledby="layer-title">
        <div><p className="eyebrow">Interpretation contract</p><h2 id="layer-title">Three layers stay visibly separate</h2></div>
        <article><span className="layer-number">F</span><h3>Fact</h3><p>Source, evidence state, confidence, date, and limitation.</p></article>
        <article><span className="layer-number">R</span><h3>Ricardo</h3><p>Interpretation and recommendation, never company truth.</p></article>
        <article><span className="layer-number">D</span><h3>Decision</h3><p>Named approver, scope, date, consequence, and revisit condition.</p></article>
      </section>
    </>
  );
}
