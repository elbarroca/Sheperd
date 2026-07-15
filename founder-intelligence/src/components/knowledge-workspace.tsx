"use client";

import { type JSX, type ReactNode, useMemo, useRef, useState } from "react";
import { usePathname, useRouter } from "next/navigation";
import { XIcon } from "@phosphor-icons/react/dist/csr/X";
import type { KnowledgeFileDetail, KnowledgeFileSummary, KnowledgeLayer } from "@/lib/types";
import { DocumentReaderDialog } from "./document-reader-dialog";
import { VaultGraph } from "./vault-graph";

interface KnowledgeWorkspaceProps {
  files: KnowledgeFileSummary[];
  initialFiles: KnowledgeFileDetail[];
  initialActivePath: string;
  initialReaderOpen?: boolean;
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

export function KnowledgeWorkspace({
  files,
  initialFiles,
  initialActivePath,
  initialReaderOpen = false,
  invalidRequest = false,
  searchSlot,
}: KnowledgeWorkspaceProps): JSX.Element {
  const router = useRouter();
  const pathname = usePathname();
  const [openFiles, setOpenFiles] = useState(initialFiles);
  const [activePath, setActivePath] = useState<string | null>(initialActivePath);
  const [readerOpen, setReaderOpen] = useState(initialReaderOpen);
  const [loadingPath, setLoadingPath] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(
    invalidRequest ? "One or more requested documents were not part of the admitted corpus." : null,
  );
  const cacheRef = useRef(new Map(initialFiles.map((file) => [file.path, file])));
  const grouped = useMemo(() => groupFiles(files), [files]);
  const activeFile = openFiles.find((file) => file.path === activePath) ?? null;

  function syncUrl(nextFiles: KnowledgeFileDetail[], nextActivePath: string | null): void {
    const params = new URLSearchParams();
    nextFiles.forEach((file) => params.append("file", file.path));
    if (nextActivePath) params.set("active", nextActivePath);
    const query = params.toString();
    router.replace(query ? `${pathname}?${query}` : pathname, { scroll: false });
  }

  function activateFile(path: string): void {
    setActivePath(path);
    setReaderOpen(true);
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
      setReaderOpen(true);
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
    if (!nextActivePath) setReaderOpen(false);
    setError(null);
    syncUrl(nextFiles, nextActivePath);
  }

  return (
    <>
      <section className="focus-section" aria-labelledby="map-title">
        <div className="focus-heading">
          <div><h2 id="map-title">Follow the links between files</h2></div>
          <p>Select a file to open its full text. The map shows focused routes, while the reader preserves every admitted link and source path.</p>
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
          <div><h2 id="dock-title">Open documents</h2><p>Select any document to read it in a focused window.</p></div>
          <strong>{openFiles.length} / {MAX_OPEN_FILES} open</strong>
        </header>

        {openFiles.length > 0 ? (
          <ul className="document-shelf" aria-label="Open research documents">
            {openFiles.map((file, index) => (
              <li key={file.path} className="document-shelf-item" data-active={file.path === activePath && readerOpen}>
                <button
                  type="button"
                  className="document-shelf-open"
                  onClick={() => activateFile(file.path)}
                >
                  <small>Document {index + 1}</small>
                  <strong>{file.title}</strong>
                  <code>{file.path}</code>
                </button>
                <button type="button" className="document-shelf-close" onClick={() => closeFile(file.path)} aria-label={`Remove ${file.title} from open documents`}>
                  <XIcon size={17} aria-hidden="true" />
                </button>
              </li>
            ))}
          </ul>
        ) : null}

        {error ? <p className="knowledge-dock-error" role="alert">{error}</p> : null}
        {loadingPath ? <p className="knowledge-dock-loading" role="status">Opening document…</p> : null}

        {openFiles.length === 0 ? (
          <div className="document-dock-empty">
            <strong>No documents open</strong>
            <p>Select a graph node or use the file index below.</p>
          </div>
        ) : null}
      </section>

      <DocumentReaderDialog
        error={error}
        file={activeFile}
        files={files}
        isOpen={readerOpen && activeFile !== null}
        loadingPath={loadingPath}
        onClose={() => setReaderOpen(false)}
        onOpenFile={(path) => void openFile(path)}
      />

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
