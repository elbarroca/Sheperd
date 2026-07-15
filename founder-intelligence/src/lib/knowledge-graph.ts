import type { KnowledgeFileSummary } from "./types";

export interface KnowledgeGraphNode {
  path: string;
  depth: number;
}

export interface KnowledgeGraphEdge {
  source: string;
  target: string;
}

export interface KnowledgeNeighborhood {
  nodes: KnowledgeGraphNode[];
  edges: KnowledgeGraphEdge[];
}

function connectionCount(file: KnowledgeFileSummary): number {
  return file.outgoingLinks.length + file.incomingLinks.length;
}

export function buildKnowledgeNeighborhood(
  files: KnowledgeFileSummary[],
  activePath: string,
  maxDepth: 1 | 2,
  maxFiles = 36,
): KnowledgeNeighborhood {
  const filesByPath = new Map(files.map((file) => [file.path, file]));
  if (!filesByPath.has(activePath)) return { nodes: [], edges: [] };

  const depthByPath = new Map<string, number>([[activePath, 0]]);
  const routeEdges: KnowledgeGraphEdge[] = [];
  const queue = [activePath];

  while (queue.length > 0 && depthByPath.size < maxFiles) {
    const path = queue.shift();
    if (!path) break;
    const depth = depthByPath.get(path) ?? 0;
    if (depth >= maxDepth) continue;

    const file = filesByPath.get(path);
    if (!file) continue;
    const neighbors = [...new Set([...file.outgoingLinks, ...file.incomingLinks])]
      .map((neighborPath) => filesByPath.get(neighborPath))
      .filter((neighbor): neighbor is KnowledgeFileSummary => neighbor !== undefined)
      .sort((left, right) => connectionCount(right) - connectionCount(left) || left.path.localeCompare(right.path));

    for (const neighbor of neighbors) {
      if (depthByPath.has(neighbor.path)) continue;
      depthByPath.set(neighbor.path, depth + 1);
      routeEdges.push(file.outgoingLinks.includes(neighbor.path)
        ? { source: path, target: neighbor.path }
        : { source: neighbor.path, target: path });
      queue.push(neighbor.path);
      if (depthByPath.size >= maxFiles) break;
    }
  }

  const nodes = [...depthByPath.entries()]
    .map(([path, depth]) => ({ path, depth }))
    .sort((left, right) => left.depth - right.depth
      || connectionCount(filesByPath.get(right.path)!) - connectionCount(filesByPath.get(left.path)!)
      || left.path.localeCompare(right.path));

  return { nodes, edges: routeEdges };
}
