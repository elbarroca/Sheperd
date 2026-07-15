"use client";

import { type JSX, useEffect, useMemo, useRef } from "react";
import { XIcon } from "@phosphor-icons/react/dist/csr/X";
import type { KnowledgeFileDetail, KnowledgeFileSummary } from "@/lib/types";

interface DocumentReaderDialogProps {
  error?: string | null;
  file: KnowledgeFileDetail | null;
  files: KnowledgeFileSummary[];
  isOpen: boolean;
  loadingPath?: string | null;
  onClose: () => void;
  onOpenFile: (path: string) => void;
}

function formatLayer(value: string): string {
  return value.replaceAll("-", " ");
}

export function DocumentReaderDialog({
  error = null,
  file,
  files,
  isOpen,
  loadingPath = null,
  onClose,
  onOpenFile,
}: DocumentReaderDialogProps): JSX.Element | null {
  const dialogRef = useRef<HTMLDialogElement>(null);
  const filesByPath = useMemo(() => new Map(files.map((item) => [item.path, item])), [files]);

  useEffect(() => {
    const dialog = dialogRef.current;
    if (!dialog) return;

    if (isOpen && !dialog.open) dialog.showModal();
    if (!isOpen && dialog.open) dialog.close();
    document.body.classList.toggle("document-dialog-open", isOpen);

    return () => document.body.classList.remove("document-dialog-open");
  }, [isOpen]);

  useEffect(() => {
    if (!isOpen) return;

    function closeOnEscape(event: KeyboardEvent): void {
      if (event.key !== "Escape") return;
      event.preventDefault();
      onClose();
    }

    document.addEventListener("keydown", closeOnEscape);
    return () => document.removeEventListener("keydown", closeOnEscape);
  }, [isOpen, onClose]);

  if (!file) return null;

  function relationshipList(paths: string[], emptyLabel: string): JSX.Element {
    if (paths.length === 0) return <p className="reader-relationship-empty">{emptyLabel}</p>;

    return (
      <ul>
        {paths.map((path) => {
          const relatedFile = filesByPath.get(path);
          return (
            <li key={path}>
              <button type="button" onClick={() => onOpenFile(path)}>
                <strong>{relatedFile?.title ?? path}</strong>
                <code>{path}</code>
              </button>
            </li>
          );
        })}
      </ul>
    );
  }

  return (
    <dialog
      ref={dialogRef}
      className="document-reader-dialog"
      aria-labelledby="document-reader-title"
      aria-describedby="document-reader-path"
      aria-modal="true"
      onCancel={(event) => {
        event.preventDefault();
        onClose();
      }}
      onClick={(event) => {
        if (event.target === event.currentTarget) onClose();
      }}
    >
      <article className="reader-frame">
        <header className="reader-header">
          <div>
            <p>Source document</p>
            <h2 id="document-reader-title">{file.title}</h2>
            <code id="document-reader-path">{file.path}</code>
          </div>
          <button type="button" className="reader-close" onClick={onClose} aria-label={`Close ${file.title}`}>
            <XIcon size={20} aria-hidden="true" />
          </button>
        </header>

        {error ? <p className="reader-message reader-message-error" role="alert">{error}</p> : null}
        {loadingPath ? <p className="reader-message" role="status">Opening {loadingPath}</p> : null}

        <div className="reader-scroll">
          <div className="reader-layout">
            <aside className="reader-sidebar" aria-label="Document outline">
              <dl>
                <div><dt>Layer</dt><dd>{formatLayer(file.primaryLayer)}</dd></div>
                <div><dt>Sections</dt><dd>{file.sectionCount}</dd></div>
                <div><dt>Words</dt><dd>{file.wordCount.toLocaleString("en-US")}</dd></div>
              </dl>
              {file.sections.length > 0 ? (
                <nav aria-label="Sections in this document">
                  <strong>In this document</strong>
                  <ol>
                    {file.sections.map((section) => (
                      <li key={section.id}><a href={`#document-section-${section.id}`}>{section.section}</a></li>
                    ))}
                  </ol>
                </nav>
              ) : null}
            </aside>

            <div className="reader-main">
              <section className="reader-relationships" aria-labelledby="reader-relationships-title">
                <div className="reader-section-heading">
                  <h3 id="reader-relationships-title">Connected documents</h3>
                  <p>Every item below is an admitted Obsidian link. The full source path stays visible.</p>
                </div>
                <div className="reader-relationship-grid">
                  <details open>
                    <summary><span>Links from this document</span><small>{file.outgoingLinks.length}</small></summary>
                    {relationshipList(file.outgoingLinks, "This document has no admitted outgoing links.")}
                  </details>
                  <details>
                    <summary><span>Links to this document</span><small>{file.incomingLinks.length}</small></summary>
                    {relationshipList(file.incomingLinks, "No admitted document links back to this source.")}
                  </details>
                </div>
              </section>

              <section className="reader-document" aria-label="Document text">
                {file.sections.length > 0 ? file.sections.map((section) => (
                  <section key={section.id} id={`document-section-${section.id}`} className="reader-text-section">
                    <header>
                      <h3>{section.section}</h3>
                      <span>{formatLayer(section.evidenceStatus)}</span>
                    </header>
                    <p>{section.text}</p>
                  </section>
                )) : (
                  <div className="document-empty">
                    <strong>No indexable section text</strong>
                    <p>The file remains admitted and connected, but its body has no retrievable section yet.</p>
                  </div>
                )}
              </section>
            </div>
          </div>
        </div>
      </article>
    </dialog>
  );
}
