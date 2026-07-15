import type { Metadata } from "next";
import { PageHeader } from "@/components/page-header";
import { PriorityLab } from "@/components/priority-lab";
import { improvementBacklog } from "@/lib/content";
import { getExperiments } from "@/lib/data";

export const metadata: Metadata = { title: "Priority lab" };

export default function ImprovementsPage() {
  const experiments = getExperiments();
  return (
    <>
      <PageHeader
        eyebrow="Priority lab · transparent planning"
        title="Optimize the sequence—not the story."
        description="Change visible planning weights and inspect the order. A high score cannot override authority, evidence, security, capacity, or human approval."
        meta={<><span>Execution allowlist</span><strong>EXP-001–003 only</strong></>}
      />
      <PriorityLab experiments={experiments} />
      <section className="section-block">
        <div className="section-heading"><div><p className="eyebrow">Improvement backlog</p><h2>What raises decision quality next.</h2></div><p>These are operating recommendations, not expected-value forecasts.</p></div>
        <div className="improvement-table" role="table" aria-label="Improvement backlog">
          <div className="improvement-row table-head" role="row"><span>Area</span><span>Improvement</span><span>Gate</span><span>State</span></div>
          {improvementBacklog.map((item) => <div key={item.id} className="improvement-row" role="row"><span><code>{item.id}</code>{item.area}</span><strong>{item.title}</strong><span>{item.gate}</span><em>{item.state.replaceAll("-", " ")}</em></div>)}
        </div>
      </section>
    </>
  );
}
