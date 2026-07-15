import type { Metadata } from "next";
import { BlockerMap } from "@/components/blocker-map";
import { PageHeader } from "@/components/page-header";
import { PriorityLab } from "@/components/priority-lab";
import { improvementBacklog } from "@/lib/content";
import { getBlockers, getExperiments } from "@/lib/data";

export const metadata: Metadata = { title: "Decision map" };

export default function ImprovementsPage() {
  const experiments = getExperiments();
  const blockers = getBlockers();

  return (
    <>
      <PageHeader
        eyebrow="Decision map"
        title="Resolve dependencies before tuning priorities."
        description="The founder team first clears authority, product truth, claims, security, capacity, and publication gates. Weighted planning starts only inside that boundary."
        meta={<><span>External activation</span><strong>On hold</strong></>}
      />
      <BlockerMap blockers={blockers} />
      <PriorityLab experiments={experiments} />
      <section className="section-block" aria-labelledby="backlog-title">
        <div className="section-heading">
          <div><p className="eyebrow">Improvement backlog</p><h2 id="backlog-title">Six moves raise decision quality next</h2></div>
          <p>These are operating recommendations, not expected-value forecasts.</p>
        </div>
        <div className="table-scroll" tabIndex={0} role="region" aria-label="Scrollable improvement backlog">
          <table className="improvement-table">
            <thead><tr><th>Area</th><th>Improvement</th><th>Gate</th><th>State</th></tr></thead>
            <tbody>
              {improvementBacklog.map((item) => (
                <tr key={item.id}>
                  <td><code>{item.id}</code><span>{item.area}</span></td>
                  <td>{item.title}</td>
                  <td>{item.gate}</td>
                  <td><span className={`state-pill state-${item.state}`}>{item.state.replaceAll("-", " ")}</span></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </>
  );
}
