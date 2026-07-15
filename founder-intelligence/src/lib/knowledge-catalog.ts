import type {
  KnowledgeChunk,
  KnowledgeFileDetail,
  KnowledgeFileManifest,
  KnowledgeFileSummary,
  KnowledgeLayer,
  KnowledgeLayerStat,
} from "./types";

interface FileAccumulator {
  path: string;
  title: string;
  folder: string;
  layers: Set<KnowledgeLayer>;
  layerCounts: Map<KnowledgeLayer, number>;
  evidenceStatuses: Set<string>;
  confidentiality: Set<string>;
  tags: Set<string>;
  sectionCount: number;
  wordCount: number;
}

function countWords(text: string): number {
  const trimmed = text.trim();
  return trimmed.length === 0 ? 0 : trimmed.split(/\s+/u).length;
}

function sortStrings(values: Set<string>): string[] {
  return [...values].sort((left, right) => left.localeCompare(right));
}

function getPrimaryLayer(counts: Map<KnowledgeLayer, number>): KnowledgeLayer {
  const ranked = [...counts.entries()].sort((left, right) => {
    const countDifference = right[1] - left[1];
    return countDifference === 0 ? left[0].localeCompare(right[0]) : countDifference;
  });
  const primary = ranked[0]?.[0];
  if (!primary) throw new Error("A knowledge file must contain at least one layer.");
  return primary;
}

export function buildKnowledgeCatalog(
  chunks: KnowledgeChunk[],
  manifests: KnowledgeFileManifest[] = [],
): KnowledgeFileSummary[] {
  const files = new Map<string, FileAccumulator>();

  for (const chunk of chunks) {
    const current = files.get(chunk.path) ?? {
      path: chunk.path,
      title: chunk.title,
      folder: chunk.path.split("/")[0] ?? "Root",
      layers: new Set<KnowledgeLayer>(),
      layerCounts: new Map<KnowledgeLayer, number>(),
      evidenceStatuses: new Set<string>(),
      confidentiality: new Set<string>(),
      tags: new Set<string>(),
      sectionCount: 0,
      wordCount: 0,
    };

    current.layers.add(chunk.layer);
    current.layerCounts.set(chunk.layer, (current.layerCounts.get(chunk.layer) ?? 0) + 1);
    current.evidenceStatuses.add(chunk.evidenceStatus);
    current.confidentiality.add(chunk.confidentiality);
    chunk.tags.forEach((tag) => current.tags.add(tag));
    current.sectionCount += 1;
    current.wordCount += countWords(chunk.text);
    files.set(chunk.path, current);
  }

  const summaries = [...files.values()]
    .map((file) => ({
      path: file.path,
      title: file.title,
      folder: file.folder,
      primaryLayer: getPrimaryLayer(file.layerCounts),
      layers: [...file.layers].sort((left, right) => left.localeCompare(right)),
      evidenceStatuses: sortStrings(file.evidenceStatuses),
      confidentiality: sortStrings(file.confidentiality),
      tags: sortStrings(file.tags),
      sectionCount: file.sectionCount,
      wordCount: file.wordCount,
    }))
    .sort((left, right) => left.path.localeCompare(right.path));

  const indexedPaths = new Set(summaries.map((file) => file.path));
  const emptyFiles = manifests
    .filter((file) => !indexedPaths.has(file.path))
    .map((file): KnowledgeFileSummary => ({
      path: file.path,
      title: file.title,
      folder: file.path.split("/")[0] ?? "Root",
      primaryLayer: file.layer,
      layers: [file.layer],
      evidenceStatuses: [file.evidenceStatus],
      confidentiality: [file.confidentiality],
      tags: [...file.tags].sort((left, right) => left.localeCompare(right)),
      sectionCount: 0,
      wordCount: 0,
    }));

  return [...summaries, ...emptyFiles].sort((left, right) => left.path.localeCompare(right.path));
}

export function buildKnowledgeFileDetail(
  chunks: KnowledgeChunk[],
  summary: KnowledgeFileSummary,
): KnowledgeFileDetail {
  return {
    ...summary,
    sections: chunks
      .filter((chunk) => chunk.path === summary.path)
      .map((chunk) => ({
        id: chunk.id,
        section: chunk.section,
        layer: chunk.layer,
        evidenceStatus: chunk.evidenceStatus,
        text: chunk.text,
      })),
  };
}

export function buildKnowledgeLayerStats(
  chunks: KnowledgeChunk[],
  catalog: KnowledgeFileSummary[],
): KnowledgeLayerStat[] {
  const layers = new Set<KnowledgeLayer>(chunks.map((chunk) => chunk.layer));

  return [...layers]
    .map((layer) => ({
      layer,
      files: catalog.filter((file) => file.layers.includes(layer)).length,
      chunks: chunks.filter((chunk) => chunk.layer === layer).length,
    }))
    .sort((left, right) => right.chunks - left.chunks);
}
