import type { Metadata } from "next";
import type { JSX } from "react";
import { KnowledgeWorkspace } from "@/components/knowledge-workspace";
import { PageHeader } from "@/components/page-header";
import { ResearchSearch } from "@/components/research-search";
import { getKnowledgeCatalog, getKnowledgeFile, getKnowledgeSummary } from "@/lib/knowledge";
import type { KnowledgeFileDetail } from "@/lib/types";

export const metadata: Metadata = { title: "Knowledge map" };

interface KnowledgePageProps {
  searchParams: Promise<{ active?: string | string[]; file?: string | string[] }>;
}

const FALLBACK_PATH = "06_Research/Market Evidence and Source Map.md";
const MAX_OPEN_FILES = 4;

export default async function KnowledgePage({ searchParams }: KnowledgePageProps): Promise<JSX.Element> {
  const summary = getKnowledgeSummary();
  const files = getKnowledgeCatalog();
  const params = await searchParams;
  const fileParams = params.file === undefined ? [] : Array.isArray(params.file) ? params.file : [params.file];
  const requestedPaths = [...new Set(fileParams)].slice(0, MAX_OPEN_FILES);
  const requestedFiles = requestedPaths.map((path) => getKnowledgeFile(path));
  const validFiles = requestedFiles.filter((file): file is KnowledgeFileDetail => file !== null);
  const fallbackFile = getKnowledgeFile(FALLBACK_PATH);
  if (!fallbackFile) throw new Error("The canonical market evidence map is missing from the admitted corpus.");
  const initialFiles = validFiles.length > 0 ? validFiles : [fallbackFile];
  const activeParam = typeof params.active === "string" ? params.active : null;
  const initialActivePath = activeParam && initialFiles.some((file) => file.path === activeParam)
    ? activeParam
    : initialFiles[0].path;
  const invalidRequest = fileParams.length > MAX_OPEN_FILES || requestedFiles.some((file) => file === null);
  const admittedLinks = files.reduce((sum, file) => sum + file.outgoingLinks.length, 0);

  return (
    <div className="focused-page">
      <PageHeader
        eyebrow="Knowledge map"
        title="Open the evidence. Keep the context."
        description="Trace real links between admitted files, keep up to four documents open, and share the exact workspace state."
        meta={<><span>Admitted graph</span><strong>{summary.sourceFiles} pages</strong><small>{admittedLinks} file links</small></>}
      />

      <KnowledgeWorkspace
        files={files}
        initialFiles={initialFiles}
        initialActivePath={initialActivePath}
        initialReaderOpen={validFiles.length > 0}
        invalidRequest={invalidRequest}
        searchSlot={<ResearchSearch />}
      />
    </div>
  );
}
