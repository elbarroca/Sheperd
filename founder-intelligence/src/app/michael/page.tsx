import type { Metadata } from "next";
import type { JSX } from "react";
import { PageHeader } from "@/components/page-header";
import { SourceLink } from "@/components/source-link";
import { getFounderActionPlan } from "@/lib/data";
import {
  AI_SOURCE_PATH,
  michaelGtmPlays,
  michaelPhaseSummaries,
  michaelPillars,
  michaelWeeklyPlan,
  OPERATING_PLAN_SOURCE_PATH,
} from "@/lib/focused-content";
import type { MichaelExecutionState } from "@/lib/types";

export const metadata: Metadata = { title: "Michael's operating plan" };

const EXECUTION_LABELS: Record<MichaelExecutionState, string> = {
  "prepare-now": "Prepare now",
  "execute-after-go": "After founder GO",
  "evidence-review": "Use observed evidence",
  "founder-decision": "Founder decision",
};

function sourceLabel(path: string): string {
  return path.slice(path.lastIndexOf("/") + 1).replace(/\.md$/u, "").replace(/^Source - /u, "");
}

export default function MichaelPage(): JSX.Element {
  const actionPlan = getFounderActionPlan();

  return (
    <div className="focused-page michael-page">
      <PageHeader
        eyebrow="Michael's operating plan"
        title="One 16-week route from truth to a founder decision."
        description="Start with evidence and operating discipline. Activate one cohort only after Avi says GO. Each week below names the goal, actions, output, optimization rule, and source."
        meta={<><span>Operating owner</span><strong>GTM lead - Michael</strong><small>Founder - Avi approves activation</small></>}
      />

      <section className="focus-section michael-now" aria-labelledby="now-title">
        <div className="michael-command">
          <span>Current action</span>
          <code>{actionPlan.primary.experimentId}</code>
          <h2 id="now-title">{actionPlan.primary.title}</h2>
          <p>Michael runs the truth-and-gates workshop. Avi approves. All 12 gates need a state, owner, target date, and evidence link before any external activation.</p>
          <dl>
            <div><dt>Owner</dt><dd>{actionPlan.primary.owner}</dd></div>
            <div><dt>Approver</dt><dd>{actionPlan.primary.approver}</dd></div>
            <div><dt>Done when</dt><dd>{actionPlan.primary.doneWhen}</dd></div>
          </dl>
          <SourceLink path={actionPlan.primary.sourcePath} label="Open the experiment" />
        </div>
        <ol className="next-seven-days" aria-label="Michael's immediate sequence">
          <li><span>01</span><div><strong>Run the workshop</strong><p>Close authority, offer, claim, data, security, owner, and activation questions.</p></div></li>
          <li><span>02</span><div><strong>Build the W2 decision pack</strong><p>Truth map, synthetic CRM, ICP hypothesis, talk tracks, cohort design, and stop rules.</p></div></li>
          <li><span>03</span><div><strong>Stop at the GO gate</strong><p>No outreach, invoice handling, or public claim until Avi records approval.</p></div></li>
        </ol>
      </section>

      <section className="focus-section" aria-labelledby="route-title">
        <div className="focus-heading">
          <div>
            <span className="section-kicker">Weeks, goals, pillars, and optimization</span>
            <h2 id="route-title">The 16-week operating route</h2>
            <p>Open a week when you need the exact checklist. The route stays internal until its stated gate passes.</p>
          </div>
          <SourceLink path={OPERATING_PLAN_SOURCE_PATH} label="Read operating plan" />
        </div>

        <div className="pillar-index" aria-label="Michael's eight operating pillars">
          {michaelPillars.map((pillar, index) => (
            <details key={pillar.id}>
              <summary>
                <span>{String(index + 1).padStart(2, "0")}</span>
                <strong>{pillar.label}</strong>
              </summary>
              <p>{pillar.objective}</p>
              <small><b>Optimize:</b> {pillar.optimization}</small>
              <SourceLink path={pillar.sourcePath} label="Read pillar source" />
            </details>
          ))}
        </div>

        <div className="michael-route">
          {michaelPhaseSummaries.map((phase, phaseIndex) => {
            const weeks = michaelWeeklyPlan.filter((week) => week.phase === phase.id);

            return (
              <section className="phase-block" key={phase.id} aria-labelledby={`${phase.id}-title`}>
                <header className="phase-header">
                  <span className="phase-marker">{String(phaseIndex + 1).padStart(2, "0")}</span>
                  <div>
                    <small>{phase.weeks}</small>
                    <h3 id={`${phase.id}-title`}>{phase.goal}</h3>
                    <p>{phase.gate}</p>
                  </div>
                </header>
                <div className="week-list">
                  {weeks.map((week) => (
                    <details className="week-plan" key={week.week} open={week.week <= 2}>
                      <summary>
                        <span className="week-number">W{String(week.week).padStart(2, "0")}</span>
                        <strong>{week.goal}</strong>
                        <span className={`execution-state execution-state-${week.state}`}>{EXECUTION_LABELS[week.state]}</span>
                      </summary>
                      <div className="week-body">
                        <div className="week-actions">
                          <span>Actions</span>
                          <ol>
                            {week.actions.map((action) => <li key={action}>{action}</li>)}
                          </ol>
                        </div>
                        <dl className="week-outcomes">
                          <div><dt>Output</dt><dd>{week.deliverable}</dd></div>
                          <div><dt>Optimize</dt><dd>{week.optimization}</dd></div>
                        </dl>
                        <div className="week-footer">
                          <ul aria-label={`Week ${week.week} pillars`}>
                            {week.pillars.map((pillarId) => {
                              const pillar = michaelPillars.find((candidate) => candidate.id === pillarId);
                              return <li key={pillarId}>{pillar?.label ?? pillarId}</li>;
                            })}
                          </ul>
                          <div className="source-cluster" aria-label={`Week ${week.week} source documents`}>
                            {week.sourcePaths.map((path) => (
                              <SourceLink key={path} path={path} label={sourceLabel(path)} />
                            ))}
                          </div>
                        </div>
                      </div>
                    </details>
                  ))}
                </div>
              </section>
            );
          })}
        </div>
      </section>

      <section className="focus-section" aria-labelledby="gtm-title">
        <div className="focus-heading">
          <div>
            <span className="section-kicker">Lead finding, positioning, outreach, and learning</span>
            <h2 id="gtm-title">How Michael goes to market</h2>
            <p>Four plays turn the competitor and market research into action without overstating what SheperD has proven.</p>
          </div>
        </div>
        <div className="gtm-playbook">
          {michaelGtmPlays.map((play, index) => (
            <details key={play.id} open={index === 0}>
              <summary>
                <span>{String(index + 1).padStart(2, "0")}</span>
                <div><small>{EXECUTION_LABELS[play.state]}</small><h3>{play.title}</h3><p>{play.objective}</p></div>
              </summary>
              <div className="gtm-play-body">
                <ol>{play.steps.map((step) => <li key={step}>{step}</li>)}</ol>
                <dl>
                  <div><dt>Measure</dt><dd>{play.measure}</dd></div>
                  <div><dt>Boundary</dt><dd>{play.boundary}</dd></div>
                </dl>
                <div className="source-cluster">
                  {play.sourcePaths.map((path) => <SourceLink key={path} path={path} label={sourceLabel(path)} />)}
                </div>
              </div>
            </details>
          ))}
        </div>
      </section>

      <section className="focus-section ai-boundary" aria-labelledby="ai-title">
        <div className="focus-heading">
          <div>
            <span className="section-kicker">Operating boundary</span>
            <h2 id="ai-title">Automate preparation, never authority</h2>
          </div>
          <SourceLink path={AI_SOURCE_PATH} label="Read AI opportunity register" />
        </div>
        <div className="ai-lanes">
          <article><span>Automate</span><h3>Structure and retrieve</h3><p>Source retrieval, record normalization, completeness checks, date arithmetic, alerts, and metric reconciliation.</p></article>
          <article><span>Assist</span><h3>Draft and compare</h3><p>Account briefs, question sets, message variants, content outlines, decision briefs, and cohort comparisons.</p></article>
          <article><span>Human only</span><h3>Interpret and act</h3><p>Eligibility, liability, qualification, pricing, external sending, claims, filing, settlement, and final outcomes.</p></article>
        </div>
        <aside className="proposal-note">
          <div><strong>Original 16-week proposal</strong><p>Internal proposal - not an executed agreement. Its targets are planning bands, not a forecast or proof.</p></div>
          <SourceLink path="10_Sources/Source - 16 Week Engagement Plan.md" label="Read complete proposal" />
        </aside>
      </section>
    </div>
  );
}
