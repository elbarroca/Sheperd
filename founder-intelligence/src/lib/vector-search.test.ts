import { describe, expect, it } from "vitest";
import { searchIndex } from "./vector-search";
import type { KnowledgeIndex } from "./types";

const index: KnowledgeIndex = {
  contractVersion: 1,
  method: "deterministic-local-tfidf-sparse-v1",
  boundary: "test",
  sourceDate: "2026-07-15",
  sourceFiles: 2,
  vocabulary: ["authority", "claims"],
  idf: [1, 1],
  chunks: [
    { id: "one", path: "authority.md", title: "Authority", section: "Gate", layer: "research", evidenceStatus: "mixed", confidentiality: "internal", tags: [], text: "Authority is blocked", vector: [[0, 1]] },
    { id: "two", path: "claims.md", title: "Claims", section: "Gate", layer: "research", evidenceStatus: "mixed", confidentiality: "internal", tags: [], text: "Claims are blocked", vector: [[1, 1]] },
  ],
};

describe("searchIndex", () => {
  it("ranks the matching evidence section first", () => {
    expect(searchIndex(index, "authority")[0].id).toBe("one");
  });

  it("fails closed on short and unknown queries", () => {
    expect(searchIndex(index, "a")).toEqual([]);
    expect(searchIndex(index, "unmapped vocabulary")).toEqual([]);
  });
});
