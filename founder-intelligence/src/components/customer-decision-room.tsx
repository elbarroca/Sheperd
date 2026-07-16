import Link from "next/link";
import type { JSX } from "react";
import { PageHeader } from "./page-header";
import { SourceLink } from "./source-link";
import {
  buyingCommittee,
  claimReadiness,
  competitiveDecision,
  currentDecision,
  customerJourney,
  DECISION_ROOM_SOURCES,
  decisionManifest,
  decisionRoomSourceShelf,
  icpProfile,
  icpQualificationDimensions,
  icpSetupMetrics,
  messageLibrary,
  offerLadder,
  outcomeState,
  painEconomics,
  targetAccountQueue,
  type DecisionRoomEvidenceState,
} from "../lib/decision-room-content";
import type { DecisionRoomExecutionState, DecisionRoomExperiment } from "../lib/types";
import styles from "../app/decision-room/decision-room.module.css";

const manifestStateClasses: Record<DecisionRoomEvidenceState, string> = {
  supported: styles.stateSupported,
  hypothesis: styles.stateHypothesis,
  "research-now": styles.stateResearch,
  "founder-decision": styles.stateFounder,
  "pilot-measurement": styles.statePilot,
  designed: styles.stateDesigned,
  "setup-ready": styles.stateSetup,
  "needs-approval": styles.stateApproval,
  "prepare-now": styles.statePrepare,
  "no-data": styles.stateNoData,
};

const experimentStateLabels: Record<DecisionRoomExecutionState, string> = {
  "prepare-now": "Prepare now",
  "synthetic-only": "Synthetic only",
  "blocked-external": "After founder setup",
  "blocked-publication": "After claims approval",
  "blocked-security": "After secure intake",
};

const evidenceStateLabels: Record<DecisionRoomEvidenceState, string> = {
  supported: "Supported",
  hypothesis: "Hypothesis",
  "research-now": "Research now",
  "founder-decision": "Founder decision",
  "pilot-measurement": "Pilot measurement",
  designed: "Designed",
  "setup-ready": "Setup ready",
  "needs-approval": "Needs approval",
  "prepare-now": "Prepare now",
  "no-data": "No data",
};

function humanize(value: string): string {
  return value.replaceAll("-", " ");
}

function experimentDecisionLabel(experiment: DecisionRoomExperiment): string {
  if (experiment.decision) return experiment.decision;
  if (experiment.executionState === "prepare-now" || experiment.executionState === "synthetic-only") {
    return "Pending";
  }
  return "Waiting on setup";
}

export function CustomerDecisionRoom({
  experiments,
}: {
  experiments: DecisionRoomExperiment[];
}): JSX.Element {
  return (
    <div className={`focused-page ${styles.page}`}>
      <PageHeader
        eyebrow="Customer and decision room"
        title="Turn the market evidence into a commercial setup."
        description="One working view of what is already known, what Michael can research now, what Avi must decide, and what the first pilot needs to measure."
        meta={<><span>Current posture</span><strong>Setup active</strong><small>Public claims stay controlled</small></>}
      />

      <nav className={styles.manifest} aria-label="Decision dependency map">
        <ol>
          {decisionManifest.map((item) => (
            <li key={item.id}>
              <a href={`#${item.id}`}>
                <span>{item.label}</span>
                <strong className={manifestStateClasses[item.state]}>{item.stateLabel}</strong>
              </a>
            </li>
          ))}
        </ol>
      </nav>

      <section className={`${styles.section} ${styles.command}`} aria-labelledby="current-decision-title">
        <div className={styles.commandPrimary}>
          <div className={styles.commandCode}>
            <span>Next founder decision</span>
            <code>{currentDecision.experimentId}</code>
          </div>
          <h2 id="current-decision-title">{currentDecision.title}</h2>
          <p>{currentDecision.instruction}</p>
          <SourceLink path={currentDecision.sourcePath} label="Open the control note" />
        </div>
        <dl className={styles.commandFacts}>
          <div><dt>Owner</dt><dd>{currentDecision.owner}</dd></div>
          <div><dt>Approver</dt><dd>{currentDecision.approver}</dd></div>
          <div><dt>Done when</dt><dd>{currentDecision.doneWhen}</dd></div>
        </dl>
      </section>

      <section id="customer" className={styles.section} aria-labelledby="customer-title">
        <div className={styles.sectionHeading}>
          <div>
            <span>Who to learn from</span>
            <h2 id="customer-title">A specific customer hypothesis, not a broad importer market</h2>
            <p>{icpProfile.boundary}</p>
          </div>
          <SourceLink path={icpProfile.sourcePath} label="Read ICP and personas" />
        </div>

        <div className={styles.customerGrid}>
          <article className={styles.icpStatement}>
            <span className={styles.stateHypothesis}>ICP hypothesis</span>
            <p>{icpProfile.bestFit}</p>
          </article>
          <dl className={styles.icpMetrics} aria-label="Current ICP setup metrics">
            {icpSetupMetrics.map((metric) => (
              <div key={metric.label}>
                <dt>{metric.label}</dt>
                <dd>{metric.value}</dd>
                <small>{metric.state}</small>
              </div>
            ))}
          </dl>
        </div>

        <section className={styles.icpAperture} aria-labelledby="icp-aperture-title">
          <div className={styles.icpApertureHeading}>
            <div>
              <span>Qualification aperture</span>
              <h3 id="icp-aperture-title">Five evidence filters define pilot fit</h3>
            </div>
            <p>Move an account forward only when each filter has minimum proof. This is a qualification method, not a predictive score.</p>
          </div>
          <ol>
            {icpQualificationDimensions.map((dimension) => (
              <li key={dimension.id}>
                <div className={styles.icpApertureCode}>
                  <code>{dimension.id}</code>
                  <span>{dimension.label}</span>
                </div>
                <p>{dimension.signal}</p>
                <dl>
                  <div><dt>Minimum proof</dt><dd>{dimension.minimumProof}</dd></div>
                  <div><dt>Decision rule</dt><dd>{dimension.decision}</dd></div>
                </dl>
              </li>
            ))}
          </ol>
        </section>

        <div className={`${styles.segmentList} ${styles.segmentPanel}`} aria-label="Beachhead hypotheses">
          {icpProfile.segments.map((segment) => (
            <details key={segment.title}>
              <summary>{segment.title}</summary>
              <dl>
                <div><dt>Inclusion signal</dt><dd>{segment.signal}</dd></div>
                <div><dt>Learning</dt><dd>{segment.learning}</dd></div>
                <div><dt>Disqualifier</dt><dd>{segment.disqualifier}</dd></div>
              </dl>
            </details>
          ))}
        </div>

        <div className={styles.committeeGrid} aria-label="Buying committee">
          {buyingCommittee.map((member) => (
            <article key={member.role}>
              <span>{member.role}</span>
              <h3>{member.people}</h3>
              <dl>
                <div><dt>Cares about</dt><dd>{member.caresAbout}</dd></div>
                <div><dt>Likely trigger</dt><dd>{member.triggers}</dd></div>
                <div><dt>Proof needed</dt><dd>{member.proof}</dd></div>
              </dl>
            </article>
          ))}
        </div>

        <div className={styles.gateGrid}>
          <article>
            <h3>Admission gates</h3>
            <ul>{icpProfile.admissionGates.map((gate) => <li key={gate}>{gate}</li>)}</ul>
          </article>
          <article>
            <h3>Disqualify when</h3>
            <ul>{icpProfile.disqualifiers.map((item) => <li key={item}>{item}</li>)}</ul>
          </article>
        </div>
      </section>

      <section id="economics" className={styles.section} aria-labelledby="economics-title">
        <div className={styles.sectionHeading}>
          <div>
            <span>Economics setup</span>
            <h2 id="economics-title">Most of the economics work can start now</h2>
            <p>{painEconomics.conclusion}</p>
          </div>
          <SourceLink path={painEconomics.sourcePath} label="Read market evidence" />
        </div>

        <div className={styles.formula}>
          <span>Commercial model</span>
          <code>{painEconomics.formula}</code>
        </div>
        <div className={styles.signalGrid} aria-label="Admitted market and pricing context">
          {painEconomics.publicSignals.map((signal) => (
            <article key={signal.label}>
              <div className={styles.signalMeta}>
                <code>{signal.sourceId}</code>
                <span className={manifestStateClasses[signal.state]}>{evidenceStateLabels[signal.state]}</span>
              </div>
              <strong>{signal.value}</strong>
              <h3>{signal.label}</h3>
              <p>{signal.meaning}</p>
              <small>{signal.boundary}</small>
            </article>
          ))}
        </div>

        <div className={styles.workbenchHeading}>
          <div>
            <span>Input workbench</span>
            <h3>Every missing input has a method and owner</h3>
          </div>
          <p>Research is not the same as deciding. A founder choice is not the same as a measured customer result.</p>
        </div>
        <div className={styles.inputWorkbench}>
          {painEconomics.inputWorkbench.map((input) => (
            <article key={input.label}>
              <div className={styles.workbenchTitle}>
                <div>
                  <span>{input.lane}</span>
                  <h3>{input.label}</h3>
                </div>
                <strong className={manifestStateClasses[input.state]}>{evidenceStateLabels[input.state]}</strong>
              </div>
              <p>{input.method}</p>
              <dl>
                <div><dt>Owner</dt><dd>{input.owner}</dd></div>
                <div><dt>Produces</dt><dd>{input.output}</dd></div>
                <div><dt>Next action</dt><dd>{input.nextAction}</dd></div>
              </dl>
              <SourceLink path={input.sourcePath} label="Open source method" />
            </article>
          ))}
        </div>

        <div className={styles.sizingHeading}>
          <span>Market-sizing ladder</span>
          <h3>Define the calculation before assigning a value</h3>
        </div>
        <dl className={styles.sizingGrid}>
          {painEconomics.sizing.map((item) => (
            <div key={item.label}>
              <dt>{item.label}</dt>
              <dd>{item.method}</dd>
              <span>Owner: {item.owner}</span>
              <strong className={manifestStateClasses[item.state]}>{evidenceStateLabels[item.state]}</strong>
            </div>
          ))}
        </dl>
      </section>

      <section className={styles.section} aria-labelledby="competition-decision-title">
        <div className={styles.sectionHeading}>
          <div>
            <span>Competition decision</span>
            <h2 id="competition-decision-title">Differentiate on measured work, not category language</h2>
            <p>No superiority, win-rate, or performance claim is admitted.</p>
          </div>
          <SourceLink path={competitiveDecision.sourcePath} label="Read sales playbook" />
        </div>

        <div className={styles.competitionGrid}>
          <div className={styles.criteriaGrid}>
            {competitiveDecision.differentiation.map((item) => (
              <article key={item.title}><h3>{item.title}</h3><p>{item.criterion}</p></article>
            ))}
          </div>
          <div className={styles.objectionList}>
            <h3>Likely objections</h3>
            {competitiveDecision.objections.map((item) => (
              <details key={item.objection}>
                <summary>{item.objection}</summary>
                <p>{item.response}</p>
              </details>
            ))}
          </div>
          <article className={styles.capturePanel}>
            <span className={styles.stateNoData}>No win or loss records</span>
            <h3>Capture these reasons later</h3>
            <ul>{competitiveDecision.winLossCapture.map((item) => <li key={item}>{item}</li>)}</ul>
          </article>
        </div>
      </section>

      <section id="offer" className={styles.section} aria-labelledby="offer-title">
        <div className={styles.sectionHeading}>
          <div>
            <span>Offer design</span>
            <h2 id="offer-title">The offer ladder is a build sequence, not a wall of blockers</h2>
            <p>Start with the diagnostic, assign the missing owners, and use pilot evidence to earn the deeper offers.</p>
          </div>
          <SourceLink path={competitiveDecision.sourcePath} label="Read complete offer ladder" />
        </div>
        <div className={styles.offerList}>
          {offerLadder.map((offer, index) => (
            <details key={offer.title} open={index === 0}>
              <summary>
                <span>{offer.title}</span>
                <strong className={manifestStateClasses[offer.state]}>{offer.stateLabel}</strong>
              </summary>
              <div>
                <dl>
                  <div><dt>Offer purpose</dt><dd>{offer.purpose}</dd></div>
                  <div><dt>Owner</dt><dd>{offer.owner}</dd></div>
                  <div><dt>Set up next</dt><dd>{offer.setupAction}</dd></div>
                  <div><dt>Ready when</dt><dd>{offer.readyWhen}</dd></div>
                  <div><dt>Proof of readiness</dt><dd>{offer.proof}</dd></div>
                </dl>
                <p><strong>Guardrail:</strong> {offer.guardrail}</p>
              </div>
            </details>
          ))}
        </div>
      </section>

      <section id="claims" className={styles.section} aria-labelledby="claims-title">
        <div className={styles.sectionHeading}>
          <div>
            <span>Claims readiness</span>
            <h2 id="claims-title">Safe internal wording is not permission to send</h2>
            <p>Every external sentence still requires the exact claim, source, reviewer, channel, approval date, and expiry.</p>
          </div>
          <SourceLink path={DECISION_ROOM_SOURCES.claims} label="Open claims register" />
        </div>
        <div className={styles.draftWarning} role="note">
          <strong>DRAFT - HUMAN REVIEW REQUIRED</strong>
          <span>No send or publication is authorized.</span>
        </div>
        <div className={styles.claimList}>
          {claimReadiness.map((claim) => (
            <details key={claim.id} open={claim.id === "C-027" || claim.id === "C-028"}>
              <summary>
                <code>{claim.id}</code>
                <span>{claim.topic}</span>
                <strong>{claim.state}</strong>
              </summary>
              <div>
                <dl>
                  <div><dt>Safe internal wording</dt><dd>{claim.safeWording}</dd></div>
                  <div><dt>Do not say</dt><dd>{claim.prohibited}</dd></div>
                  <div><dt>Required approval</dt><dd>{claim.approver}</dd></div>
                </dl>
              </div>
            </details>
          ))}
        </div>
      </section>

      <section id="journey" className={styles.section} aria-labelledby="journey-title">
        <div className={styles.sectionHeading}>
          <div>
            <span>Customer journey</span>
            <h2 id="journey-title">Each handoff needs proof before the next one opens</h2>
            <p>The likely bottleneck is secure, complete, valid data submission, not initial interest.</p>
          </div>
          <SourceLink path={DECISION_ROOM_SOURCES.journey} label="Read customer journey" />
        </div>
        <ol className={styles.journey}>
          {customerJourney.map((step, index) => (
            <li key={step.title}>
              <div className={styles.journeyIndex}>{String(index + 1).padStart(2, "0")}</div>
              <div>
                <span className={manifestStateClasses[step.state]}>{evidenceStateLabels[step.state]}</span>
                <h3>{step.title}</h3>
                <p>{step.friction}</p>
                <dl>
                  <div><dt>Proof to advance</dt><dd>{step.proof}</dd></div>
                  <div><dt>Decision owner</dt><dd>{step.owner}</dd></div>
                </dl>
              </div>
            </li>
          ))}
        </ol>
      </section>

      <section id="experiments" className={styles.section} aria-labelledby="experiments-title">
        <div className={styles.sectionHeading}>
          <div>
            <span>Michael&apos;s execution desk</span>
            <h2 id="experiments-title">Prepare the system in the order it can actually run</h2>
            <p>The queue, messages, and experiments show what Michael prepares now and which setup step unlocks the work after it.</p>
          </div>
          <SourceLink path={DECISION_ROOM_SOURCES.cadence} label="Read KPI and experiment contract" />
        </div>

        <div className={styles.queuePanel}>
          <div className={styles.emptyQueue}>
            <span className={styles.stateNoData}>0 admitted records</span>
            <h3>{targetAccountQueue.state}</h3>
            <p>{targetAccountQueue.instruction}</p>
            <div className={styles.queueSources}>
              <SourceLink path={DECISION_ROOM_SOURCES.michaelPlan} label="Read source proposal" />
              <SourceLink path={targetAccountQueue.sourcePath} label="Read CRM data model" />
            </div>
          </div>
          <div className={styles.queueFields} aria-label="Required target-account fields">
            {targetAccountQueue.fieldGroups.map((group) => (
              <article key={group.label}>
                <h4>{group.label}</h4>
                <ul>{group.fields.map((field) => <li key={field}>{field}</li>)}</ul>
              </article>
            ))}
          </div>
        </div>

        <div className={styles.executionGrid}>
          <section className={styles.messagePanel} aria-labelledby="messages-title">
            <div className={styles.panelHeading}>
              <span>DRAFT - HUMAN REVIEW REQUIRED</span>
              <h3 id="messages-title">Messaging library</h3>
            </div>
            {messageLibrary.map((message) => (
              <details key={message.persona}>
                <summary>{message.persona}</summary>
                <p>{message.direction}</p>
                <dl>
                  <div><dt>Claim IDs</dt><dd>{message.claimIds}</dd></div>
                  <div><dt>Proof before use</dt><dd>{message.proof}</dd></div>
                </dl>
              </details>
            ))}
          </section>

          <section className={styles.experimentPanel} aria-labelledby="experiment-board-title">
            <div className={styles.panelHeading}>
              <span>Eight bounded hypotheses</span>
              <h3 id="experiment-board-title">Experiment board</h3>
            </div>
            {experiments.map((experiment) => (
              <details key={experiment.experimentId} open={experiment.experimentId === "EXP-001"}>
                <summary>
                  <code>{experiment.experimentId}</code>
                  <span>{experiment.name}</span>
                  <strong>{experimentStateLabels[experiment.executionState]}</strong>
                </summary>
                <div className={styles.experimentBody}>
                  <p>{experiment.hypothesis}</p>
                  <dl className={styles.experimentMeta}>
                    <div><dt>Segment</dt><dd>{humanize(experiment.segment)}</dd></div>
                    <div><dt>Persona</dt><dd>{humanize(experiment.persona)}</dd></div>
                    <div><dt>Channel</dt><dd>{humanize(experiment.channel)}</dd></div>
                    <div><dt>Message</dt><dd><code>{experiment.messageVersion}</code></dd></div>
                    <div><dt>Cohort</dt><dd>{humanize(experiment.cohort)}</dd></div>
                    <div><dt>Decision point</dt><dd>{experiment.decisionDate}</dd></div>
                  </dl>
                  <dl className={styles.decisionRules}>
                    <div><dt>Expected learning</dt><dd>{experiment.expectedLearning}</dd></div>
                    <div><dt>Continue</dt><dd>{experiment.continueThreshold}</dd></div>
                    <div><dt>Change</dt><dd>{experiment.changeThreshold}</dd></div>
                    <div><dt>Stop</dt><dd>{experiment.stopThreshold}</dd></div>
                  </dl>
                  <div className={styles.experimentOutcome}>
                    <div><span>Result</span><strong>{experiment.result ?? "Not run"}</strong></div>
                    <div><span>Decision</span><strong>{experimentDecisionLabel(experiment)}</strong></div>
                  </div>
                  <SourceLink path={experiment.sourcePath} label="Open experiment source" />
                </div>
              </details>
            ))}
          </section>
        </div>
      </section>

      <section id="outcomes" className={styles.section} aria-labelledby="outcomes-title">
        <div className={styles.sectionHeading}>
          <div>
            <span>Measurement baseline</span>
            <h2 id="outcomes-title">The measurement system is defined; observed results start at zero</h2>
            <p>This is a clean baseline, not a dead end. Each empty result now has a capture method upstream.</p>
          </div>
          <SourceLink path={currentDecision.sourcePath} label="Read current state" />
        </div>
        <dl className={styles.outcomeGrid}>
          {outcomeState.map((item) => (
            <div key={item.label}>
              <dt>{item.label}</dt>
              <dd>{item.boundary}</dd>
              <strong>{item.value}</strong>
            </div>
          ))}
        </dl>
      </section>

      <section className={`${styles.section} ${styles.sourceShelf}`} aria-labelledby="source-shelf-title">
        <div className={styles.sectionHeading}>
          <div>
            <span>Knowledge layer</span>
            <h2 id="source-shelf-title">Open the source behind every decision</h2>
            <p>These summaries never replace the admitted canonical files.</p>
          </div>
          <Link className={styles.knowledgeLink} href="/knowledge">Open Knowledge map</Link>
        </div>
        <div className={styles.sourceGrid}>
          {decisionRoomSourceShelf.map((source) => (
            <SourceLink key={source.path} path={source.path} label={source.label} />
          ))}
        </div>
      </section>
    </div>
  );
}
