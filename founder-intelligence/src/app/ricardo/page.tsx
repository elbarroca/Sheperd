import type { Metadata } from "next";
import Link from "next/link";
import type { JSX } from "react";
import { SourceLink } from "@/components/source-link";
import { MICHAEL_PLAN_SOURCE_PATH, ricardoNotes } from "@/lib/content";

export const metadata: Metadata = { title: "Ricardo analysis" };

const workshopQuestions = [
  "What must be true before Michael represents SheperD?",
  "Who approves each material decision and who is the backup?",
  "What exists today versus roadmap?",
  "Which exact claims and commercial terms are approved?",
  "Which system may hold each data class?",
  "Who reviews domain meaning and product output, and how fast?",
  "Which Week 2 evidence permits the first bounded cohort?",
  "Which result causes continue, change, stop, or no-go?",
] as const;

export default function RicardoPage(): JSX.Element {
  return (
    <>
      <header className="analysis-hero-compact">
        <div>
          <p>Ricardo analysis</p>
          <h1>Keep the ambition. Make it earn evidence.</h1>
          <span>Interpretation, not company fact</span>
        </div>
        <aside>
          <strong>What changes now</strong>
          <p>Run the founder truth-and-gates workshop before any external cohort.</p>
          <Link href="/improvements">Open decisions<span aria-hidden="true">→</span></Link>
        </aside>
      </header>

      <section className="analysis-translation" aria-labelledby="analysis-translation-title">
        <div className="brief-section-heading">
          <div><span>Source to consequence</span><h2 id="analysis-translation-title">Four corrections to the operating plan</h2></div>
          <p>The source, interpretation, and founder consequence remain separate.</p>
        </div>
        <div className="analysis-table" role="table" aria-label="Ricardo source translation">
          <div className="analysis-table-head" role="row">
            <span role="columnheader">Source</span>
            <span role="columnheader">Ricardo&apos;s interpretation</span>
            <span role="columnheader">What changes</span>
            <span role="columnheader">Document</span>
          </div>
          {ricardoNotes.map((note) => (
            <article key={note.id} className="analysis-table-row" role="row">
              <div role="cell" data-label="Source"><code>{note.id}</code><h3>{note.sourceObservation}</h3></div>
              <p role="cell" data-label="Ricardo's interpretation">{note.note}</p>
              <p role="cell" data-label="What changes">{note.implication}</p>
              <div role="cell" data-label="Document"><SourceLink path={note.evidence} /></div>
            </article>
          ))}
        </div>
      </section>

      <section className="analysis-workshop" aria-labelledby="analysis-workshop-title">
        <div>
          <span>Founder workshop</span>
          <h2 id="analysis-workshop-title">Turn the plan into eight explicit answers</h2>
          <p>Use these questions to record authority, product truth, controls, and the external-activation decision.</p>
          <SourceLink path={MICHAEL_PLAN_SOURCE_PATH} label="Open the complete 16-week plan" />
        </div>
        <details>
          <summary>Show the eight questions</summary>
          <ol>{workshopQuestions.map((question) => <li key={question}>{question}</li>)}</ol>
        </details>
      </section>
    </>
  );
}
