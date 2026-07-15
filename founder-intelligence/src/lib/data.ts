import "server-only";

import dashboardJson from "@/generated/dashboard-data.json";
import type { Blocker, Experiment, FounderAction, FounderActionLane, FounderActionPlan } from "./types";

interface SourceRow {
  source_id: string;
  evidence_status: string;
  confidence: string;
  title: string;
}

interface ExperimentRow {
  experiment_id: string;
  name: string;
  primary_hypothesis: string;
  owner: string;
  approver: string;
  eligibility: string;
  outcome_event: string;
  quality_metric: string;
  continue_threshold: string;
  stop_threshold: string;
  canonical_source: string;
  execution_state: string;
  learning_value: string;
  evidence_readiness: string;
  risk: string;
  effort: string;
}

interface WorkflowRow {
  workflow_id: string;
  coverage_status: string;
  workstream: string;
}

interface AiOpportunityRow {
  opportunity_id: string;
  initial_class: string;
  state: string;
}

interface DashboardData {
  contractVersion: number;
  sourceDate: string;
  scores: {
    researchSystem: number;
    gtmDesign: number;
    realMarketEvidence: number;
    safeExecutionReadiness: number;
  };
  sources: SourceRow[];
  blockers: Blocker[];
  experiments: ExperimentRow[];
  workflows: WorkflowRow[];
  aiOpportunities: AiOpportunityRow[];
  measurements: Record<string, string>[];
  timeSavings: Record<string, string>[];
  contentBacklog: Record<string, string>[];
  artifacts: Record<string, string>[];
}

const dashboard = dashboardJson as unknown as DashboardData;

function countBy<T>(items: T[], key: (item: T) => string): Record<string, number> {
  return items.reduce<Record<string, number>>((counts, item) => {
    const value = key(item) || "unknown";
    counts[value] = (counts[value] ?? 0) + 1;
    return counts;
  }, {});
}

function parseScore(value: string, field: string): number {
  const parsed = Number.parseInt(value, 10);
  if (!Number.isInteger(parsed) || parsed < 1 || parsed > 5) {
    throw new Error(`${field} must be an integer from 1 to 5`);
  }
  return parsed;
}

function getActionLane(executionState: string): FounderActionLane {
  if (executionState === "prepare-now") return "do-now";
  if (executionState === "synthetic-only") return "prepare-internally";
  return "not-yet";
}

function formatAccountability(value: string): string {
  return value
    .split(" and ")
    .map((item) => {
      if (item === "Michael") return "GTM lead - Michael";
      if (item === "Avi") return "Founder - Avi";
      return item;
    })
    .join(" · ");
}

function toFounderAction(row: ExperimentRow): FounderAction {
  return {
    experimentId: row.experiment_id,
    title: row.name,
    owner: formatAccountability(row.owner),
    approver: formatAccountability(row.approver),
    lane: getActionLane(row.execution_state),
    requiredEvidence: row.eligibility,
    doneWhen: `${row.outcome_event}. ${row.quality_metric}.`,
    continueThreshold: row.continue_threshold,
    stopRule: row.stop_threshold,
    sourcePath: row.canonical_source,
  };
}

export function getOverviewData() {
  return {
    sourceDate: dashboard.sourceDate,
    scores: dashboard.scores,
    sourceStates: countBy(dashboard.sources, (source) => source.evidence_status),
    sourceConfidence: countBy(dashboard.sources, (source) => source.confidence),
    experimentStates: countBy(dashboard.experiments, (experiment) => experiment.execution_state),
    workflowStates: countBy(dashboard.workflows, (workflow) => workflow.coverage_status),
    aiClasses: countBy(dashboard.aiOpportunities, (opportunity) => opportunity.initial_class),
    blockers: dashboard.blockers,
    counts: {
      sources: dashboard.sources.length,
      workflows: dashboard.workflows.length,
      aiOpportunities: dashboard.aiOpportunities.length,
      blockers: dashboard.blockers.length,
      experiments: dashboard.experiments.length,
      measurements: dashboard.measurements.length,
      capacityModels: dashboard.timeSavings.length,
      contentItems: dashboard.contentBacklog.length,
      artifacts: dashboard.artifacts.length,
    },
  };
}

export function getExperiments(): Experiment[] {
  return dashboard.experiments.map((row) => ({
    experimentId: row.experiment_id,
    name: row.name,
    hypothesis: row.primary_hypothesis,
    executionState: row.execution_state,
    learningValue: parseScore(row.learning_value, "learningValue"),
    evidenceReadiness: parseScore(row.evidence_readiness, "evidenceReadiness"),
    risk: parseScore(row.risk, "risk"),
    effort: parseScore(row.effort, "effort"),
  }));
}

export function getFounderActionPlan(): FounderActionPlan {
  const actions = dashboard.experiments.map(toFounderAction);
  const primary = actions.find((action) => action.experimentId === "EXP-001");
  if (!primary) throw new Error("EXP-001 is required for the founder action plan.");

  return {
    primary,
    doNow: actions.filter((action) => action.lane === "do-now"),
    prepareInternally: actions.filter((action) => action.lane === "prepare-internally"),
    notYet: actions.filter((action) => action.lane === "not-yet"),
  };
}

export function getBlockers(): Blocker[] {
  return dashboard.blockers;
}
