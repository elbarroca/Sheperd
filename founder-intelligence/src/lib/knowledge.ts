import "server-only";

import knowledgeJson from "@/generated/knowledge-index.json";
import { buildKnowledgeCatalog, buildKnowledgeFileDetail, buildKnowledgeLayerStats } from "./knowledge-catalog";
import type { KnowledgeFileDetail, KnowledgeFileSummary, KnowledgeIndex, SearchResult } from "./types";
import { searchIndex } from "./vector-search";

const knowledge = knowledgeJson as unknown as KnowledgeIndex;
const catalog = buildKnowledgeCatalog(knowledge.chunks, knowledge.files);

export function getKnowledgeSummary() {
  const layerCounts = knowledge.chunks.reduce<Record<string, number>>((counts, chunk) => {
    counts[chunk.layer] = (counts[chunk.layer] ?? 0) + 1;
    return counts;
  }, {});
  return {
    sourceDate: knowledge.sourceDate,
    sourceFiles: knowledge.sourceFiles,
    chunks: knowledge.chunks.length,
    vocabulary: knowledge.vocabulary.length,
    method: knowledge.method,
    boundary: knowledge.boundary,
    layerCounts,
    layerStats: buildKnowledgeLayerStats(knowledge.chunks, catalog),
    folders: new Set(catalog.map((file) => file.folder)).size,
  };
}

export function getKnowledgeCatalog(): KnowledgeFileSummary[] {
  return catalog;
}

export function getKnowledgeFile(path: string): KnowledgeFileDetail | null {
  const summary = catalog.find((file) => file.path === path);
  return summary ? buildKnowledgeFileDetail(knowledge.chunks, summary) : null;
}

export function searchKnowledge(query: string, limit = 12): SearchResult[] {
  return searchIndex(knowledge, query, limit);
}
