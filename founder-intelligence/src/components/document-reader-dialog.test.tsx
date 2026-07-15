import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";
import type { KnowledgeFileDetail, KnowledgeFileSummary } from "@/lib/types";
import { DocumentReaderDialog } from "./document-reader-dialog";

const relatedFile: KnowledgeFileSummary = {
  path: "06_Research/Market Evidence and Source Map.md",
  title: "Market Evidence and Source Map",
  folder: "06_Research",
  primaryLayer: "research",
  layers: ["research"],
  evidenceStatuses: ["verified"],
  confidentiality: ["public-clean"],
  tags: [],
  sectionCount: 1,
  wordCount: 12,
  outgoingLinks: [],
  incomingLinks: ["00_System/Knowledge Retrieval Contract.md"],
};

const file: KnowledgeFileDetail = {
  path: "00_System/Knowledge Retrieval Contract.md",
  title: "Knowledge Retrieval Contract",
  folder: "00_System",
  primaryLayer: "research",
  layers: ["research"],
  evidenceStatuses: ["policy"],
  confidentiality: ["internal"],
  tags: [],
  sectionCount: 2,
  wordCount: 24,
  outgoingLinks: [relatedFile.path],
  incomingLinks: [],
  sections: [
    {
      id: "goal",
      section: "Goal",
      layer: "research",
      evidenceStatus: "policy",
      text: "Give humans and AI the smallest trustworthy context pack.",
    },
    {
      id: "rules",
      section: "Hard rules",
      layer: "research",
      evidenceStatus: "policy",
      text: "Claims must not outrun admitted evidence.",
    },
  ],
};

describe("DocumentReaderDialog", () => {
  it("renders complete document text and full admitted relationship paths", () => {
    const markup = renderToStaticMarkup(
      <DocumentReaderDialog
        file={file}
        files={[file, relatedFile]}
        isOpen
        onClose={() => undefined}
        onOpenFile={() => undefined}
      />,
    );

    expect(markup).toContain("Knowledge Retrieval Contract");
    expect(markup).toContain("00_System/Knowledge Retrieval Contract.md");
    expect(markup).toContain("06_Research/Market Evidence and Source Map.md");
    expect(markup).toContain("Give humans and AI the smallest trustworthy context pack.");
    expect(markup).toContain("Claims must not outrun admitted evidence.");
    expect(markup).toContain('aria-modal="true"');
  });
});
