import "server-only";

import dashboardJson from "@/generated/dashboard-data.json";
import type { Blocker, Experiment } from "./types";

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

export function getBlockers(): Blocker[] {
  return dashboard.blockers;
}
