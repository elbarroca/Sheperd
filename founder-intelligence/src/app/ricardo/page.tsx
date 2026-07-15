import type { Metadata } from "next";
import { PageHeader } from "@/components/page-header";
import { ricardoNotes } from "@/lib/content";

export const metadata: Metadata = { title: "Ricardo analysis" };

const questionGroups = [
  {
    title: "Authority",
    questions: [
      "What must be true before Michael represents SheperD?",
      "Who approves each material decision and who is the backup?",
    ],
  },
  {
    title: "Product and claims",
    questions: [
      "What exists today versus roadmap?",
      "Which exact claims and commercial terms are approved?",
    ],
  },
  {
    title: "Data and review",
    questions: [
      "Which system may hold each data class?",
      "Who reviews domain meaning and product output, and how fast?",
    ],
  },
  {
    title: "Decision",
    questions: [
      "Which Week 2 evidence permits the first bounded cohort?",
      "Which result causes continue, change, stop, or no-go?",
    ],
  },
] as const;

export default function RicardoPage() {
  return (
    <>
      <PageHeader
        eyebrow="Ricardo analysis"
        title="Convert ambition into an evidence contract."
        description="These notes preserve the founder vision while making unsupported certainty, hidden dependencies, and unsafe sequencing visible."
        meta={<><span>Layer status</span><strong>Interpretation, not fact</strong></>}
      />

      <aside className="analysis-principle">
        <span>Operating principle</span>
        <p>Keep the ambition. Make every move earn its evidence, owner, permission, and stop rule.</p>
      </aside>

      <section className="analysis-matrix section-block" aria-labelledby="analysis-title">
        <div className="section-heading">
          <div><p className="eyebrow">Research to consequence</p><h2 id="analysis-title">Four interpretations that change the operating plan</h2></div>
          <p>Each note keeps the source observation separate from Ricardo&apos;s conclusion.</p>
        </div>
        {ricardoNotes.map((note) => (
          <article key={note.id} className="analysis-row">
            <header><code>{note.id}</code><h3>{note.title}</h3></header>
            <dl>
              <div><dt>Source observation</dt><dd>{note.sourceObservation}</dd></div>
              <div><dt>Ricardo analysis</dt><dd>{note.note}</dd></div>
              <div><dt>Founder consequence</dt><dd>{note.implication}</dd></div>
            </dl>
            <details><summary>Inspect source path</summary><code>{note.evidence}</code></details>
          </article>
        ))}
      </section>

      <section className="question-section section-block" aria-labelledby="questions-title">
        <div className="section-heading">
          <div><p className="eyebrow">Founder conversation</p><h2 id="questions-title">Eight questions turn vision into operating truth</h2></div>
          <p>Use these in the founder truth and gates workshop.</p>
        </div>
        <div className="question-groups">
          {questionGroups.map((group) => (
            <article key={group.title}>
              <h3>{group.title}</h3>
              <ol>{group.questions.map((question) => <li key={question}>{question}</li>)}</ol>
            </article>
          ))}
        </div>
      </section>
    </>
  );
}
