"use client";

import { type ChangeEvent, useMemo, useRef, useState } from "react";
import { CopyIcon } from "@phosphor-icons/react/dist/csr/Copy";
import { FileTextIcon } from "@phosphor-icons/react/dist/csr/FileText";
import { FolderOpenIcon } from "@phosphor-icons/react/dist/csr/FolderOpen";
import { MagnifyingGlassIcon } from "@phosphor-icons/react/dist/csr/MagnifyingGlass";
import type { KnowledgeFileDetail, KnowledgeFileSummary, KnowledgeLayer } from "@/lib/types";
import { LayerBadge } from "./layer-badge";

interface SourceLibraryProps {
  files: KnowledgeFileSummary[];
  initialFile: KnowledgeFileDetail;
}

interface FilePayload {
  error?: string;
  file?: KnowledgeFileDetail;
}

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
    && typeof candidate.folder === "string"
    && typeof candidate.primaryLayer === "string"
    && knowledgeLayers.has(candidate.primaryLayer as KnowledgeLayer)
    && typeof candidate.sectionCount === "number"
    && typeof candidate.wordCount === "number"
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

function formatLayer(layer: string): string {
  return layer.replaceAll("-", " ");
}

function formatCount(value: number): string {
  return new Intl.NumberFormat("en-US").format(value);
}

export function SourceLibrary({ files, initialFile }: SourceLibraryProps) {
  const folders = useMemo(() => [...new Set(files.map((file) => file.folder))].sort(), [files]);
  const layers = useMemo(() => [...new Set(files.flatMap((file) => file.layers))].sort(), [files]);
  const [query, setQuery] = useState("");
  const [folder, setFolder] = useState("all");
  const [layer, setLayer] = useState("all");
  const [selectedPath, setSelectedPath] = useState(initialFile.path);
  const [detail, setDetail] = useState<KnowledgeFileDetail>(initialFile);
  const [loadingPath, setLoadingPath] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [copyStatus, setCopyStatus] = useState("Copy source path");
  const cacheRef = useRef(new Map<string, KnowledgeFileDetail>([[initialFile.path, initialFile]]));
  const requestRef = useRef<AbortController | null>(null);

  const filteredFiles = useMemo(() => {
    const normalized = query.trim().toLocaleLowerCase();

    return files.filter((file) => {
      const matchesFolder = folder === "all" || file.folder === folder;
      const matchesLayer = layer === "all" || file.layers.includes(layer as KnowledgeLayer);
      const searchable = [file.path, file.title, file.folder, ...file.tags, ...file.evidenceStatuses]
        .join(" ")
        .toLocaleLowerCase();
      return matchesFolder && matchesLayer && (normalized.length === 0 || searchable.includes(normalized));
    });
  }, [files, folder, layer, query]);

  async function selectFile(path: string): Promise<void> {
    setSelectedPath(path);
    setCopyStatus("Copy source path");
    setError(null);

    const cached = cacheRef.current.get(path);
    if (cached) {
      setDetail(cached);
      return;
    }

    requestRef.current?.abort();
    const controller = new AbortController();
    requestRef.current = controller;
    setLoadingPath(path);

    try {
      const response = await fetch(`/api/files?path=${encodeURIComponent(path)}`, { signal: controller.signal });
      const rawPayload: unknown = await response.json();
      if (!isFilePayload(rawPayload)) throw new Error("The source response was malformed.");
      if (!response.ok || !rawPayload.file) throw new Error(rawPayload.error ?? "Source retrieval failed.");
      cacheRef.current.set(path, rawPayload.file);
      setDetail(rawPayload.file);
    } catch (caughtError) {
      if (caughtError instanceof DOMException && caughtError.name === "AbortError") return;
      setError(caughtError instanceof Error ? caughtError.message : "Source retrieval failed safely.");
    } finally {
      if (requestRef.current === controller) {
        requestRef.current = null;
        setLoadingPath(null);
      }
    }
  }

  async function copyPath(): Promise<void> {
    try {
      await navigator.clipboard.writeText(detail.path);
      setCopyStatus("Path copied");
    } catch {
      setCopyStatus("Copy unavailable");
    }
  }

  function updateQuery(event: ChangeEvent<HTMLInputElement>): void {
    setQuery(event.target.value);
  }

  return (
    <section className="source-library section-block" aria-labelledby="source-library-title">
      <div className="section-heading library-heading">
        <div>
          <p className="eyebrow">Source library</p>
          <h2 id="source-library-title">Open every admitted file without leaving the dashboard</h2>
        </div>
        <p>Filter the full corpus, select a file, and inspect each indexed section with its evidence state still attached.</p>
      </div>

      <div className="library-toolbar">
        <label className="library-search" htmlFor="source-filter">
          <MagnifyingGlassIcon aria-hidden="true" size={18} />
          <span className="sr-only">Filter source files</span>
          <input
            id="source-filter"
            type="search"
            value={query}
            onChange={updateQuery}
            placeholder="Filter by file, tag, or evidence state"
          />
        </label>
        <label>
          <span>Folder</span>
          <select value={folder} onChange={(event) => setFolder(event.target.value)}>
            <option value="all">All folders</option>
            {folders.map((item) => <option key={item} value={item}>{item}</option>)}
          </select>
        </label>
        <label>
          <span>Layer</span>
          <select value={layer} onChange={(event) => setLayer(event.target.value)}>
            <option value="all">All layers</option>
            {layers.map((item) => <option key={item} value={item}>{formatLayer(item)}</option>)}
          </select>
        </label>
        <div className="library-result-count" role="status">
          <strong>{filteredFiles.length}</strong>
          <span>of {files.length} files</span>
        </div>
      </div>

      <div className="library-workspace">
        <div className="file-index" aria-label="Research files">
          {filteredFiles.length === 0 ? (
            <div className="empty-state">
              <strong>No files match these filters</strong>
              <span>Clear the search or select a broader folder and layer.</span>
            </div>
          ) : filteredFiles.map((file) => (
            <button
              key={file.path}
              type="button"
              className="file-row"
              aria-pressed={selectedPath === file.path}
              onClick={() => void selectFile(file.path)}
            >
              <FileTextIcon aria-hidden="true" size={18} weight={selectedPath === file.path ? "fill" : "regular"} />
              <span className="file-row-copy">
                <strong>{file.title}</strong>
                <span>{file.path}</span>
              </span>
              <span className="file-section-count">{file.sectionCount}</span>
            </button>
          ))}
        </div>

        <article className="file-reader" aria-busy={loadingPath !== null}>
          <header className="file-reader-header">
            <div className="file-reader-kicker">
              <FolderOpenIcon aria-hidden="true" size={18} />
              <span>{detail.folder}</span>
              <LayerBadge layer={detail.primaryLayer} />
            </div>
            <h3>{detail.title}</h3>
            <code>{detail.path}</code>
            <dl>
              <div><dt>Sections</dt><dd>{detail.sectionCount}</dd></div>
              <div><dt>Indexed words</dt><dd>{formatCount(detail.wordCount)}</dd></div>
              <div><dt>Evidence states</dt><dd>{detail.evidenceStatuses.length}</dd></div>
            </dl>
            <button type="button" className="copy-path-button" onClick={() => void copyPath()}>
              <CopyIcon aria-hidden="true" size={16} />
              {copyStatus}
            </button>
          </header>

          {error ? <p className="file-error" role="alert">{error}</p> : null}
          {loadingPath ? <div className="file-loading" role="status"><span aria-hidden="true" />Loading source sections</div> : (
            <div className="file-sections">
              {detail.sections.length === 0 ? (
                <div className="empty-file-state">
                  <strong>No indexable section text</strong>
                  <p>This file is admitted to the corpus, but its current template body does not meet the minimum retrieval length. The source path remains visible and traceable.</p>
                </div>
              ) : detail.sections.map((section, index) => (
                <details key={section.id} open={index === 0}>
                  <summary>
                    <span>{String(index + 1).padStart(2, "0")}</span>
                    <strong>{section.section}</strong>
                    <em>{formatLayer(section.evidenceStatus)}</em>
                  </summary>
                  <div className="file-section-body">
                    <div><LayerBadge layer={section.layer} /><span>{formatLayer(section.evidenceStatus)}</span></div>
                    <p>{section.text}</p>
                  </div>
                </details>
              ))}
            </div>
          )}
        </article>
      </div>
    </section>
  );
}
