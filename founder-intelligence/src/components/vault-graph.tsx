"use client";

import type { ReactNode } from "react";
import { useMemo, useState } from "react";
import {
  Background,
  BackgroundVariant,
  Controls,
  MarkerType,
  ReactFlow,
  type Edge,
  type Node,
  type NodeMouseHandler,
} from "@xyflow/react";
import { buildKnowledgeNeighborhood } from "@/lib/knowledge-graph";
import type { KnowledgeFileSummary } from "@/lib/types";

type VaultNodeData = {
  label: ReactNode;
  path: string;
};

type VaultNode = Node<VaultNodeData>;

interface VaultGraphProps {
  files: KnowledgeFileSummary[];
  activePath: string | null;
  openPaths: string[];
  onOpenFile: (path: string) => void;
}

function nodeLabel(file: KnowledgeFileSummary): ReactNode {
  return (
    <span>
      <strong>{file.title}</strong>
      <small>{file.outgoingLinks.length} links out · {file.incomingLinks.length} backlinks</small>
    </span>
  );
}

function getDefaultPath(files: KnowledgeFileSummary[]): string | null {
  return [...files]
    .sort((left, right) => right.outgoingLinks.length + right.incomingLinks.length
      - left.outgoingLinks.length - left.incomingLinks.length || left.path.localeCompare(right.path))[0]?.path ?? null;
}

function buildGraph(
  files: KnowledgeFileSummary[],
  rootPath: string,
  depth: 1 | 2,
  openPaths: string[],
): { nodes: VaultNode[]; edges: Edge[] } {
  const filesByPath = new Map(files.map((file) => [file.path, file]));
  const neighborhood = buildKnowledgeNeighborhood(files, rootPath, depth, depth === 1 ? 14 : 30);
  const ringMembers = new Map<number, string[]>();

  for (const node of neighborhood.nodes) {
    ringMembers.set(node.depth, [...(ringMembers.get(node.depth) ?? []), node.path]);
  }

  const nodes = neighborhood.nodes.flatMap((node): VaultNode[] => {
    const file = filesByPath.get(node.path);
    if (!file) return [];
    const ring = ringMembers.get(node.depth) ?? [node.path];
    const index = ring.indexOf(node.path);
    const angle = ring.length === 1 ? 0 : -Math.PI / 2 + (index * Math.PI * 2) / ring.length;
    const radius = node.depth * 460;
    const position = node.depth === 0
      ? { x: 0, y: 0 }
      : { x: Math.cos(angle) * radius, y: Math.sin(angle) * radius * 0.72 };
    const stateClass = node.path === rootPath
      ? "vault-node-active"
      : openPaths.includes(node.path) ? "vault-node-open" : "";

    return [{
      id: node.path,
      position,
      data: { label: nodeLabel(file), path: node.path },
      className: `vault-node vault-node-file ${stateClass}`.trim(),
    }];
  });
  const edges = neighborhood.edges.map((edge, index): Edge => ({
    id: `${index}:${edge.source}:${edge.target}`,
    source: edge.source,
    target: edge.target,
    markerEnd: { type: MarkerType.ArrowClosed, width: 13, height: 13 },
    className: "vault-edge vault-edge-link",
  }));

  return { nodes, edges };
}

export function VaultGraph({ files, activePath, openPaths, onOpenFile }: VaultGraphProps) {
  const [depth, setDepth] = useState<1 | 2>(1);
  const rootPath = activePath && files.some((file) => file.path === activePath)
    ? activePath
    : getDefaultPath(files);
  const graph = useMemo(
    () => rootPath ? buildGraph(files, rootPath, depth, openPaths) : { nodes: [], edges: [] },
    [depth, files, openPaths, rootPath],
  );

  const handleNodeClick: NodeMouseHandler<VaultNode> = (_event, node) => {
    onOpenFile(node.data.path);
  };

  return (
    <div className="vault-graph-shell">
      <div className="vault-graph-toolbar" aria-label="Knowledge map controls">
        <div>
          <button type="button" onClick={() => setDepth(1)} aria-pressed={depth === 1}>Direct links</button>
          <button type="button" onClick={() => setDepth(2)} aria-pressed={depth === 2}>Two steps</button>
        </div>
        <span>{graph.nodes.length} files · {graph.edges.length} admitted links</span>
      </div>
      <div className="vault-graph" aria-label="Interactive map of admitted Obsidian file links">
        <ReactFlow<VaultNode>
          nodes={graph.nodes}
          edges={graph.edges}
          onNodeClick={handleNodeClick}
          nodesDraggable={false}
          nodesConnectable={false}
          fitView
          fitViewOptions={{ padding: 0.2, maxZoom: 1.2 }}
          minZoom={0.62}
          maxZoom={1.8}
          deleteKeyCode={null}
        >
          <Background variant={BackgroundVariant.Dots} gap={22} size={1} color="#c5d3e3" />
          <Controls showInteractive={false} />
        </ReactFlow>
      </div>
    </div>
  );
}
