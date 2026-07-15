import type { Metadata } from "next";
import { PageHeader } from "@/components/page-header";
import { ricardoNotes } from "@/lib/content";

export const metadata: Metadata = { title: "Ricardo notes" };

export default function RicardoPage() {
  return (
    <>
      <PageHeader
        eyebrow="Ricardo notes · interpretation layer"
        title="The useful tension inside Avi’s plan."
        description="These notes preserve the founder’s ambition while correcting unsupported certainty, hidden dependencies, and unsafe sequencing."
        meta={<><span>Layer status</span><strong>Interpretation · not fact</strong></>}
      />
      <section className="ricardo-manifesto">
        <span className="manifesto-mark">R</span>
        <blockquote>“Do not reduce the ambition. Convert it into an evidence contract.”</blockquote>
        <p>Ricardo’s operating principle</p>
      </section>
      <section className="notes-stack section-block">
        {ricardoNotes.map((note) => (
          <article key={note.id} className="note-card">
            <div className="note-rail"><code>{note.id}</code><span>Ricardo interpretation</span></div>
            <div className="note-body"><h2>{note.title}</h2><p>{note.note}</p><div className="implication"><span>Operating implication</span><strong>{note.implication}</strong></div><code className="source-code">{note.evidence}</code></div>
          </article>
        ))}
      </section>
      <section className="question-grid section-block">
        <div><p className="eyebrow">Founder conversation</p><h2>Seven questions that convert vision into operating truth.</h2></div>
        <ol>
          <li>What must be true before Michael represents SheperD?</li>
          <li>What exists today versus roadmap?</li>
          <li>Which exact claims and commercial terms are approved?</li>
          <li>Which system may hold each data class?</li>
          <li>Who reviews domain meaning and product output—and how fast?</li>
          <li>Which Week 2 evidence permits the first bounded cohort?</li>
          <li>Which result causes continue, change, stop, or no-go?</li>
        </ol>
      </section>
    </>
  );
}
