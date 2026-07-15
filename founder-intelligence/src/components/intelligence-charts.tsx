"use client";

import { useSyncExternalStore } from "react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Legend,
  Pie,
  PieChart,
  PolarAngleAxis,
  PolarGrid,
  PolarRadiusAxis,
  Radar,
  RadarChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { KnowledgeLayerStat } from "@/lib/types";

interface IntelligenceChartsProps {
  scores: {
    researchSystem: number;
    gtmDesign: number;
    realMarketEvidence: number;
    safeExecutionReadiness: number;
  };
  layerStats: KnowledgeLayerStat[];
  sourceStates: Record<string, number>;
}

const evidenceColors = ["#136efc", "#5a8ff0", "#8aa9dc", "#efaa3c", "#df5f55", "#727b92"];

function formatLabel(value: string): string {
  return value.replaceAll("-", " ").replace(/\b\w/gu, (letter) => letter.toUpperCase());
}

function subscribeToReducedMotion(callback: () => void): () => void {
  const mediaQuery = window.matchMedia("(prefers-reduced-motion: reduce)");
  mediaQuery.addEventListener("change", callback);
  return () => mediaQuery.removeEventListener("change", callback);
}

function getReducedMotionSnapshot(): boolean {
  return window.matchMedia("(prefers-reduced-motion: reduce)").matches;
}

function useReducedMotion(): boolean {
  return useSyncExternalStore(subscribeToReducedMotion, getReducedMotionSnapshot, () => true);
}

export function IntelligenceCharts({ scores, layerStats, sourceStates }: IntelligenceChartsProps) {
  const reducedMotion = useReducedMotion();
  const scoreData = [
    { label: "Research system", value: scores.researchSystem },
    { label: "GTM design", value: scores.gtmDesign },
    { label: "Market proof", value: scores.realMarketEvidence },
    { label: "Safe execution", value: scores.safeExecutionReadiness },
  ];
  const corpusData = layerStats.map((stat) => ({
    label: formatLabel(stat.layer),
    files: stat.files,
    sectionsPerFile: Number((stat.chunks / Math.max(stat.files, 1)).toFixed(1)),
  }));
  const evidenceData = Object.entries(sourceStates)
    .map(([state, count]) => ({ state: formatLabel(state), count }))
    .sort((left, right) => right.count - left.count);
  const tooltipStyle = {
    border: "1px solid #c9d6e6",
    borderRadius: "8px",
    background: "#ffffff",
    color: "#07101e",
    fontSize: "12px",
    boxShadow: "0 12px 30px rgba(7, 16, 30, 0.12)",
  };

  return (
    <section className="intelligence-section section-block" aria-labelledby="intelligence-charts-title">
      <div className="section-heading">
        <div>
          <p className="eyebrow">Intelligence atlas</p>
          <h2 id="intelligence-charts-title">See depth, proof, and readiness as separate signals</h2>
        </div>
        <p>Every mark is generated from the committed corpus. No synthetic trend line or forecast is shown.</p>
      </div>

      <div className="intelligence-charts">
        <article className="chart-card chart-readiness">
          <header><span>01</span><div><h3>Decision readiness</h3><p>Four admitted planning scores, each out of ten.</p></div></header>
          <div className="chart-frame" role="img" aria-label="Radar chart showing strong research and GTM design but low market proof and safe execution readiness">
            <ResponsiveContainer width="100%" height="100%">
              <RadarChart data={scoreData} outerRadius="72%" margin={{ top: 16, right: 36, bottom: 16, left: 36 }}>
                <PolarGrid stroke="#cfdae8" />
                <PolarAngleAxis dataKey="label" tick={{ fill: "#4b5c72", fontSize: 11 }} />
                <PolarRadiusAxis domain={[0, 10]} tickCount={6} axisLine={false} tick={{ fill: "#738198", fontSize: 9 }} />
                <Radar
                  dataKey="value"
                  name="Score"
                  stroke="#136efc"
                  strokeWidth={2}
                  fill="#136efc"
                  fillOpacity={0.16}
                  isAnimationActive={!reducedMotion}
                />
                <Tooltip contentStyle={tooltipStyle} />
              </RadarChart>
            </ResponsiveContainer>
          </div>
          <details className="chart-data-table">
            <summary>Read exact score data</summary>
            <dl>{scoreData.map((item) => <div key={item.label}><dt>{item.label}</dt><dd>{item.value}/10</dd></div>)}</dl>
          </details>
        </article>

        <article className="chart-card chart-corpus">
          <header><span>02</span><div><h3>Corpus shape</h3><p>File coverage and section depth by knowledge layer.</p></div></header>
          <div className="chart-frame" role="img" aria-label="Bar chart comparing source file count and indexed sections per file across knowledge layers">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={corpusData} margin={{ top: 18, right: 12, bottom: 56, left: 0 }}>
                <CartesianGrid stroke="#e2e9f1" vertical={false} />
                <XAxis dataKey="label" angle={-32} textAnchor="end" interval={0} tick={{ fill: "#5c6d83", fontSize: 10 }} />
                <YAxis allowDecimals={false} tick={{ fill: "#738198", fontSize: 10 }} width={34} />
                <Tooltip contentStyle={tooltipStyle} cursor={{ fill: "#edf4ff" }} />
                <Legend wrapperStyle={{ fontSize: "11px", paddingTop: "8px" }} />
                <Bar dataKey="files" name="Files" fill="#136efc" radius={[4, 4, 0, 0]} isAnimationActive={!reducedMotion} />
                <Bar dataKey="sectionsPerFile" name="Sections / file" fill="#9fb7db" radius={[4, 4, 0, 0]} isAnimationActive={!reducedMotion} />
              </BarChart>
            </ResponsiveContainer>
          </div>
          <details className="chart-data-table">
            <summary>Read exact corpus data</summary>
            <dl>{layerStats.map((item) => <div key={item.layer}><dt>{formatLabel(item.layer)}</dt><dd>{item.files} files, {item.chunks} sections</dd></div>)}</dl>
          </details>
        </article>

        <article className="chart-card chart-evidence">
          <header><span>03</span><div><h3>Evidence state</h3><p>What the source ledger can support today.</p></div></header>
          <div className="chart-frame" role="img" aria-label="Donut chart showing the current source evidence state distribution">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={evidenceData}
                  dataKey="count"
                  nameKey="state"
                  innerRadius="54%"
                  outerRadius="78%"
                  paddingAngle={2}
                  stroke="#ffffff"
                  strokeWidth={2}
                  isAnimationActive={!reducedMotion}
                >
                  {evidenceData.map((item, index) => <Cell key={item.state} fill={evidenceColors[index % evidenceColors.length]} />)}
                </Pie>
                <Tooltip contentStyle={tooltipStyle} />
                <Legend iconType="circle" wrapperStyle={{ fontSize: "10px" }} />
              </PieChart>
            </ResponsiveContainer>
          </div>
          <details className="chart-data-table">
            <summary>Read exact evidence data</summary>
            <dl>{evidenceData.map((item) => <div key={item.state}><dt>{item.state}</dt><dd>{item.count}</dd></div>)}</dl>
          </details>
        </article>
      </div>
    </section>
  );
}
