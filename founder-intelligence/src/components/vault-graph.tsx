"use client";

import type { ReactNode } from "react";
import { useMemo, useState } from "react";
import { useRouter } from "next/navigation";
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
import { researchFileHref } from "@/lib/content";
import type { KnowledgeFileSummary } from "@/lib/types";

type VaultNodeKind = "root" | "folder" | "file";
type VaultNodeData = {
  label: ReactNode;
  kind: VaultNodeKind;
  folder?: string;
  path?: string;
};
type VaultNode = Node<VaultNodeData>;

interface FolderGroup {
  folder: string;
  files: KnowledgeFileSummary[];
}

function groupFiles(files: KnowledgeFileSummary[]): FolderGroup[] {
  const grouped = new Map<string, KnowledgeFileSummary[]>();
  for (const file of files) {
    const current = grouped.get(file.folder) ?? [];
    current.push(file);
    grouped.set(file.folder, current);
  }
  return [...grouped.entries()]
    .map(([folder, folderFiles]) => ({ folder, files: folderFiles }))
    .sort((left, right) => left.folder.localeCompare(right.folder));
}

function nodeLabel(title: string, detail: string): ReactNode {
  return <span><strong>{title}</strong><small>{detail}</small></span>;
}

function buildFolderView(groups: FolderGroup[]): { nodes: VaultNode[]; edges: Edge[] } {
  const nodes: VaultNode[] = groups.map((group, index) => ({
    id: `folder:${group.folder}`,
    position: { x: 420, y: index * 96 },
    data: { label: nodeLabel(group.folder.replaceAll("_", " "), `${group.files.length} documents`), kind: "folder", folder: group.folder },
    className: "vault-node vault-node-folder",
  }));
  nodes.unshift({
    id: "vault-root",
    position: { x: 0, y: Math.max(0, ((groups.length - 1) * 96) / 2) },
    data: { label: nodeLabel("SheperD vault", `${groups.reduce((sum, group) => sum + group.files.length, 0)} documents`), kind: "root" },
    className: "vault-node vault-node-root",
  });
  const edges = groups.map((group) => ({
    id: `root:${group.folder}`,
    source: "vault-root",
    target: `folder:${group.folder}`,
    markerEnd: { type: MarkerType.ArrowClosed },
    className: "vault-edge",
  }));
  return { nodes, edges };
}

function buildDocumentView(groups: FolderGroup[], activeFolder: string | "all"): { nodes: VaultNode[]; edges: Edge[] } {
  const visibleGroups = activeFolder === "all" ? groups : groups.filter((group) => group.folder === activeFolder);
  const nodes: VaultNode[] = [];
  const edges: Edge[] = [];
  let cursorY = 0;

  for (const group of visibleGroups) {
    const rowCount = Math.max(1, Math.ceil(group.files.length / 2));
    const blockHeight = rowCount * 88;
    const folderId = `folder:${group.folder}`;
    nodes.push({
      id: folderId,
      position: { x: 340, y: cursorY + blockHeight / 2 - 34 },
      data: { label: nodeLabel(group.folder.replaceAll("_", " "), `${group.files.length} documents`), kind: "folder", folder: group.folder },
      className: "vault-node vault-node-folder",
    });
    edges.push({
      id: `root:${group.folder}`,
      source: "vault-root",
      target: folderId,
      markerEnd: { type: MarkerType.ArrowClosed },
      className: "vault-edge",
    });

    group.files.forEach((file, index) => {
      const fileId = `file:${file.path}`;
      nodes.push({
        id: fileId,
        position: { x: 740 + (index % 2) * 320, y: cursorY + Math.floor(index / 2) * 88 },
        data: { label: nodeLabel(file.title, file.primaryLayer.replaceAll("-", " ")), kind: "file", path: file.path },
        className: "vault-node vault-node-file",
      });
      edges.push({
        id: `${folderId}:${fileId}`,
        source: folderId,
        target: fileId,
        className: "vault-edge vault-edge-file",
      });
    });
    cursorY += blockHeight + 88;
  }

  nodes.unshift({
    id: "vault-root",
    position: { x: 0, y: Math.max(0, cursorY / 2 - 70) },
    data: { label: nodeLabel("SheperD vault", `${visibleGroups.reduce((sum, group) => sum + group.files.length, 0)} shown`), kind: "root" },
    className: "vault-node vault-node-root",
  });
  return { nodes, edges };
}

export function VaultGraph({ files }: { files: KnowledgeFileSummary[] }) {
  const router = useRouter();
  const groups = useMemo(() => groupFiles(files), [files]);
  const [view, setView] = useState<string | "folders" | "all">("folders");
  const graph = useMemo(
    () => view === "folders" ? buildFolderView(groups) : buildDocumentView(groups, view),
    [groups, view],
  );

  const handleNodeClick: NodeMouseHandler<VaultNode> = (_event, node) => {
    if (node.data.kind === "folder" && node.data.folder) {
      setView(node.data.folder);
      return;
    }
    if (node.data.kind === "file" && node.data.path) {
      router.push(researchFileHref(node.data.path));
    }
  };

  return (
    <div className="vault-graph-shell">
      <div className="vault-graph-toolbar" aria-label="Knowledge map controls">
        <button type="button" onClick={() => setView("folders")} aria-pressed={view === "folders"}>Folders</button>
        <button type="button" onClick={() => setView("all")} aria-pressed={view === "all"}>Show all {files.length} pages</button>
        <span>{view === "folders" ? "Choose a folder to reveal its pages." : view === "all" ? "Every admitted page is visible." : `Showing ${view.replaceAll("_", " ")}.`}</span>
      </div>
      <div className="vault-graph" aria-label="Interactive map of admitted SheperD vault documents">
        <ReactFlow<VaultNode>
          nodes={graph.nodes}
          edges={graph.edges}
          onNodeClick={handleNodeClick}
          nodesDraggable={false}
          nodesConnectable={false}
          fitView
          fitViewOptions={{ padding: 0.18, maxZoom: 1.15 }}
          minZoom={0.12}
          maxZoom={1.6}
          deleteKeyCode={null}
        >
          <Background variant={BackgroundVariant.Dots} gap={22} size={1} color="#c5d3e3" />
          <Controls showInteractive={false} />
        </ReactFlow>
      </div>
    </div>
  );
}
