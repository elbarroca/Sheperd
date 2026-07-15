import type { Metadata } from "next";
import { PageHeader } from "@/components/page-header";
import { operatingAxes, phases } from "@/lib/content";

export const metadata: Metadata = { title: "Mikey workflow" };

export default function MikeyPage() {
  return (
    <>
      <PageHeader
        eyebrow="Mikey workflow · learner → builder → operating lead"
        title="Build the commercial system. Do not absorb every authority."
        description="Michael’s mandate is GTM and Revenue Operations: structure market learning, CRM discipline, founder knowledge, and commercial decisions."
        meta={<><span>Recommended role</span><strong>GTM & Revenue Operations Lead</strong></>}
      />
      <section className="responsibility-grid">
        <article className="responsibility-card owns"><p className="eyebrow">Michael owns</p><h2>Commercial learning system</h2><ul><li>Account and partner segmentation</li><li>Controlled cohort operations</li><li>CRM architecture and hygiene</li><li>Discovery and objection capture</li><li>Website/content requirements</li><li>Weekly GTM decision cadence</li></ul></article>
        <article className="responsibility-card boundaries"><p className="eyebrow">Requires specialist approval</p><h2>Material authority</h2><ul><li>Regulatory and eligibility meaning</li><li>Product-analysis conclusions</li><li>Pricing and contracts</li><li>Customer-data acceptance</li><li>Public claims and case studies</li><li>Hiring, funding, or scale claims</li></ul></article>
      </section>
      <section className="section-block">
        <div className="section-heading"><div><p className="eyebrow">Eight-axis operating model</p><h2>The source says seven. The work contains eight.</h2></div><p>Live execution is a separate risk-bearing axis; it cannot be hidden inside preparation.</p></div>
        <div className="axis-grid">
          {operatingAxes.map((axis, index) => <article key={axis}><span>{String(index + 1).padStart(2, "0")}</span><h3>{axis}</h3><div className={`axis-state ${index === 7 ? "gated" : "internal"}`}>{index === 7 ? "Approval gated" : "Prepare internally"}</div></article>)}
        </div>
      </section>
      <section className="section-block">
        <div className="section-heading"><div><p className="eyebrow">16-week correction</p><h2>Three phases. Four explicit gates.</h2></div></div>
        <div className="timeline-table" role="table" aria-label="Mikey 16-week operating phases">
          {phases.map((phase) => <div key={phase.period} className="timeline-row" role="row"><span role="cell">{phase.period}</span><strong role="cell">{phase.admittedLabel}</strong><p role="cell">{phase.detail}</p><em role="cell">{phase.state.replaceAll("-", " ")}</em></div>)}
        </div>
      </section>
      <section className="decision-ribbon compact-ribbon"><div><span className="ribbon-index">SAFE START</span><div><p>Week 0 is not optional.</p><span>Written engagement, authority, systems, confidentiality, IP, data rules, and success definitions precede representation.</span></div></div><strong>GATE</strong></section>
    </>
  );
}
