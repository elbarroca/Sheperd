import type { JSX } from "react";
import { researchThemes } from "@/lib/research-synthesis";

export function ResearchSynthesis(): JSX.Element {
  return (
    <section className="research-synthesis section-block" aria-labelledby="research-synthesis-title">
      <div className="section-heading">
        <div>
          <p className="eyebrow">Evidence depth</p>
          <h2 id="research-synthesis-title">Open the full five-question evidence trail</h2>
        </div>
        <p>Use this when a decision needs the study logic, consequence, and source path behind a golden nugget.</p>
      </div>

      <details className="synthesis-disclosure">
        <summary>
          <span>Show the detailed research breakdown</span>
          <small>5 questions · studied · found · founder move · Michael move</small>
        </summary>
        <div className="synthesis-guide" aria-label="How to read the research synthesis">
          <strong>5</strong>
          <div>
            <span>Research questions</span>
            <p>Question → evidence-backed finding → founder decision → Michael workflow</p>
          </div>
        </div>

        <ol className="synthesis-list">
          {researchThemes.map((item) => (
            <li key={item.id} className="synthesis-card">
              <header>
                <code>{item.id}</code>
                <p>{item.theme}</p>
                <h3>{item.question}</h3>
                <span className={`synthesis-state synthesis-state-${item.state.replaceAll(" ", "-")}`}>{item.state}</span>
                <details>
                  <summary>Inspect source path</summary>
                  <code>{item.source}</code>
                </details>
              </header>
              <div className="synthesis-detail-grid">
                <div>
                  <h4>What we studied</h4>
                  <p>{item.studied}</p>
                </div>
                <div>
                  <h4>What we found</h4>
                  <p>{item.finding}</p>
                </div>
                <div className="synthesis-consequence">
                  <h4>What changes now</h4>
                  <dl>
                    <div><dt>Founder</dt><dd>{item.founderMove}</dd></div>
                    <div><dt>Michael</dt><dd>{item.michaelMove}</dd></div>
                  </dl>
                </div>
              </div>
            </li>
          ))}
        </ol>

        <div className="audience-takeaway" aria-label="Research value by audience">
          <article>
            <span>Founder value</span>
            <h3>Decide truth, ownership, and permission.</h3>
            <p>The dashboard shows which decisions unlock learning and which claims must remain blocked.</p>
          </article>
          <article>
            <span>Michael value</span>
            <h3>Prepare, measure, and escalate.</h3>
            <p>The same evidence becomes a weekly operating system without transferring specialist authority.</p>
          </article>
        </div>
      </details>
    </section>
  );
}
