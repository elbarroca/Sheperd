import Link from "next/link";
import type { JSX } from "react";
import { SourceLink } from "@/components/source-link";
import { briefLenses, MICHAEL_PLAN_SOURCE_PATH, phases } from "@/lib/content";
import { getFounderActionPlan, getOverviewData } from "@/lib/data";
import type { FounderAction, FounderActionLane } from "@/lib/types";

const laneCopy: Record<FounderActionLane, { label: string; description: string }> = {
  "do-now": {
    label: "Do now",
    description: "Internal work that can produce a decision without external activation.",
  },
  "prepare-internally": {
    label: "Prepare internally",
    description: "Synthetic controls that can be tested without customer or market exposure.",
  },
  "not-yet": {
    label: "Not yet",
    description: "External, publication, or security work that remains blocked by evidence and approval.",
  },
};

function ActionLane({ lane, actions }: { lane: FounderActionLane; actions: FounderAction[] }): JSX.Element {
  const copy = laneCopy[lane];

  return (
    <article className={`action-lane action-lane-${lane}`}>
      <header>
        <span>{copy.label}</span>
        <strong>{actions.length}</strong>
      </header>
      <p>{copy.description}</p>
      <ul>
        {actions.map((action) => (
          <li key={action.experimentId}>
            <code>{action.experimentId}</code>
            <div>
              <strong>{action.title}</strong>
              <span>{action.owner}</span>
            </div>
            <SourceLink path={action.sourcePath} />
          </li>
        ))}
      </ul>
    </article>
  );
}

export default function FounderBriefPage(): JSX.Element {
  const overview = getOverviewData();
  const actionPlan = getFounderActionPlan();
  const primary = actionPlan.primary;

  return (
    <>
      <section className="brief-command" aria-labelledby="brief-command-title">
        <div className="brief-decision">
          <p className="brief-kicker">Founder decision brief</p>
          <span className="brief-hold">Hold external activation</span>
          <h1 id="brief-command-title">Prepare the decision. Do not scale yet.</h1>
          <p>{overview.counts.blockers} authority, product, claims, security, and capacity gates remain unresolved.</p>
          <small>Public read-only synthesis · Evidence snapshot {overview.sourceDate}</small>
        </div>

        <div className="brief-primary-action">
          <div className="brief-action-id"><span>Do next</span><code>{primary.experimentId}</code></div>
          <h2>{primary.title}</h2>
          <p>Turn every open gate into an explicit decision before any external work begins.</p>
          <dl>
            <div><dt>Owner</dt><dd>{primary.owner}</dd></div>
            <div><dt>Approver</dt><dd>{primary.approver}</dd></div>
            <div><dt>Bring</dt><dd>{primary.requiredEvidence}</dd></div>
            <div><dt>Done when</dt><dd>{primary.doneWhen}</dd></div>
          </dl>
          <p className="brief-stop"><strong>Stop if:</strong> {primary.stopRule}</p>
          <div className="brief-action-links">
            <Link className="primary-action" href="/improvements">Open decisions</Link>
            <SourceLink path={primary.sourcePath} />
          </div>
        </div>
      </section>

      <section className="brief-truths brief-section" aria-labelledby="brief-truths-title">
        <div className="brief-section-heading">
          <div><span>Research in plain English</span><h2 id="brief-truths-title">Three truths lead to one action</h2></div>
          <p>Each conclusion stays attached to the document that supports it.</p>
        </div>
        <ol className="brief-route" aria-label="Company truth to full source decision route">
          {briefLenses.map((lens) => (
            <li key={lens.id}>
              <span className="route-node" aria-hidden="true" />
              <p>{lens.label}</p>
              <h3>{lens.finding}</h3>
              <dl>
                <div><dt>What it means</dt><dd>{lens.implication}</dd></div>
                <div><dt>What changes</dt><dd>{lens.nextAction}</dd></div>
              </dl>
              <SourceLink path={lens.sourcePath} />
            </li>
          ))}
          <li className="brief-route-terminal">
            <span className="route-node" aria-hidden="true" />
            <p>Action now</p>
            <h3>Run the truth-and-gates workshop.</h3>
            <Link className="source-link" href="/improvements">Review all 12 gates<span aria-hidden="true">→</span></Link>
            <SourceLink path={primary.sourcePath} />
          </li>
          <li className="brief-route-terminal">
            <span className="route-node" aria-hidden="true" />
            <p>Full source</p>
            <h3>Read Avi&apos;s complete 16-week proposal.</h3>
            <SourceLink path={MICHAEL_PLAN_SOURCE_PATH} label="Open full plan" />
          </li>
        </ol>
      </section>

      <section className="brief-actions brief-section" aria-labelledby="brief-actions-title">
        <div className="brief-section-heading">
          <div><span>Action boundary</span><h2 id="brief-actions-title">What Michael can do—and what stays blocked</h2></div>
          <p>Priority never overrides eligibility, permission, or evidence.</p>
        </div>
        <div className="action-lanes">
          <ActionLane lane="do-now" actions={actionPlan.doNow} />
          <ActionLane lane="prepare-internally" actions={actionPlan.prepareInternally} />
          <ActionLane lane="not-yet" actions={actionPlan.notYet} />
        </div>
      </section>

      <section className="brief-source brief-section" aria-labelledby="brief-source-title">
        <div className="brief-section-heading">
          <div><span>16-week source</span><h2 id="brief-source-title">Keep the ambition. Gate the progression.</h2></div>
          <p>The proposal is a discussion framework, not an executed agreement or proven forecast.</p>
        </div>
        <ol className="brief-phases">
          {phases.map((phase) => (
            <li key={phase.period}>
              <span>{phase.period}</span>
              <p>{phase.sourceLabel}</p>
              <h3>{phase.admittedLabel}</h3>
              <small>{phase.detail}</small>
              <strong className={`state-pill state-${phase.state}`}>{phase.state.replaceAll("-", " ")}</strong>
            </li>
          ))}
        </ol>
        <div className="full-source-callout">
          <div><span>Internal proposal</span><strong>Not an executed agreement</strong></div>
          <p>Read the complete message, three phases, eight operating axes, engagement principles, and original next steps.</p>
          <SourceLink path={MICHAEL_PLAN_SOURCE_PATH} label="Open the complete 16-week plan" />
        </div>
      </section>
    </>
  );
}
