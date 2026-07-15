import type { Metadata } from "next";
import type { JSX } from "react";
import Link from "next/link";
import { PageHeader } from "@/components/page-header";
import { ResearchSearch } from "@/components/research-search";
import { VaultGraph } from "@/components/vault-graph";
import { researchFileHref } from "@/lib/content";
import { getKnowledgeCatalog, getKnowledgeFile, getKnowledgeSummary } from "@/lib/knowledge";
import type { KnowledgeFileSummary } from "@/lib/types";

export const metadata: Metadata = { title: "Knowledge map" };

interface KnowledgePageProps {
  searchParams: Promise<{ file?: string | string[] }>;
}

function groupedFiles(files: KnowledgeFileSummary[]): [string, KnowledgeFileSummary[]][] {
  const groups = new Map<string, KnowledgeFileSummary[]>();
  for (const file of files) {
    const current = groups.get(file.folder) ?? [];
    current.push(file);
    groups.set(file.folder, current);
  }
  return [...groups.entries()].sort((left, right) => left[0].localeCompare(right[0]));
}

export default async function KnowledgePage({ searchParams }: KnowledgePageProps): Promise<JSX.Element> {
  const summary = getKnowledgeSummary();
  const files = getKnowledgeCatalog();
  const fileParam = (await searchParams).file;
  const requestedPath = typeof fileParam === "string" ? fileParam : null;
  const fallbackPath = "06_Research/Market Evidence and Source Map.md";
  const selectedFile = getKnowledgeFile(requestedPath ?? fallbackPath);
  const invalidRequest = fileParam !== undefined && selectedFile === null;

  return (
    <div className="focused-page">
      <PageHeader
        eyebrow="Knowledge map"
        title="Every research page, connected to its source."
        description="Search the admitted evidence, follow its connections, and read the full indexed document without exposing arbitrary filesystem paths."
        meta={<><span>Admitted corpus</span><strong>{summary.sourceFiles} pages</strong><small>{summary.chunks} indexed sections</small></>}
      />

      <ResearchSearch />

      <section className="focus-section" aria-labelledby="map-title">
        <div className="focus-heading">
          <div><h2 id="map-title">See how company context connects to source evidence</h2></div>
          <p>Choose a folder, then a page. The full document opens below and the URL remains shareable.</p>
        </div>
        <VaultGraph files={files} />
      </section>

      <section className="focus-section document-reader" aria-labelledby="document-title">
        {invalidRequest ? (
          <div className="document-not-found" role="alert">
            <p className="focus-label">Safe boundary</p>
            <h2 id="document-title">Document not found in the admitted corpus</h2>
            <p>The requested path was rejected. Only files committed to the public-clean research index can be opened.</p>
            <Link href={researchFileHref(fallbackPath)}>Open the market evidence map</Link>
          </div>
        ) : selectedFile ? (
          <>
            <header className="document-header">
              <div><p className="focus-label">Full source document</p><h2 id="document-title">{selectedFile.title}</h2><p>{selectedFile.path}</p></div>
              <dl><div><dt>Layer</dt><dd>{selectedFile.primaryLayer.replaceAll("-", " ")}</dd></div><div><dt>Sections</dt><dd>{selectedFile.sectionCount}</dd></div><div><dt>Words</dt><dd>{selectedFile.wordCount.toLocaleString("en-US")}</dd></div></dl>
            </header>
            <div className="document-sections">
              {selectedFile.sections.map((section, index) => (
                <details key={section.id} open={index === 0}>
                  <summary><span>{section.section}</span><small>{section.evidenceStatus.replaceAll("-", " ")}</small></summary>
                  <div className="document-text">{section.text}</div>
                </details>
              ))}
            </div>
          </>
        ) : null}
      </section>

      <section className="focus-section document-index" aria-labelledby="index-title">
        <div className="focus-heading">
          <div><h2 id="index-title">Browse all {files.length} pages</h2></div>
          <p>The list mirrors the graph for keyboard, screen reader, and small-screen access.</p>
        </div>
        <div className="folder-index">
          {groupedFiles(files).map(([folder, folderFiles]) => (
            <details key={folder}>
              <summary><span>{folder.replaceAll("_", " ")}</span><small>{folderFiles.length} pages</small></summary>
              <ul>{folderFiles.map((file) => <li key={file.path}><Link href={researchFileHref(file.path)}>{file.title}<small>{file.primaryLayer.replaceAll("-", " ")}</small></Link></li>)}</ul>
            </details>
          ))}
        </div>
      </section>
    </div>
  );
}
