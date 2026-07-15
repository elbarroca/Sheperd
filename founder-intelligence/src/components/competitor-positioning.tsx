"use client";

import {
  CartesianGrid,
  LabelList,
  ResponsiveContainer,
  Scatter,
  ScatterChart,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { competitorProfiles } from "@/lib/focused-content";
import type { CompetitorCategory } from "@/lib/types";

const categorySeries: readonly {
  id: CompetitorCategory;
  label: string;
  color: string;
}[] = [
  { id: "recovery", label: "Recovery specialists", color: "#136efc" },
  { id: "audit", label: "Audit and prevention", color: "#5f7899" },
  { id: "enterprise", label: "Enterprise audit", color: "#8b5c08" },
];

const sheperdPoint = [{ name: "SheperD target", specialization: 5.2, workflowBreadth: 3.4 }];

export function CompetitorPositioning() {
  return (
    <div className="positioning-visual">
      <div className="positioning-chart" aria-hidden="true">
        <ResponsiveContainer width="100%" height="100%">
          <ScatterChart margin={{ top: 34, right: 28, bottom: 42, left: 4 }}>
            <CartesianGrid stroke="#d6e0ec" strokeDasharray="3 5" />
            <XAxis
              type="number"
              dataKey="specialization"
              domain={[0, 6]}
              ticks={[1, 2, 3, 4, 5]}
              tick={{ fill: "#526278", fontSize: 12 }}
              label={{ value: "D&D specialization", position: "insideBottom", offset: -22, fill: "#526278" }}
            />
            <YAxis
              type="number"
              dataKey="workflowBreadth"
              domain={[0, 6]}
              ticks={[1, 2, 3, 4, 5]}
              tick={{ fill: "#526278", fontSize: 12 }}
              label={{ value: "Workflow breadth", angle: -90, position: "insideLeft", fill: "#526278" }}
            />
            <Tooltip cursor={{ stroke: "#829aa3", strokeDasharray: "4 4" }} />
            {categorySeries.map((series) => (
              <Scatter
                key={series.id}
                name={series.label}
                data={competitorProfiles.filter((profile) => profile.category === series.id)}
                fill={series.color}
              />
            ))}
            <Scatter name="SheperD intended wedge" data={sheperdPoint} fill="#b63732">
              <LabelList dataKey="name" position="top" fill="#07101e" fontSize={12} fontWeight={700} />
            </Scatter>
          </ScatterChart>
        </ResponsiveContainer>
      </div>
      <div className="positioning-legend" aria-label="Positioning chart legend">
        {categorySeries.map((series) => (
          <span key={series.id}><i style={{ background: series.color }} />{series.label}</span>
        ))}
        <span><i style={{ background: "#b63732" }} />SheperD intended wedge</span>
      </div>
      <p className="chart-boundary">Analytical classification only. Coordinates describe public offer shape, not performance, traction, or superiority.</p>
      <table className="sr-only">
        <caption>Accessible data for the competitor positioning chart</caption>
        <thead><tr><th>Provider</th><th>D&amp;D specialization</th><th>Workflow breadth</th></tr></thead>
        <tbody>
          {competitorProfiles.map((profile) => <tr key={profile.id}><th>{profile.name}</th><td>{profile.specialization}</td><td>{profile.workflowBreadth}</td></tr>)}
          <tr><th>SheperD intended wedge</th><td>{sheperdPoint[0].specialization}</td><td>{sheperdPoint[0].workflowBreadth}</td></tr>
        </tbody>
      </table>
    </div>
  );
}
