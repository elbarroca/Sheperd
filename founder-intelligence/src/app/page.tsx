import { Distribution } from "@/components/distribution";
import { EvidenceTide } from "@/components/evidence-tide";
import { PageHeader } from "@/components/page-header";
import { ScoreGrid } from "@/components/score-grid";
import { phases } from "@/lib/content";
import { getOverviewData } from "@/lib/data";

export default function FounderBriefPage() {
  const overview = getOverviewData();
  return (
    <>
      <PageHeader
        eyebrow="Founder brief · decision view"
        title="What can we responsibly decide now?"
        description="The research and GTM system are strong. Market proof and execution authority are not. This view keeps those truths separate."
        meta={<><span>Source date</span><strong>{overview.sourceDate}</strong></>}
      />

      <section className="decision-ribbon" aria-label="Next highest-value decision">
        <div>
          <span className="ribbon-index">NEXT / 01</span>
          <div><p>Founder truth-and-gates workshop</p><span>Admit or reject GAP-001–012 and record one external-activation GO or NO-GO.</span></div>
        </div>
        <strong>HOLD</strong>
      </section>

      <ScoreGrid scores={overview.scores} />
      <EvidenceTide counts={overview.sourceStates} />

      <section className="section-block">
        <div className="section-heading">
          <div><p className="eyebrow">Source plan versus admitted plan</p><h2>Ambition remains. Certainty is corrected.</h2></div>
          <p>Avi’s learner → builder → leader arc is preserved; every phase now has an evidence gate.</p>
        </div>
        <div className="phase-route">
          {phases.map((phase, index) => (
            <article key={phase.period} className="phase-card">
              <div className="phase-marker"><span>{String(index + 1).padStart(2, "0")}</span></div>
              <p className="metric-id">{phase.period}</p>
              <h3>{phase.admittedLabel}</h3>
              <p>{phase.detail}</p>
              <div className="source-translation"><span>Source</span><strong>{phase.sourceLabel}</strong></div>
              <span className={`state-pill state-${phase.state}`}>{phase.state.replaceAll("-", " ")}</span>
            </article>
          ))}
        </div>
      </section>

      <section className="chart-grid section-block">
        <Distribution eyebrow="Execution register" title="Experiment states" counts={overview.experimentStates} />
        <Distribution eyebrow="Workflow atlas" title="Coverage states" counts={overview.workflowStates} />
        <Distribution eyebrow="AI register" title="Human-control classes" counts={overview.aiClasses} />
      </section>

      <section className="section-block">
        <div className="section-heading">
          <div><p className="eyebrow">Activation manifest</p><h2>Twelve blockers. None silently promoted.</h2></div>
          <p>Every gate has a decision question, owner, and next evidence action.</p>
        </div>
        <div className="blocker-grid">
          {overview.blockers.map((blocker) => (
            <article key={blocker.blocker_id} className="blocker-card">
              <div className="blocker-head"><code>{blocker.blocker_id}</code><span>{blocker.gate}</span></div>
              <h3>{blocker.decision_question}</h3>
              <dl><div><dt>Owner</dt><dd>{blocker.owner}</dd></div><div><dt>Next</dt><dd>{blocker.next_action}</dd></div></dl>
            </article>
          ))}
        </div>
      </section>

      <section className="layer-contract section-block" aria-labelledby="layer-title">
        <div><p className="eyebrow">Interpretation contract</p><h2 id="layer-title">One dashboard. Three visible layers.</h2></div>
        <article><span className="layer-number">F</span><h3>Fact</h3><p>Source, evidence state, confidence, date, and limitation.</p></article>
        <article><span className="layer-number">R</span><h3>Ricardo</h3><p>Interpretation and recommendation—never presented as company truth.</p></article>
        <article><span className="layer-number">D</span><h3>Decision</h3><p>Named approver, scope, date, consequence, and revisit condition.</p></article>
      </section>
    </>
  );
}
