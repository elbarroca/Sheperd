import type { Metadata } from "next";
import { PageHeader } from "@/components/page-header";
import { SourceLink } from "@/components/source-link";
import { getFounderActionPlan } from "@/lib/data";
import { AI_SOURCE_PATH, michaelTasks, MICHAEL_ROLE_SOURCE_PATH } from "@/lib/focused-content";

export const metadata: Metadata = { title: "Michael's operating plan" };

export default function MichaelPage() {
  const actionPlan = getFounderActionPlan();

  return (
    <div className="focused-page">
      <PageHeader
        eyebrow="Michael's operating plan"
        title="Build the learning system before running the market."
        description="Michael owns commercial learning, CRM discipline, source-led content, and weekly decision preparation. Avi owns activation, pricing, claims, and other founder decisions."
        meta={<><span>Role</span><strong>GTM lead - Michael</strong><small>Founder - Avi approves</small></>}
      />

      <section className="focus-section michael-now" aria-labelledby="now-title">
        <div className="michael-command">
          <span>Do now</span>
          <code>{actionPlan.primary.experimentId}</code>
          <h2 id="now-title">{actionPlan.primary.title}</h2>
          <p>Michael runs the truth-and-gates workshop. Avi approves. All 12 gates need a state, owner, target date, and evidence link before external activation.</p>
          <dl>
            <div><dt>Owner</dt><dd>{actionPlan.primary.owner}</dd></div>
            <div><dt>Approver</dt><dd>{actionPlan.primary.approver}</dd></div>
            <div><dt>Done when</dt><dd>{actionPlan.primary.doneWhen}</dd></div>
          </dl>
          <SourceLink path={actionPlan.primary.sourcePath} />
        </div>
        <ol className="next-seven-days">
          <li><span>01</span><div><strong>Close the truth table</strong><p>Entity, authority, offer, claims, data, security, and owners.</p></div></li>
          <li><span>02</span><div><strong>Build the synthetic system</strong><p>CRM objects, stages, event definitions, dashboards, and decision cadence.</p></div></li>
          <li><span>03</span><div><strong>Prepare one cohort design</strong><p>Eligibility, measures, stop rules, reviewer capacity, and explicit GO decision.</p></div></li>
        </ol>
      </section>

      <section className="focus-section" aria-labelledby="tasks-title">
        <div className="focus-heading">
          <div><p className="focus-label">Eight workstreams</p><h2 id="tasks-title">What Michael does, where AI helps, and who decides</h2></div>
          <SourceLink path={MICHAEL_ROLE_SOURCE_PATH} label="Read role charter" />
        </div>
        <div className="task-table" role="table" aria-label="Michael workstreams and AI support">
          <div className="task-table-head" role="row">
            <span role="columnheader">Workstream and outcome</span><span role="columnheader">AI can assist</span><span role="columnheader">Human checkpoint</span><span role="columnheader">State</span>
          </div>
          {michaelTasks.map((task) => (
            <div className="task-row" role="row" key={task.id}>
              <div role="cell"><code>{task.id}</code><h3>{task.workstream}</h3><p>{task.outcome}</p><SourceLink path={task.sourcePath} /></div>
              <p role="cell" data-label="AI can assist">{task.aiAssist}</p>
              <p role="cell" data-label="Human checkpoint">{task.humanDecision}</p>
              <strong role="cell" className={`task-state task-state-${task.state}`}>{task.state === "prepare-now" ? "Prepare now" : "Approval gate"}</strong>
            </div>
          ))}
        </div>
      </section>

      <section className="focus-section ai-boundary" aria-labelledby="ai-title">
        <div className="focus-heading">
          <div><p className="focus-label">AI operating rule</p><h2 id="ai-title">Automate preparation, never authority</h2></div>
          <SourceLink path={AI_SOURCE_PATH} label="Read AI opportunity register" />
        </div>
        <div className="ai-lanes">
          <article><span>Automate</span><h3>Structure and retrieve</h3><p>Extraction, completeness checks, date arithmetic, cited summaries, alerts, and metric reconciliation.</p></article>
          <article><span>Assist</span><h3>Draft and compare</h3><p>Research briefs, customer questions, message variants, packet drafts, and cohort analysis.</p></article>
          <article><span>Human only</span><h3>Interpret and act</h3><p>Liability, eligibility, route selection, pricing, external sending, claims, filing, settlement, and final outcomes.</p></article>
        </div>
      </section>

      <aside className="proposal-note">
        <div><strong>16-week source status</strong><p>Internal proposal - not an executed agreement. Use it as a learning plan, not a proven forecast.</p></div>
        <SourceLink path="10_Sources/Source - 16 Week Engagement Plan.md" label="Read complete proposal" />
      </aside>
    </div>
  );
}
