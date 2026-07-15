import { describe, expect, it } from "vitest";
import dashboard from "../generated/dashboard-data.json";
import knowledge from "../generated/knowledge-index.json";

describe("generated founder intelligence", () => {
  it("preserves the admitted evidence and blocker counts", () => {
    expect(dashboard.sources).toHaveLength(42);
    expect(dashboard.blockers).toHaveLength(12);
    expect(dashboard.blockers.every((row) => row.current_state === "blocked")).toBe(true);
  });

  it("excludes the public website from the private knowledge corpus", () => {
    expect(knowledge.sourceFiles).toBeGreaterThanOrEqual(80);
    expect(knowledge.files).toHaveLength(knowledge.sourceFiles);
    expect(knowledge.chunks.length).toBeGreaterThanOrEqual(300);
    expect(knowledge.chunks.some((chunk) => chunk.path.startsWith("website/"))).toBe(false);
  });
});
