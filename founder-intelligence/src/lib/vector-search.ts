import vectorContract from "../../vector-contract.json";
import type { KnowledgeIndex, SearchResult, SparseVector } from "./types";

const stopWords = new Set(vectorContract.stopWords);

export function tokenize(text: string): string[] {
  return (text.toLowerCase().match(/[\p{L}\p{N}]+/gu) ?? []).filter(
    (term) => term.length > 1 && !stopWords.has(term),
  );
}

export function buildQueryVector(query: string, index: KnowledgeIndex): SparseVector {
  const termIndex = new Map(index.vocabulary.map((term, position) => [term, position]));
  const counts = new Map<number, number>();
  for (const term of tokenize(query)) {
    const position = termIndex.get(term);
    if (position !== undefined) counts.set(position, (counts.get(position) ?? 0) + 1);
  }
  const weighted = [...counts.entries()].map(
    ([position, count]) => [position, (1 + Math.log(count)) * index.idf[position]] as [number, number],
  );
  const magnitude = Math.sqrt(weighted.reduce((sum, [, value]) => sum + value * value, 0)) || 1;
  return weighted
    .map(([position, value]) => [position, value / magnitude] as [number, number])
    .sort((left, right) => left[0] - right[0]);
}

export function cosineSimilarity(left: SparseVector, right: SparseVector): number {
  let leftIndex = 0;
  let rightIndex = 0;
  let score = 0;
  while (leftIndex < left.length && rightIndex < right.length) {
    const [leftPosition, leftValue] = left[leftIndex];
    const [rightPosition, rightValue] = right[rightIndex];
    if (leftPosition === rightPosition) {
      score += leftValue * rightValue;
      leftIndex += 1;
      rightIndex += 1;
    } else if (leftPosition < rightPosition) {
      leftIndex += 1;
    } else {
      rightIndex += 1;
    }
  }
  return score;
}

export function searchIndex(index: KnowledgeIndex, query: string, limit = 12): SearchResult[] {
  const normalizedQuery = query.trim();
  if (normalizedQuery.length < 2 || normalizedQuery.length > 160) return [];
  const queryVector = buildQueryVector(normalizedQuery, index);
  if (!queryVector.length) return [];
  return index.chunks
    .map((chunk) => ({ chunk, score: cosineSimilarity(queryVector, chunk.vector) }))
    .filter(({ score }) => score > 0)
    .sort((left, right) => right.score - left.score || left.chunk.id.localeCompare(right.chunk.id))
    .slice(0, Math.min(Math.max(limit, 1), 20))
    .map(({ chunk, score }) => ({
      id: chunk.id,
      path: chunk.path,
      title: chunk.title,
      section: chunk.section,
      layer: chunk.layer,
      evidenceStatus: chunk.evidenceStatus,
      text: chunk.text,
      score: Number(score.toFixed(4)),
    }));
}
