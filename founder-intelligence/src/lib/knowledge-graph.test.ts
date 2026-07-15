import { describe, expect, it } from "vitest";
import { buildKnowledgeNeighborhood } from "./knowledge-graph";
import type { KnowledgeFileSummary } from "./types";

function file(path: string, outgoingLinks: string[], incomingLinks: string[]): KnowledgeFileSummary {
  return {
    path,
    title: path,
    folder: "research",
    primaryLayer: "research",
    layers: ["research"],
    evidenceStatuses: ["verified"],
    confidentiality: ["public-clean"],
    tags: [],
    sectionCount: 1,
    wordCount: 10,
    outgoingLinks,
    incomingLinks,
  };
}

const files = [
  file("A.md", ["B.md", "C.md"], ["D.md"]),
  file("B.md", ["D.md"], ["A.md"]),
  file("C.md", [], ["A.md"]),
  file("D.md", ["A.md"], ["B.md"]),
];

describe("knowledge graph", () => {
  it("builds one-hop neighborhoods from outgoing links and backlinks", () => {
    const graph = buildKnowledgeNeighborhood(files, "A.md", 1);

    expect(graph.nodes).toHaveLength(4);
    expect(graph.nodes.find((node) => node.path === "A.md")?.depth).toBe(0);
    expect(graph.edges).toEqual([
      { source: "A.md", target: "B.md" },
      { source: "D.md", target: "A.md" },
      { source: "A.md", target: "C.md" },
    ]);
  });

  it("shows one admitted route per visible file instead of every cross-link", () => {
    const graph = buildKnowledgeNeighborhood(files, "A.md", 2);

    expect(graph.edges).toHaveLength(graph.nodes.length - 1);
    expect(graph.edges).not.toContainEqual({ source: "B.md", target: "D.md" });
  });

  it("rejects unknown roots and honors the file cap", () => {
    expect(buildKnowledgeNeighborhood(files, "missing.md", 2)).toEqual({ nodes: [], edges: [] });
    expect(buildKnowledgeNeighborhood(files, "A.md", 2, 2).nodes).toHaveLength(2);
  });
});
