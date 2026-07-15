import type { Blocker } from "@/lib/types";

const clusters = [
  { name: "Authority and ownership", ids: ["GAP-001", "GAP-002", "GAP-003"] },
  { name: "Product and proof", ids: ["GAP-004", "GAP-005"] },
  { name: "Commercial and claims", ids: ["GAP-006", "GAP-008"] },
  { name: "Domain review", ids: ["GAP-007"] },
  { name: "Data and CRM", ids: ["GAP-009", "GAP-010"] },
  { name: "Capacity and publication", ids: ["GAP-011", "GAP-012"] },
] as const;

export function BlockerMap({ blockers }: { blockers: Blocker[] }) {
  const blockerById = new Map(blockers.map((blocker) => [blocker.blocker_id, blocker]));

  return (
    <section className="blocker-map section-block" aria-labelledby="blocker-map-title">
      <div className="section-heading">
        <div>
          <p className="eyebrow">Decision map</p>
          <h2 id="blocker-map-title">Six conversations resolve twelve open gates</h2>
        </div>
        <p>The center remains blocked until every branch has admitted evidence and an accountable approver.</p>
      </div>
      <div className="mind-map">
        <div className="mind-map-center" aria-label="External activation is on hold">
          <span>Current posture</span>
          <strong>External hold</strong>
          <p>{blockers.length} open gates</p>
        </div>
        <ol className="mind-map-branches">
          {clusters.map((cluster) => {
            const items = cluster.ids.map((id) => blockerById.get(id)).filter((item): item is Blocker => item !== undefined);

            return (
              <li key={cluster.name}>
                <div className="cluster-head"><h3>{cluster.name}</h3><span>{items.length} {items.length === 1 ? "gate" : "gates"}</span></div>
                <ul>
                  {items.map((item) => (
                    <li key={item.blocker_id}>
                      <code>{item.blocker_id}</code>
                      <p>{item.decision_question}</p>
                      <details>
                        <summary>Owner and next evidence</summary>
                        <dl>
                          <div><dt>Owner</dt><dd>{item.owner}</dd></div>
                          <div><dt>Next</dt><dd>{item.next_action}</dd></div>
                        </dl>
                      </details>
                    </li>
                  ))}
                </ul>
              </li>
            );
          })}
        </ol>
      </div>
    </section>
  );
}
