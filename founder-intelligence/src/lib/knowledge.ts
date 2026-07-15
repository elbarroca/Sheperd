import "server-only";

import knowledgeJson from "@/generated/knowledge-index.json";
import type { KnowledgeIndex, SearchResult } from "./types";
import { searchIndex } from "./vector-search";

const knowledge = knowledgeJson as unknown as KnowledgeIndex;

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
  };
}

export function searchKnowledge(query: string, limit = 12): SearchResult[] {
  return searchIndex(knowledge, query, limit);
}
