import type { Metadata } from "next";
import { UnavailableState } from "@/components/report-accordion";
import { getMonthlyRollups } from "@/lib/research-api";

export const metadata: Metadata = { title: "Monthly rollups" };

export default async function MonthlyPage() {
  const response = await getMonthlyRollups();
  if (response.status === "unavailable") return <UnavailableState error={response.error} />;
  return (
    <div className="page-stack">
      <div className="page-intro">
        <p className="eyebrow">Deterministic aggregation</p>
        <h1>Monthly signal rollups.</h1>
        <p>Counts come directly from persisted signal events. No second LLM synthesis is used here.</p>
      </div>
      <div className="rollup-table">
        <div className="rollup-row rollup-head"><span>Month</span><span>Signals</span><span>Runs</span><span>Geographies</span></div>
        {response.data.rollups.length > 0 ? response.data.rollups.map((rollup) => (
          <div className="rollup-row" key={rollup.month}>
            <strong>{rollup.month}</strong>
            <span>{rollup.signals}</span>
            <span>{rollup.runs}</span>
            <span>{rollup.geographies.join(", ") || "None recorded"}</span>
          </div>
        )) : <p className="empty-state">No persisted signal events yet.</p>}
      </div>
    </div>
  );
}
