import { describe, expect, it } from "vitest";
import {
  buildKnowledgeCatalog,
  buildKnowledgeFileDetail,
  buildKnowledgeLayerStats,
  findAdmittedKnowledgeFile,
} from "./knowledge-catalog";
import type { KnowledgeChunk, KnowledgeFileManifest } from "./types";

const chunks: KnowledgeChunk[] = [
  {
    id: "one",
    path: "06_Research/source.md",
    title: "Source",
    section: "Claim",
    layer: "research",
    evidenceStatus: "verified",
    confidentiality: "internal",
    tags: ["evidence"],
    text: "A verified research statement.",
    vector: [],
  },
  {
    id: "two",
    path: "06_Research/source.md",
    title: "Source",
    section: "Limit",
    layer: "source",
    evidenceStatus: "mixed",
    confidentiality: "internal",
    tags: ["evidence", "limit"],
    text: "A material limitation remains visible.",
    vector: [],
  },
];

const manifests: KnowledgeFileManifest[] = [
  {
    path: "06_Research/source.md",
    title: "Source",
    layer: "research",
    evidenceStatus: "verified",
    confidentiality: "internal",
    tags: [],
    links: ["06_Research/target.md", "../../outside.md"],
  },
  {
    path: "06_Research/target.md",
    title: "Target",
    layer: "research",
    evidenceStatus: "verified",
    confidentiality: "internal",
    tags: [],
    links: [],
  },
];

describe("knowledge catalog", () => {
  it("rejects paths outside the admitted corpus", () => {
    const catalog = buildKnowledgeCatalog(chunks);
    expect(findAdmittedKnowledgeFile(catalog, "../../.env.local")).toBeNull();
    expect(findAdmittedKnowledgeFile(catalog, "/etc/passwd")).toBeNull();
  });
  it("groups chunks into a deterministic file summary", () => {
    const catalog = buildKnowledgeCatalog(chunks);

    expect(catalog).toHaveLength(1);
    expect(catalog[0]).toMatchObject({
      folder: "06_Research",
      sectionCount: 2,
      primaryLayer: "research",
      evidenceStatuses: ["mixed", "verified"],
      tags: ["evidence", "limit"],
    });
  });

  it("returns complete sections and accurate layer statistics", () => {
    const catalog = buildKnowledgeCatalog(chunks);
    const detail = buildKnowledgeFileDetail(chunks, catalog[0]);
    const stats = buildKnowledgeLayerStats(chunks, catalog);

    expect(detail.sections.map((section) => section.id)).toEqual(["one", "two"]);
    expect(stats).toEqual([
      { layer: "research", files: 1, chunks: 1 },
      { layer: "source", files: 1, chunks: 1 },
    ]);
  });

  it("resolves files only from the admitted catalog", () => {
    const catalog = buildKnowledgeCatalog(chunks);

    expect(catalog.find((file) => file.path === "../../etc/passwd")).toBeUndefined();
    expect(catalog.find((file) => file.path === "/Users/example/private.txt")).toBeUndefined();
  });

  it("derives admitted outgoing links and backlinks", () => {
    const catalog = buildKnowledgeCatalog(chunks, manifests);
    const source = catalog.find((file) => file.path === "06_Research/source.md");
    const target = catalog.find((file) => file.path === "06_Research/target.md");

    expect(source?.outgoingLinks).toEqual(["06_Research/target.md"]);
    expect(target?.incomingLinks).toEqual(["06_Research/source.md"]);
  });
});
