import type { Metadata } from "next";
import { ArrowSquareOutIcon } from "@phosphor-icons/react/dist/ssr/ArrowSquareOut";
import { CompetitorPositioning } from "@/components/competitor-positioning";
import { PageHeader } from "@/components/page-header";
import { SourceLink } from "@/components/source-link";
import { competitorProfiles, COMPETITOR_SOURCE_PATH } from "@/lib/focused-content";

export const metadata: Metadata = { title: "Competitors" };

const categoryOrder = ["recovery", "audit", "enterprise"] as const;
const categoryGuidance = {
  recovery: "Closest buyer expectation. Compare case quality, speed, and realized net outcomes first.",
  audit: "Broader workflow alternatives. SheperD must win on D&D depth, not platform breadth.",
  enterprise: "System-of-record incumbents. Integrate with them rather than claim replacement.",
} satisfies Record<(typeof categoryOrder)[number], string>;

export default function CompetitorsPage() {
  return (
    <div className="focused-page">
      <PageHeader
        eyebrow="Competitors"
        title="SheperD enters a crowded category."
        description="Recovery specialists own the narrow job. Enterprise audit platforms own the broader workflow. SheperD still needs to prove that its evidence-to-decision wedge is better for a defined customer cohort."
        meta={<><span>Observed field</span><strong>14 providers</strong><small>Public positioning only</small></>}
      />

      <section className="focus-section position-section" aria-labelledby="position-title">
        <div className="focus-heading">
          <div><h2 id="position-title">Narrow expertise, with a traceable operating layer</h2></div>
          <p>The intended position sits between specialist recovery and broader audit tooling. That is a hypothesis until comparable customer evidence exists.</p>
        </div>
        <div className="position-layout">
          <CompetitorPositioning />
          <aside className="position-conclusion">
            <span>Positioning decision</span>
            <h3>Do not lead with generic AI or recovery.</h3>
            <p>Lead with faster evidence completeness, explicit negative decisions, owner visibility, and an auditable path from invoice to cash or credit.</p>
            <SourceLink path={COMPETITOR_SOURCE_PATH} />
          </aside>
        </div>
      </section>

      <section className="focus-section" aria-labelledby="field-title">
        <div className="focus-heading">
          <div><h2 id="field-title">What buyers can choose today</h2></div>
          <p>Prices and outcomes are captured as displayed public signals. They are not independently verified.</p>
        </div>
        <div className="competitor-groups">
          {categoryOrder.map((category) => {
            const profiles = competitorProfiles.filter((profile) => profile.category === category);
            return (
              <details key={category} className="competitor-group" open={category === "recovery"}>
                <summary>
                  <span><strong id={`category-${category}`}>{profiles[0]?.categoryLabel}</strong><small>{categoryGuidance[category]}</small></span>
                  <span>{profiles.length}</span>
                </summary>
                <div className="competitor-list">
                  {profiles.map((profile) => (
                    <article key={profile.id} className="competitor-row">
                      <div>
                        <h4>{profile.name}</h4>
                        <a href={profile.url} target="_blank" rel="noreferrer">Visit company <ArrowSquareOutIcon size={15} aria-hidden="true" /></a>
                      </div>
                      <p>{profile.offer}</p>
                      <p><strong>Pricing signal</strong>{profile.pricingSignal}</p>
                      <p className="competitor-boundary"><strong>Boundary</strong>{profile.evidenceBoundary}</p>
                    </article>
                  ))}
                </div>
              </details>
            );
          })}
        </div>
      </section>

      <section className="focus-section proof-section" aria-labelledby="proof-title">
        <div className="focus-heading">
          <div><h2 id="proof-title">The moat is evidence, not the category label</h2></div>
        </div>
        <ol className="proof-list">
          <li><strong>Case quality</strong><span>More complete evidence with fewer reviewer corrections.</span></li>
          <li><strong>Decision speed</strong><span>Less time from invoice intake to submit, stop, or escalate.</span></li>
          <li><strong>Net outcome</strong><span>Realized cash, credit, or waiver after fee and customer work.</span></li>
          <li><strong>Control</strong><span>Clear provenance, owners, approvals, access, and retention.</span></li>
        </ol>
      </section>
    </div>
  );
}
