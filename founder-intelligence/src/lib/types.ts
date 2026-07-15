export type KnowledgeLayer =
  | "founder-context"
  | "operating-system"
  | "research"
  | "ricardo-interpretation"
  | "source"
  | "structured-data"
  | "template";

export type SparseVector = [number, number][];

export interface KnowledgeChunk {
  id: string;
  path: string;
  title: string;
  section: string;
  layer: KnowledgeLayer;
  evidenceStatus: string;
  confidentiality: string;
  tags: string[];
  text: string;
  vector: SparseVector;
}

export interface KnowledgeIndex {
  contractVersion: number;
  method: string;
  boundary: string;
  sourceDate: string;
  sourceFiles: number;
  files?: KnowledgeFileManifest[];
  vocabulary: string[];
  idf: number[];
  chunks: KnowledgeChunk[];
}

export interface KnowledgeFileManifest {
  path: string;
  title: string;
  layer: KnowledgeLayer;
  evidenceStatus: string;
  confidentiality: string;
  tags: string[];
  links?: string[];
}

export interface SearchResult {
  id: string;
  path: string;
  title: string;
  section: string;
  layer: KnowledgeLayer;
  evidenceStatus: string;
  text: string;
  score: number;
}

export interface KnowledgeFileSummary {
  path: string;
  title: string;
  folder: string;
  primaryLayer: KnowledgeLayer;
  layers: KnowledgeLayer[];
  evidenceStatuses: string[];
  confidentiality: string[];
  tags: string[];
  sectionCount: number;
  wordCount: number;
  outgoingLinks: string[];
  incomingLinks: string[];
}

export interface KnowledgeFileSection {
  id: string;
  section: string;
  layer: KnowledgeLayer;
  evidenceStatus: string;
  text: string;
}

export interface KnowledgeFileDetail extends KnowledgeFileSummary {
  sections: KnowledgeFileSection[];
}

export interface KnowledgeLayerStat {
  layer: KnowledgeLayer;
  files: number;
  chunks: number;
}

export type BriefLensId = "company" | "industry" | "goals";

export interface BriefLens {
  id: BriefLensId;
  label: string;
  finding: string;
  implication: string;
  nextAction: string;
  sourcePath: string;
}

export type FounderActionLane = "do-now" | "prepare-internally" | "not-yet";

export interface FounderAction {
  experimentId: string;
  title: string;
  owner: string;
  approver: string;
  lane: FounderActionLane;
  requiredEvidence: string;
  doneWhen: string;
  continueThreshold: string;
  stopRule: string;
  sourcePath: string;
}

export interface FounderActionPlan {
  primary: FounderAction;
  doNow: FounderAction[];
  prepareInternally: FounderAction[];
  notYet: FounderAction[];
}

export interface Experiment {
  experimentId: string;
  name: string;
  hypothesis: string;
  executionState: string;
  learningValue: number;
  evidenceReadiness: number;
  risk: number;
  effort: number;
}

export interface RankedExperiment extends Experiment {
  executionAllowed: boolean;
  priorityScore: number;
}

export interface PriorityWeights {
  learningValue: number;
  evidenceReadiness: number;
  lowerRisk: number;
  lowerEffort: number;
}

export interface Blocker {
  blocker_id: string;
  gate: string;
  decision_question: string;
  owner: string;
  current_state: string;
  next_action: string;
}

export type CompetitorCategory = "recovery" | "audit" | "enterprise";

export interface CompetitorProfile {
  id: string;
  name: string;
  url: string;
  category: CompetitorCategory;
  categoryLabel: string;
  specialization: number;
  workflowBreadth: number;
  offer: string;
  pricingSignal: string;
  evidenceBoundary: string;
}

export interface MarketSignal {
  id: string;
  value: string;
  label: string;
  meaning: string;
  boundary: string;
  url?: string;
}

export type MichaelTaskState = "prepare-now" | "approval-gated";

export interface MichaelTask {
  id: string;
  workstream: string;
  outcome: string;
  aiAssist: string;
  humanDecision: string;
  state: MichaelTaskState;
  sourcePath: string;
}
