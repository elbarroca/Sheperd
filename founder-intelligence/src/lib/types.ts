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
