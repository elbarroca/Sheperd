import { describe, expect, it } from "vitest";
import dashboard from "../generated/dashboard-data.json";
import knowledge from "../generated/knowledge-index.json";

describe("generated founder intelligence", () => {
  it("preserves the admitted evidence and blocker counts", () => {
    expect(dashboard.sources).toHaveLength(42);
    expect(dashboard.blockers).toHaveLength(12);
    expect(dashboard.blockers.every((row) => row.current_state === "blocked")).toBe(true);
  });

  it("keeps every founder action traceable and bounded", () => {
    const admittedPaths = new Set(knowledge.files.map((file) => file.path));
    const requiredFields = [
      "owner",
      "approver",
      "eligibility",
      "outcome_event",
      "quality_metric",
      "continue_threshold",
      "stop_threshold",
      "canonical_source",
    ] as const;

    expect(dashboard.experiments).toHaveLength(8);
    expect(dashboard.experiments.every((row) => requiredFields.every((field) => row[field].trim().length > 0))).toBe(true);
    expect(dashboard.experiments.every((row) => admittedPaths.has(row.canonical_source))).toBe(true);
    expect(dashboard.experiments.find((row) => row.experiment_id === "EXP-001")).toMatchObject({
      owner: "Michael",
      approver: "Avi",
      execution_state: "prepare-now",
    });
  });

  it("excludes the public website from the admitted knowledge corpus", () => {
    expect(knowledge.sourceFiles).toBeGreaterThanOrEqual(80);
    expect(knowledge.files).toHaveLength(knowledge.sourceFiles);
    expect(knowledge.chunks.length).toBeGreaterThanOrEqual(300);
    expect(knowledge.chunks.some((chunk) => chunk.path.startsWith("website/"))).toBe(false);
  });

  it("publishes the complete 16-week proposal with its evidence boundary", () => {
    const sourcePath = "10_Sources/Source - 16 Week Engagement Plan.md";
    const manifest = knowledge.files.find((file) => file.path === sourcePath);
    const planChunks = knowledge.chunks.filter((chunk) => chunk.path === sourcePath);
    const sections = new Set(planChunks.map((chunk) => chunk.section));
    const text = planChunks.map((chunk) => chunk.text).join(" ");

    expect(manifest).toMatchObject({
      evidenceStatus: "internal-proposal",
      confidentiality: "public-clean-copy",
    });
    expect(sections.has("Phase 1: Deep immersion and foundation building (Weeks 1–2)")).toBe(true);
    expect(sections.has("Phase 2: Gradual market activation and learning by doing (Weeks 3–12)")).toBe(true);
    expect(sections.has("Phase 3: Ownership and scale readiness (Weeks 13–16)")).toBe(true);
    expect(sections.has("Engagement principles")).toBe(true);
    expect(sections.has("Next steps")).toBe(true);
    expect(text).toContain("Live Sales Execution");
    expect(text).toContain("not an executed agreement");
  });
});
