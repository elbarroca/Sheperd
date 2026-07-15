import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";
import type { KnowledgeFileDetail } from "@/lib/types";
import { SourceLibrary } from "./source-library";

const file: KnowledgeFileDetail = {
  path: "10_Sources/Source - 16 Week Engagement Plan.md",
  title: "Source - 16 Week Engagement Plan",
  folder: "10_Sources",
  primaryLayer: "source",
  layers: ["source"],
  evidenceStatuses: ["internal-proposal"],
  confidentiality: ["public-clean-copy"],
  tags: ["sheperd/source"],
  sectionCount: 1,
  wordCount: 9,
  sections: [{
    id: "source-section",
    section: "Document status",
    layer: "source",
    evidenceStatus: "internal-proposal",
    text: "Internal proposal — not an executed agreement.",
  }],
};

describe("SourceLibrary", () => {
  it("fails safely when a requested file is not admitted", () => {
    const markup = renderToStaticMarkup(
      <SourceLibrary files={[file]} initialFile={file} requestedFileMissing />,
    );

    expect(markup).toContain("Document not found in the admitted corpus");
    expect(markup).toContain("The evidence library opened its default file instead.");
    expect(markup).toContain("Source - 16 Week Engagement Plan");
  });
});
