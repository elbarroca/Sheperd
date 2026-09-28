import type { Metadata } from "next";
import {
  getResearchHealth,
  getWeeklyReports,
  type WeeklyReportSummary,
} from "@/lib/research-api";

export const metadata: Metadata = { title: "How it works" };

type WorkflowStage = {
  label: string;
  description: string;
  output: string;
};

type Atom = {
  name: string;
  purpose: string;
  subAtoms: string[];
  persistence: string;
};

type PromptTrace = {
  prompt: string;
  worker: string;
  contract: string;
  gate: string;
};

const WORKFLOW_STAGES: WorkflowStage[] = [
  {
    label: "Discover",
    description: "Three bounded lanes search regulatory, port, and global market sources through Tavily.",
    output: "URLs, source metadata, lane coverage",
  },
  {
    label: "Extract",
    description: "The selected URLs are fetched and checked before an article can enter the evidence set.",
    output: "Article snapshot, retrieval status, content hash",
  },
  {
    label: "Distill",
    description: "One bounded article worker creates a structured insight packet with summary, impact, risks, opportunities, uncertainty, and next steps.",
    output: "Distillation, claims, citations, evidence locators",
  },
  {
    label: "Reconcile",
    description: "The critic checks freshness, contradictions, unsupported conclusions, and citation coverage.",
    output: "Validation findings, evidence states",
  },
  {
    label: "Report",
    description: "The weekly synthesizer turns validated packets into a cited draft that stays review-gated.",
    output: "Neon brief, API payload, Markdown-ready report",
  },
];

const ATOMS: Atom[] = [
  {
    name: "Research run",
    purpose: "The durable container for one collection and synthesis cycle.",
    subAtoms: ["run ID", "as_of timestamp", "cadence", "Neon branch", "checkpoint state"],
    persistence: "research_runs, validation_checks",
  },
  {
    name: "Discovery lane",
    purpose: "A bounded specialist responsible for a defined geography and signal family.",
    subAtoms: ["query families", "Tavily Search", "Tavily Extract", "domain filters", "tool receipts"],
    persistence: "agent_steps, agent_tool_calls, sources",
  },
  {
    name: "Article evidence",
    purpose: "The traceable source record that separates retrieval from interpretation.",
    subAtoms: ["canonical URL", "publisher", "publication date", "language", "freshness", "content hash"],
    persistence: "sources, source_snapshots",
  },
  {
    name: "Insight packet",
    purpose: "The article-level answer used by the report, never a free-form model blob.",
    subAtoms: ["summary", "what happened", "why it matters", "risk", "opportunity", "uncertainty", "next step"],
    persistence: "article_distillations",
  },
  {
    name: "Claim and signal",
    purpose: "The smallest units that can be cited, compared, and rolled up over time.",
    subAtoms: ["claim text", "source URLs", "evidence excerpt", "verification basis", "signal type"],
    persistence: "claims, signal_events",
  },
  {
    name: "Brief",
    purpose: "A cited decision document with explicit limits and human review state.",
    subAtoms: ["executive findings", "developments", "risks", "opportunities", "follow-up", "audit trail"],
    persistence: "weekly_briefs, review_decisions",
  },
];

const PROMPT_TRACE: PromptTrace[] = [
  {
    prompt: "discovery-v3-multilingual",
    worker: "Three discovery lanes",
    contract: "Source packet",
    gate: "Search and Extract must both run",
  },
  {
    prompt: "distill-v6-insight",
    worker: "One article worker per extracted source",
    contract: "Article insight packet",
    gate: "Required fields cannot be empty",
  },
  {
    prompt: "critic-v5-evidence",
    worker: "Critic and reconciler",
    contract: "Validation findings",
    gate: "Unsupported or uncited output blocks PASS",
  },
  {
    prompt: "weekly-brief-v6-decision",
    worker: "Weekly synthesizer",
    contract: "Cited weekly brief",
    gate: "Every report section needs qualified output",
  },
];

function formatModelList(report: WeeklyReportSummary): string {
  return report.models.length > 0 ? report.models.join(", ") : "Not recorded in this run";
}

function percent(value: number | undefined): string {
  return value === undefined ? "Not recorded" : `${Math.round(value * 100)}%`;
}

function metricWidth(value: number, maximum: number): string {
  if (value <= 0 || maximum <= 0) return "0%";
  return `${Math.max(8, Math.round((value / maximum) * 100))}%`;
}

function LiveSnapshot({
  report,
  healthStatus,
  healthMessage,
  dataStatus,
  dataMessage,
}: {
  report: WeeklyReportSummary | null;
  healthStatus: "online" | "unavailable";
  healthMessage?: string;
  dataStatus: "ok" | "unavailable";
  dataMessage?: string;
}) {
  if (healthStatus === "unavailable") {
    return (
      <div className="empty-state" role="status">
        <strong>Live run metrics unavailable.</strong>
        <p>{healthMessage}. Start the FastAPI service at 127.0.0.1:8787 for local development. No sample run is shown.</p>
      </div>
    );
  }

  if (dataStatus === "unavailable") {
    return (
      <div className="empty-state" role="status">
        <strong>Latest run metrics unavailable.</strong>
        <p>{dataMessage}. The workflow documentation remains available, but no stale counts are shown.</p>
      </div>
    );
  }

  if (!report) {
    return (
      <div className="empty-state" role="status">
        <strong>No recorded run yet.</strong>
        <p>The workflow map is static documentation. Live counts will appear after the first persisted run.</p>
      </div>
    );
  }

  const metrics = [
    { label: "Sources", value: report.source_count },
    { label: "Distillations", value: report.distillation_count },
    { label: "Claims", value: report.claim_count },
    { label: "Signals", value: report.signal_count },
  ];
  const maximum = Math.max(...metrics.map((metric) => metric.value), 1);

  return (
    <div className="snapshot-stack">
      <div className="snapshot-header">
        <div>
          <strong>{report.title}</strong>
          <p className="muted">As of {report.as_of}. The latest API summary is read from Neon.</p>
        </div>
        <span className="status-badge status-succeeded">{report.run_status} / {report.validation_status}</span>
      </div>
      <div className="snapshot-grid">
        <div><strong>{report.lane_coverage.length}</strong><span>lanes</span></div>
        <div><strong>{report.regions.length}</strong><span>regions</span></div>
        <div><strong>{report.languages.length}</strong><span>languages</span></div>
        <div><strong>{percent(report.article_insight_completeness)}</strong><span>article packets</span></div>
        <div><strong>{percent(report.report_section_completeness)}</strong><span>report sections</span></div>
        <div><strong>{formatModelList(report)}</strong><span>resolved model</span></div>
      </div>
      <div className="metric-chart" aria-label="Latest persisted record counts">
        {metrics.map((metric) => (
          <div className="metric-chart-row" key={metric.label}>
            <span>{metric.label}</span>
            <span className="metric-chart-line"><span style={{ width: metricWidth(metric.value, maximum) }} /></span>
            <strong>{metric.value}</strong>
          </div>
        ))}
      </div>
    </div>
  );
}

export default async function HowItWorksPage() {
  const [health, weekly] = await Promise.all([getResearchHealth(), getWeeklyReports({ archive_scope: "active", limit: 1, offset: 0 })]);
  const report = weekly.status === "ok" ? weekly.data.reports[0] : null;
  const summary = report && "brief" in report ? null : report ?? null;
  const healthStatus = health.status === "ok" ? "online" : "unavailable";
  const healthMessage = health.status === "ok" ? undefined : health.error;

  return (
    <div className="how-it-works-page">
      <header className="page-intro how-intro">
        <p className="eyebrow">System map</p>
        <h1>How research becomes a brief.</h1>
        <p>Agents collect public evidence, turn each article into a structured insight packet, validate the result, then expose the same records through Neon, the API, and the dashboard.</p>
      </header>

      <section className="how-section" aria-labelledby="workflow-heading">
        <div className="how-section-heading">
          <h2 id="workflow-heading">From source to decision</h2>
          <p>Each handoff has a defined input, output, and hard gate.</p>
        </div>
        <ol className="workflow-map">
          {WORKFLOW_STAGES.map((stage) => (
            <li className="workflow-node" key={stage.label}>
              <h3>{stage.label}</h3>
              <p>{stage.description}</p>
              <span>Output: {stage.output}</span>
            </li>
          ))}
        </ol>
      </section>

      <section className="how-section" aria-labelledby="atoms-heading">
        <div className="how-section-heading">
          <h2 id="atoms-heading">Atoms and sub-atoms</h2>
          <p>The workflow is inspectable because every object has one job and one persistence boundary.</p>
        </div>
        <div className="atom-list">
          {ATOMS.map((atom) => (
            <details className="atom-row" key={atom.name} open>
              <summary><strong>{atom.name}</strong><span>{atom.persistence}</span></summary>
              <div className="atom-detail">
                <p>{atom.purpose}</p>
                <ul>{atom.subAtoms.map((subAtom) => <li key={subAtom}>{subAtom}</li>)}</ul>
              </div>
            </details>
          ))}
        </div>
      </section>

      <section className="how-section" aria-labelledby="prompts-heading">
        <div className="how-section-heading">
          <h2 id="prompts-heading">Prompt and contract trace</h2>
          <p>Prompt versions are recorded with agent steps. The system stores structured rationale, not private chain-of-thought.</p>
        </div>
        <div className="prompt-list">
          {PROMPT_TRACE.map((item) => (
            <div className="prompt-row" key={item.prompt}>
              <code>{item.prompt}</code>
              <span>{item.worker}</span>
              <span>{item.contract}</span>
              <strong>{item.gate}</strong>
            </div>
          ))}
        </div>
      </section>

      <section className="how-section" aria-labelledby="snapshot-heading">
        <div className="how-section-heading">
          <h2 id="snapshot-heading">Live system snapshot</h2>
          <p>These counts come from the current API response. They are not fixtures or estimates.</p>
        </div>
        <LiveSnapshot
          report={summary}
          healthStatus={healthStatus}
          healthMessage={healthMessage}
          dataStatus={weekly.status}
          dataMessage={weekly.status === "unavailable" ? weekly.error : undefined}
        />
      </section>

      <section className="how-boundary" aria-labelledby="boundary-heading">
        <div>
          <h2 id="boundary-heading">What the UI can prove</h2>
          <p>The dashboard can show source links, article packets, citations, evidence states, timestamps, model identity, tool receipts, and validation findings.</p>
        </div>
        <ul>
          <li>Neon is the source of truth.</li>
          <li>OpenAI workers are bounded inside LangGraph.</li>
          <li>Every article needs a complete or explicitly qualified packet.</li>
          <li>Human review is required before approval or export.</li>
        </ul>
      </section>
    </div>
  );
}
