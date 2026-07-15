"use client";

import { type JSX, type ReactNode, useMemo, useRef, useState } from "react";
import { usePathname, useRouter } from "next/navigation";
import { XIcon } from "@phosphor-icons/react/dist/csr/X";
import type { KnowledgeFileDetail, KnowledgeFileSummary, KnowledgeLayer } from "@/lib/types";
import { VaultGraph } from "./vault-graph";

interface KnowledgeWorkspaceProps {
  files: KnowledgeFileSummary[];
  initialFiles: KnowledgeFileDetail[];
  initialActivePath: string;
  invalidRequest?: boolean;
  searchSlot?: ReactNode;
}

interface FilePayload {
  error?: string;
  file?: KnowledgeFileDetail;
}

const MAX_OPEN_FILES = 4;
const knowledgeLayers = new Set<KnowledgeLayer>([
  "founder-context",
  "operating-system",
  "research",
  "ricardo-interpretation",
  "source",
  "structured-data",
  "template",
]);

function isFileDetail(value: unknown): value is KnowledgeFileDetail {
  if (typeof value !== "object" || value === null) return false;
  const candidate = value as Record<string, unknown>;
  return typeof candidate.path === "string"
    && typeof candidate.title === "string"
    && typeof candidate.primaryLayer === "string"
    && knowledgeLayers.has(candidate.primaryLayer as KnowledgeLayer)
    && typeof candidate.sectionCount === "number"
    && typeof candidate.wordCount === "number"
    && Array.isArray(candidate.outgoingLinks)
    && candidate.outgoingLinks.every((path) => typeof path === "string")
    && Array.isArray(candidate.incomingLinks)
    && candidate.incomingLinks.every((path) => typeof path === "string")
    && Array.isArray(candidate.sections)
    && candidate.sections.every((section) => {
      if (typeof section !== "object" || section === null) return false;
      const item = section as Record<string, unknown>;
      return typeof item.id === "string"
        && typeof item.section === "string"
        && typeof item.text === "string"
        && typeof item.evidenceStatus === "string"
        && typeof item.layer === "string"
        && knowledgeLayers.has(item.layer as KnowledgeLayer);
    });
}

function isFilePayload(value: unknown): value is FilePayload {
  if (typeof value !== "object" || value === null) return false;
  const candidate = value as Record<string, unknown>;
  return (candidate.error === undefined || typeof candidate.error === "string")
    && (candidate.file === undefined || isFileDetail(candidate.file));
}

function groupFiles(files: KnowledgeFileSummary[]): [string, KnowledgeFileSummary[]][] {
  const groups = new Map<string, KnowledgeFileSummary[]>();
  for (const file of files) groups.set(file.folder, [...(groups.get(file.folder) ?? []), file]);
  return [...groups.entries()].sort((left, right) => left[0].localeCompare(right[0]));
}

function formatLayer(value: string): string {
  return value.replaceAll("-", " ");
}

export function KnowledgeWorkspace({
  files,
  initialFiles,
  initialActivePath,
  invalidRequest = false,
  searchSlot,
}: KnowledgeWorkspaceProps): JSX.Element {
  const router = useRouter();
  const pathname = usePathname();
  const [openFiles, setOpenFiles] = useState(initialFiles);
  const [activePath, setActivePath] = useState<string | null>(initialActivePath);
  const [loadingPath, setLoadingPath] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(
    invalidRequest ? "One or more requested documents were not part of the admitted corpus." : null,
  );
  const cacheRef = useRef(new Map(initialFiles.map((file) => [file.path, file])));
  const fileSummaries = useMemo(() => new Map(files.map((file) => [file.path, file])), [files]);
  const grouped = useMemo(() => groupFiles(files), [files]);
  const activeFile = openFiles.find((file) => file.path === activePath) ?? null;
  const activeSummary = activePath ? fileSummaries.get(activePath) ?? null : null;
  const activeTabIndex = openFiles.findIndex((file) => file.path === activePath);

  function syncUrl(nextFiles: KnowledgeFileDetail[], nextActivePath: string | null): void {
    const params = new URLSearchParams();
    nextFiles.forEach((file) => params.append("file", file.path));
    if (nextActivePath) params.set("active", nextActivePath);
    const query = params.toString();
    router.replace(query ? `${pathname}?${query}` : pathname, { scroll: false });
  }

  function activateFile(path: string): void {
    setActivePath(path);
    setError(null);
    syncUrl(openFiles, path);
  }

  async function openFile(path: string): Promise<void> {
    const alreadyOpen = openFiles.find((file) => file.path === path);
    if (alreadyOpen) {
      activateFile(path);
      return;
    }
    if (openFiles.length >= MAX_OPEN_FILES) {
      setError("Four documents are already open. Close one before opening another.");
      return;
    }

    setLoadingPath(path);
    setError(null);
    try {
      const cached = cacheRef.current.get(path);
      let nextFile = cached;
      if (!nextFile) {
        const response = await fetch(`/api/files?path=${encodeURIComponent(path)}`);
        const payload: unknown = await response.json();
        if (!isFilePayload(payload)) throw new Error("The document response was malformed.");
        if (!response.ok || !payload.file) throw new Error(payload.error ?? "The document could not be opened.");
        nextFile = payload.file;
        cacheRef.current.set(path, nextFile);
      }
      const nextFiles = [...openFiles, nextFile];
      setOpenFiles(nextFiles);
      setActivePath(path);
      syncUrl(nextFiles, path);
    } catch (caughtError) {
      setError(caughtError instanceof Error ? caughtError.message : "The document could not be opened safely.");
    } finally {
      setLoadingPath(null);
    }
  }

  function closeFile(path: string): void {
    const closingIndex = openFiles.findIndex((file) => file.path === path);
    const nextFiles = openFiles.filter((file) => file.path !== path);
    const nextActivePath = path === activePath
      ? nextFiles[Math.min(closingIndex, nextFiles.length - 1)]?.path ?? null
      : activePath;
    setOpenFiles(nextFiles);
    setActivePath(nextActivePath);
    setError(null);
    syncUrl(nextFiles, nextActivePath);
  }

  function relationshipList(paths: string[], emptyLabel: string): JSX.Element {
    if (paths.length === 0) return <p>{emptyLabel}</p>;
    return (
      <ul>
        {paths.map((path) => {
          const file = fileSummaries.get(path);
          return (
            <li key={path}>
              <button type="button" onClick={() => void openFile(path)}>
                <strong>{file?.title ?? path}</strong>
                <small>{file?.folder.replaceAll("_", " ") ?? "Admitted source"}</small>
              </button>
            </li>
          );
        })}
      </ul>
    );
  }

  return (
    <>
      <section className="focus-section" aria-labelledby="map-title">
        <div className="focus-heading">
          <div><h2 id="map-title">Follow the links between files</h2></div>
          <p>Every line is an admitted Obsidian link. Select a file to open it without losing the documents already in your dock.</p>
        </div>
        <VaultGraph
          files={files}
          activePath={activePath}
          openPaths={openFiles.map((file) => file.path)}
          onOpenFile={(path) => void openFile(path)}
        />
      </section>

      <section className="focus-section knowledge-dock" aria-labelledby="dock-title">
        <header className="knowledge-dock-heading">
          <div><h2 id="dock-title">Document dock</h2><p>Open, switch, and close up to four source documents.</p></div>
          <strong>{openFiles.length} / {MAX_OPEN_FILES} open</strong>
        </header>

        {openFiles.length > 0 ? (
          <div className="document-tabs" role="tablist" aria-label="Open research documents">
            {openFiles.map((file, index) => (
              <div key={file.path} className="document-tab" data-active={file.path === activePath}>
                <button
                  type="button"
                  role="tab"
                  id={`document-tab-${index + 1}`}
                  aria-selected={file.path === activePath}
                  aria-controls="active-document-panel"
                  onClick={() => activateFile(file.path)}
                >
                  <small>Page {index + 1}</small>
                  <span>{file.title}</span>
                </button>
                <button type="button" className="document-tab-close" onClick={() => closeFile(file.path)} aria-label={`Close ${file.title}`}>
                  <XIcon size={15} aria-hidden="true" />
                </button>
              </div>
            ))}
          </div>
        ) : null}

        {error ? <p className="knowledge-dock-error" role="alert">{error}</p> : null}
        {loadingPath ? <p className="knowledge-dock-loading" role="status">Opening document…</p> : null}

        {activeFile && activeSummary ? (
          <article
            id="active-document-panel"
            className="document-reader"
            role="tabpanel"
            aria-labelledby={activeTabIndex >= 0 ? `document-tab-${activeTabIndex + 1}` : undefined}
          >
            <header className="document-header">
              <div><p className="focus-label">Active source</p><h3>{activeFile.title}</h3><p>{activeFile.path}</p></div>
              <dl>
                <div><dt>Layer</dt><dd>{formatLayer(activeFile.primaryLayer)}</dd></div>
                <div><dt>Sections</dt><dd>{activeFile.sectionCount}</dd></div>
                <div><dt>Words</dt><dd>{activeFile.wordCount.toLocaleString("en-US")}</dd></div>
              </dl>
            </header>
            <div className="document-relationships" aria-label="Document relationships">
              <details open>
                <summary><span>Links to other files</span><small>{activeSummary.outgoingLinks.length}</small></summary>
                {relationshipList(activeSummary.outgoingLinks, "This file has no admitted outgoing links.")}
              </details>
              <details>
                <summary><span>Linked from other files</span><small>{activeSummary.incomingLinks.length}</small></summary>
                {relationshipList(activeSummary.incomingLinks, "No admitted file links back to this document.")}
              </details>
            </div>
            <div className="document-sections">
              {activeFile.sections.length > 0 ? activeFile.sections.map((section, index) => (
                <details key={section.id} open={index === 0}>
                  <summary><span>{section.section}</span><small>{formatLayer(section.evidenceStatus)}</small></summary>
                  <div className="document-text">{section.text}</div>
                </details>
              )) : (
                <div className="document-empty"><strong>No indexable section text</strong><p>The file remains admitted and connected, but its body has no retrievable section yet.</p></div>
              )}
            </div>
          </article>
        ) : (
          <div className="document-dock-empty">
            <strong>No documents open</strong>
            <p>Select a graph node or use the file index below.</p>
          </div>
        )}
      </section>

      {searchSlot}

      <section className="focus-section document-index" aria-labelledby="index-title">
        <div className="focus-heading">
          <div><h2 id="index-title">Browse all {files.length} pages</h2></div>
          <p>This semantic index mirrors the graph for keyboard, screen reader, and small-screen access.</p>
        </div>
        <div className="folder-index">
          {grouped.map(([folder, folderFiles]) => (
            <details key={folder}>
              <summary><span>{folder.replaceAll("_", " ")}</span><small>{folderFiles.length} pages</small></summary>
              <ul>
                {folderFiles.map((file) => (
                  <li key={file.path}>
                    <button type="button" onClick={() => void openFile(file.path)}>
                      <span>{file.title}</span>
                      <small>{file.outgoingLinks.length + file.incomingLinks.length} connections</small>
                    </button>
                  </li>
                ))}
              </ul>
            </details>
          ))}
        </div>
      </section>
    </>
  );
}
