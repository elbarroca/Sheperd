import type { Metadata } from "next";
import { OwnershipMap } from "@/components/ownership-map";
import { PageHeader } from "@/components/page-header";
import { operatingAxes, phases } from "@/lib/content";

export const metadata: Metadata = { title: "Operating plan" };

export default function MikeyPage() {
  return (
    <>
      <PageHeader
        eyebrow="Operating plan"
        title="Michael builds the commercial system."
        description="His mandate is GTM and Revenue Operations: structure market learning, CRM discipline, founder knowledge, and commercial decisions without absorbing specialist authority."
        meta={<><span>Recommended role</span><strong>GTM and Revenue Operations Lead</strong></>}
      />

      <OwnershipMap />

      <section className="responsibility-grid section-block" aria-label="Michael responsibility boundary">
        <article className="responsibility-card owns">
          <p className="eyebrow">Michael owns</p>
          <h2>Commercial learning system</h2>
          <ul><li>Account and partner segmentation</li><li>Controlled cohort operations</li><li>CRM architecture and hygiene</li><li>Discovery and objection capture</li><li>Website and content requirements</li><li>Weekly GTM decision cadence</li></ul>
        </article>
        <article className="responsibility-card boundaries">
          <p className="eyebrow">Specialist approval</p>
          <h2>Material authority</h2>
          <ul><li>Regulatory and eligibility meaning</li><li>Product-analysis conclusions</li><li>Pricing and contracts</li><li>Customer-data acceptance</li><li>Public claims and case studies</li><li>Hiring, funding, or scale claims</li></ul>
        </article>
      </section>

      <section className="section-block" aria-labelledby="axes-title">
        <div className="section-heading">
          <div><p className="eyebrow">Eight-axis operating model</p><h2 id="axes-title">Preparation and live execution stay separate</h2></div>
          <p>Live execution is a distinct risk-bearing axis and needs its own approval.</p>
        </div>
        <ol className="axis-grid">
          {operatingAxes.map((axis, index) => (
            <li key={axis}>
              <span>{String(index + 1).padStart(2, "0")}</span>
              <h3>{axis}</h3>
              <strong className={`axis-state ${index === 7 ? "gated" : "internal"}`}>{index === 7 ? "Approval gated" : "Prepare internally"}</strong>
            </li>
          ))}
        </ol>
      </section>

      <section className="section-block" aria-labelledby="mikey-timeline-title">
        <div className="section-heading">
          <div><p className="eyebrow">Sixteen-week correction</p><h2 id="mikey-timeline-title">Three phases, each opened by a decision</h2></div>
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

      <aside className="safe-start-note">
        <span>Safe start</span>
        <div><h2>Week 0 is not optional</h2><p>Written engagement, authority, systems, confidentiality, IP, data rules, and success definitions precede representation.</p></div>
        <strong>Gate</strong>
      </aside>
    </>
  );
}
