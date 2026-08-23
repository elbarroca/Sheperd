import Link from "next/link";
import type {
  AgentStep,
  ArticleInsight,
  ReportBullet,
  ReportPayload,
  ResearchClaim,
  ResearchSignal,
  ToolCallReceipt,
  WeeklyBrief,
  WeeklyReportSummary,
} from "@/lib/research-api";
import type { ReactNode } from "react";

function dateLabel(value: string): string {
  return new Intl.DateTimeFormat("en", { dateStyle: "medium" }).format(new Date(value));
}

function timestampLabel(value: string | null | undefined): string {
  if (!value) return "Not recorded";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "Not recorded";
  return new Intl.DateTimeFormat("en-US", {
    dateStyle: "medium",
    timeStyle: "medium",
    timeZone: "UTC",
  }).format(date);
}

function periodLabel(from: string, until: string): string {
  return `${dateLabel(from)} to ${dateLabel(until)}`;
}

function isHttpUrl(value: string): boolean {
  return value.startsWith("https://") || value.startsWith("http://");
}

function CitationLinks({ urls }: { urls: string[] }) {
  return urls.filter(isHttpUrl).map((url, index) => (
    <a key={`${url}-${index}`} href={url} target="_blank" rel="noreferrer" className="citation-link">
      Source {index + 1}
    </a>
  ));
}

function recorded(value: string | null | undefined): string {
  return value?.trim() ? value : "Not recorded in this run.";
}

function InsightBlock({ label, insight }: { label: string; insight?: ArticleInsight | null }) {
  if (!insight) {
    return <div className="insight-block"><strong>{label}</strong><p className="muted">Not recorded in this run.</p></div>;
  }
  return (
    <div className="insight-block">
      <div className="bullet-meta"><strong>{label}</strong><span className={`status-badge status-${insight.status}`}>{insight.status.replaceAll("_", " ")}</span></div>
      <p>{recorded(insight.statement)}</p>
      <p><strong>Why it matters:</strong> {recorded(insight.why_it_matters)}</p>
      <p><strong>Next step:</strong> {recorded(insight.next_step)}</p>
      {insight.evidence_excerpt ? <p className="muted">Evidence: {insight.evidence_excerpt}</p> : null}
      {insight.evidence_locator ? <p className="muted">Locator: {insight.evidence_locator}</p> : null}
    </div>
  );
}

function BulletList({ bullets, emptyLabel = "Not recorded in this run." }: { bullets: ReportBullet[]; emptyLabel?: string }) {
  if (bullets.length === 0) return <p className="muted">{emptyLabel}</p>;
  return (
    <ul className="report-bullets">
      {bullets.map((bullet, index) => (
        <li key={`${bullet.text}-${index}`}>
          <span>{bullet.text}</span>
          {bullet.why_it_matters ? <span className="bullet-context"><strong>Why it matters:</strong> {bullet.why_it_matters}</span> : null}
          {bullet.next_step ? <span className="bullet-context"><strong>Next step:</strong> {bullet.next_step}</span> : null}
          <span className="bullet-meta">
            <span className={`evidence-badge evidence-${bullet.evidence_status}`}>{bullet.evidence_status}</span>
            <CitationLinks urls={bullet.source_urls} />
          </span>
        </li>
      ))}
    </ul>
  );
}

type DecisionItem = {
  text: string;
  sourceUrls: string[];
  evidenceStatus: string;
};

function nextStepItems(brief: WeeklyBrief): DecisionItem[] {
  const seen = new Set<string>();
  return [...brief.risks, ...brief.opportunities, ...brief.uncertainties].flatMap((bullet) => {
    if (!bullet.next_step || seen.has(bullet.next_step)) return [];
    seen.add(bullet.next_step);
    return [{ text: bullet.next_step, sourceUrls: bullet.source_urls, evidenceStatus: bullet.evidence_status }];
  });
}

function DecisionList({ items, emptyLabel }: { items: DecisionItem[]; emptyLabel: string }) {
  if (items.length === 0) return <p className="muted">{emptyLabel}</p>;
  return (
    <ol className="decision-list">
      {items.slice(0, 4).map((item, index) => (
        <li key={`${item.text}-${index}`}>
          <span>{item.text}</span>
          <span className="bullet-meta">
            <span className={`evidence-badge evidence-${item.evidenceStatus}`}>{item.evidenceStatus}</span>
            <CitationLinks urls={item.sourceUrls} />
          </span>
        </li>
      ))}
    </ol>
  );
}

function DecisionReadout({ brief }: { brief: WeeklyBrief }) {
  const nextSteps = nextStepItems(brief);
  const openQuestions = brief.follow_up_questions.slice(0, 4);
  return (
    <section className="decision-readout" aria-labelledby="decision-readout-heading">
      <div className="decision-intro">
        <p className="eyebrow">Decision readout</p>
        <h2 id="decision-readout-heading">What this run tells us</h2>
        <p className="report-summary">{brief.summary}</p>
      </div>
      <div className="decision-grid">
        <article className="decision-block">
          <p className="decision-label">Next steps</p>
          <h3>What to do next</h3>
          <DecisionList items={nextSteps} emptyLabel="No next step was recorded." />
        </article>
        <article className="decision-block">
          <p className="decision-label">Open questions</p>
          <h3>What still needs checking</h3>
          {openQuestions.length > 0 ? (
            <ol className="decision-list">
              {openQuestions.map((question, index) => <li key={`${question}-${index}`}><span>{question}</span></li>)}
            </ol>
          ) : <p className="muted">No follow-up question was recorded.</p>}
        </article>
      </div>
    </section>
  );
}

function Section({ title, children, open = false }: { title: string; children: ReactNode; open?: boolean }) {
  return (
    <details className="report-section" open={open}>
      <summary>{title}</summary>
      <div className="report-section-body">{children}</div>
    </details>
  );
}

function ToolCallList({ calls }: { calls: ToolCallReceipt[] }) {
  if (calls.length === 0) return <p className="muted">No tool receipts recorded.</p>;
  return (
    <ul className="step-list">
      {calls.map((call, index) => (
        <li key={`${call.agent_name}-${call.attempt}-${call.call_index}-${index}`}>
          <span>{call.tool_name} / {call.lane ?? "unknown lane"} / attempt {call.attempt ?? "unknown"}</span>
          <span>{call.status}</span>
          <span>{call.result_count ?? "unknown"} results / {call.latency_ms ?? "unknown"} ms</span>
          <span>{call.error_code ?? "no error"}</span>
          <small>Args: {call.sanitized_args ? JSON.stringify(call.sanitized_args) : "none"}</small>
          <small>Input: {call.input_hash ?? "unknown"} / Result: {call.result_hash ?? "unknown"}</small>
        </li>
      ))}
    </ul>
  );
}

function SourceEvidence({ report }: { report: ReportPayload }) {
  return (
    <>
      <p>
        {report.sources.length} persisted sources, {report.distillations.length} distillations, {report.claims.length} claims, {report.signals.length} signals.
        Citation coverage: {Math.round((report.validation?.citation_coverage ?? 0) * 100)}%.
      </p>
      {report.sources.length > 0 && (
        <>
          <h3>Sources</h3>
          <ul className="source-list">
            {report.sources.map((source) => (
              <li key={source.url}>
                <a href={source.url} target="_blank" rel="noreferrer">{source.title}</a>
                <span className="bullet-meta">{source.publisher} / {source.region ?? "global"} / {source.language_code ?? "und"} / {source.lane} / {source.evidence_status} / {source.extraction_status ?? "unknown"}</span>
              </li>
            ))}
          </ul>
        </>
      )}
      {report.distillations.length > 0 && (
        <>
          <h3>Distillations</h3>
          <div className="evidence-grid">
            {report.distillations.map((distillation) => (
              <article className="evidence-card" key={distillation.source_url}>
                <p>{recorded(distillation.summary)}</p>
                {distillation.summary_original && distillation.summary_original !== distillation.summary ? <p className="muted">Original: {distillation.summary_original}</p> : null}
                {distillation.key_points.length > 0 ? <ul>{distillation.key_points.map((point) => <li key={point}>{point}</li>)}</ul> : <p className="muted">Key points: Not recorded in this run.</p>}
                <h4>What happened</h4>
                <p>{recorded(distillation.what_happened)}</p>
                <h4>Why it matters</h4>
                <p>{recorded(distillation.why_it_matters)}</p>
                <div className="insight-grid">
                  <InsightBlock label="Risk assessment" insight={distillation.risk_assessment} />
                  <InsightBlock label="Opportunity assessment" insight={distillation.opportunity_assessment} />
                </div>
                <h4>Next steps</h4>
                {distillation.next_steps?.length ? <ul>{distillation.next_steps.map((step) => <li key={step}>{step}</li>)}</ul> : <p className="muted">Not recorded in this run.</p>}
                <h4>Uncertainty</h4>
                {distillation.uncertainties?.length ? <ul>{distillation.uncertainties.map((item) => <li key={item}>{item}</li>)}</ul> : <p className="muted">Not recorded in this run.</p>}
                {distillation.entities.length > 0 ? <p className="muted">Entities: {distillation.entities.join(", ")}</p> : null}
                {distillation.signals.length > 0 ? <p className="muted">Signals: {distillation.signals.join(", ")}</p> : null}
                {distillation.evidence_excerpts?.length ? <p className="muted">Evidence: {distillation.evidence_excerpts.join(" / ")}</p> : <p className="muted">Evidence excerpts: Not recorded in this run.</p>}
                {distillation.evidence_locators?.length ? <p className="muted">Locators: {distillation.evidence_locators.join(" / ")}</p> : <p className="muted">Evidence locators: Not recorded in this run.</p>}
                <p className="muted">{distillation.model_id} / {distillation.prompt_version} / {distillation.evidence_status} / language {distillation.source_language ?? "und"} / translation {distillation.translation_status ?? "unknown"} / quality {distillation.quality_status ?? "incomplete"}</p>
                {distillation.quality_issues?.length ? <p className="muted">Quality issues: {distillation.quality_issues.join(", ")}</p> : null}
                {report.quality?.article_fulfillment ? (() => {
                  const fulfillment = report.quality.article_fulfillment.find((item) => item.source_url === distillation.source_url);
                  return fulfillment ? <p className="muted">Fulfillment: {fulfillment.status} · {fulfillment.claim_count} claims · {fulfillment.citation_count} cited · UI {fulfillment.ui_displayable ? "ready" : "not ready"}{fulfillment.missing_fields.length ? ` · missing ${fulfillment.missing_fields.join(", ")}` : ""}</p> : null;
                })() : null}
                <code>Hash: {distillation.content_hash ?? "unknown"}</code>
                {distillation.claims.length > 0 ? <ul>{distillation.claims.map((claim) => <ClaimRow key={claim.claim} claim={claim} />)}</ul> : <p className="muted">Claims: Not recorded in this run.</p>}
              </article>
            ))}
          </div>
        </>
      )}
      {report.claims.length > 0 ? (
        <>
          <h3>Claims and citations</h3>
          <ul className="source-list">{report.claims.map((claim) => <ClaimRow key={claim.claim} claim={claim} />)}</ul>
        </>
      ) : <p className="muted">Claims and citations: Not recorded in this run.</p>}
      {report.signals.length > 0 && (
        <>
          <h3>Signals</h3>
          <ul className="source-list">{report.signals.map((signal) => <SignalRow key={signal.event_id} signal={signal} />)}</ul>
        </>
      )}
      <p className="muted">Source snapshot hashes: {report.source_hashes.length ? report.source_hashes.join(", ") : "none recorded"}</p>
      <ul className="source-list">
        {briefSourceUrls(report.brief).map((url) => <li key={url}><a href={url} target="_blank" rel="noreferrer">{url}</a></li>)}
      </ul>
      {report.brief.limitations.length > 0 && <><h3>Limitations</h3><ul>{report.brief.limitations.map((item) => <li key={item}>{item}</li>)}</ul></>}
    </>
  );
}

function ReportQuality({ report, brief }: { report: ReportPayload; brief: WeeklyBrief }) {
  const sections = [
    ["Executive", brief.executive_bullets],
    ["Developments", brief.developments],
    ["Risks", brief.risks],
    ["Opportunities", brief.opportunities],
    ["Uncertainty", brief.uncertainties],
  ] as const;
  const completeSections = report.quality?.report_sections_complete
    ?? sections.filter(([, bullets]) => bullets.length > 0).length;
  const coverage = Math.round((report.validation?.citation_coverage ?? 0) * 100);
  const sectionCheck = report.validation?.checks.find((check) => check.name === "report_sections");
  const sectionComplete = report.quality?.report_section_completeness === 1
    && sectionCheck?.status !== "failed";
  const completeArticles = report.quality?.complete_article_count
    ?? report.distillations.filter((item) => item.quality_status === "complete").length;
  const articleCount = report.quality?.article_count ?? report.distillations.length;
  return (
    <div className="report-quality" aria-label="Report quality">
      <div><strong>{completeSections}/{sections.length}</strong><span>insight sections</span></div>
      <div><strong>{coverage}%</strong><span>citation coverage</span></div>
      <div><strong>{report.sources.length}</strong><span>sources</span></div>
      <div><strong>{report.distillations.length}</strong><span>distillations</span></div>
      <div><strong>{report.claims.length}</strong><span>claims</span></div>
      <div><strong>{completeArticles}/{articleCount}</strong><span>complete article insights</span></div>
      <div><strong>{sectionCheck?.status ?? "not recorded"}</strong><span>section validator</span></div>
      <p>{report.readiness_status === "decision_ready" && sectionComplete
        ? "All required insight sections and article packets are complete."
        : "This run requires review before it can be decision-ready."}</p>
      {!report.quality ? <p className="muted">Legacy quality snapshot: Not recorded in this run.</p> : null}
      {report.blocking_reasons?.length ? <p className="muted">Blocking reasons: {report.blocking_reasons.join(", ")}</p> : null}
    </div>
  );
}

function briefSourceUrls(brief: WeeklyBrief): string[] {
  return brief.source_urls.filter(isHttpUrl);
}

function ClaimRow({ claim }: { claim: ResearchClaim }) {
  return (
    <li>
      <span>{claim.claim}{claim.evidence_excerpt ? `: ${claim.evidence_excerpt}` : ""}</span>
      <span className="bullet-meta"><span className={`evidence-badge evidence-${claim.evidence_status}`}>{claim.evidence_status}</span><CitationLinks urls={claim.source_urls} /></span>
    </li>
  );
}

function SignalRow({ signal }: { signal: ResearchSignal }) {
  return (
    <li>
      <span>{signal.event_type}: {signal.summary}</span>
      <span className="bullet-meta"><span className={`evidence-badge evidence-${signal.evidence_status}`}>{signal.evidence_status}</span><CitationLinks urls={signal.source_urls} /></span>
    </li>
  );
}

function AgentStepList({ steps }: { steps: AgentStep[] }) {
  if (steps.length === 0) return <p className="muted">No agent steps recorded.</p>;
  return (
    <ul className="step-list">
      {steps.map((step) => (
        <li key={`${step.agent_name}-${step.attempt}`}>
          <strong>{step.agent_name} / {step.lane} / attempt {step.attempt}</strong>
          <span>{step.status} / {step.duration_ms ?? "unknown"} ms</span>
          <span>{step.requested_model ?? "unknown"} to {step.resolved_model ?? "unknown"}</span>
          <span>{step.prompt_version ?? "unknown"} / {step.total_tokens ?? "unknown"} tokens</span>
          <small>{timestampLabel(step.created_at)} / Input: {step.input_hash ?? "unknown"} / Output: {step.output_hash ?? "unknown"} / Error: {step.error_code ?? "none"}</small>
        </li>
      ))}
    </ul>
  );
}

type ActivityItem = {
  id: string;
  createdAt: string | null;
  title: string;
  status: string;
  detail: string;
};

function RunActivity({ steps, calls }: { steps: AgentStep[]; calls: ToolCallReceipt[] }) {
  const items: ActivityItem[] = [
    ...steps.map((step, index) => ({
      id: `step-${step.agent_name}-${step.attempt}-${index}`,
      createdAt: step.created_at ?? null,
      title: step.agent_name,
      status: step.status,
      detail: `${step.lane} / attempt ${step.attempt} / ${step.tool_calls ?? 0} tool calls / ${step.duration_ms ?? "unknown"} ms${step.fallback_reason ? ` / rerouted: ${step.fallback_reason}` : ""}`,
    })),
    ...calls.map((call, index) => ({
      id: `tool-${call.tool_name}-${call.attempt ?? "unknown"}-${index}`,
      createdAt: call.created_at ?? null,
      title: call.tool_name,
      status: call.status,
      detail: `${call.lane ?? "unknown lane"} / ${call.result_count ?? 0} results / ${call.latency_ms ?? "unknown"} ms`,
    })),
  ].sort((left, right) => {
    const leftTime = left.createdAt ? Date.parse(left.createdAt) : Number.MAX_SAFE_INTEGER;
    const rightTime = right.createdAt ? Date.parse(right.createdAt) : Number.MAX_SAFE_INTEGER;
    return leftTime - rightTime;
  });

  if (items.length === 0) return <p className="muted">No persisted activity recorded.</p>;
  return (
    <ol className="activity-list">
      {items.map((item) => (
        <li className="activity-item" key={item.id}>
          <time dateTime={item.createdAt ?? undefined}>{timestampLabel(item.createdAt)}</time>
          <span className="activity-event"><strong>{item.title}</strong><small>{item.detail}</small></span>
          <span className={`status-badge status-${item.status}`}>{item.status}</span>
        </li>
      ))}
    </ol>
  );
}

export function ReportAccordion({ report }: { report: ReportPayload }) {
  const brief: WeeklyBrief = report.brief;
  const checks = report.validation?.checks ?? [];
  const runStatus = report.run?.status ?? "missing";
  const validationStatus = report.validation?.status ?? "missing";
  const blocked = !(
    report.readiness_status === "decision_ready"
    && runStatus === "succeeded"
    && validationStatus === "pass"
  );
  const headingLabel = report.run?.archived
    ? "Archived report"
    : blocked
      ? "Review required"
      : "Decision-ready report";
  const workflowStates = ["critic", "synthesis", "validation"].map((agentName) => ({
    agentName,
    step: report.steps.find((item) => item.agent_name === agentName),
  }));
  return (
    <div className="report-stack">
      <div className="report-heading">
        <div>
          <p className="eyebrow">{headingLabel}</p>
          <h1>{brief.title}</h1>
          <p className="report-period">{periodLabel(brief.covered_from, brief.covered_until)}</p>
          <p className="report-as-of">As of {timestampLabel(report.as_of)}</p>
        </div>
        <div className="status-cluster">
          {report.run?.archived ? <span className="status-badge status-archived">Archived</span> : null}
          <span className={`status-badge status-${report.run?.status ?? "unknown"}`}>{report.run?.status ?? "unknown"}</span>
          <span className={`status-badge status-${report.validation?.status ?? "blocked"}`}>{report.validation?.status ?? "blocked"}</span>
          <a className="secondary-action" href={`/reports/${encodeURIComponent(brief.run_id)}/markdown${report.run?.archived ? "?archive_scope=archived" : ""}`}>
            Download Markdown
          </a>
        </div>
      </div>

      {report.run?.archived ? (
        <div className="archive-notice" role="status">
          Archived from the default dashboard. Reason: {report.run.archive_reason ?? "terminal failure"}.
        </div>
      ) : null}

      {blocked && (
        <div className="unavailable" role="alert">
          <strong>Report is blocked, failed, or partial.</strong>
          <p>Run status: {runStatus}. Validation status: {validationStatus}. {report.run?.error ?? "This report is not decision-ready."}</p>
        </div>
      )}

      <DecisionReadout brief={brief} />
      <Section title="1. Executive findings" open><BulletList bullets={brief.executive_bullets} /></Section>
      <Section title="2. Developments by lane and geography">
        <BulletList bullets={brief.developments} />
        <p className="lane-line">Coverage: {report.lane_coverage.join(", ") || "none recorded"}</p>
      </Section>
      <ReportQuality report={report} brief={brief} />
      <Section title="3. Risks / exposure and impact"><BulletList bullets={brief.risks} emptyLabel="No structured risk insight was recorded in this run." /></Section>
      <Section title="4. Opportunities / openings and next moves"><BulletList bullets={brief.opportunities} emptyLabel="No structured opportunity insight was recorded in this run." /></Section>
      <Section title="5. Uncertainty and follow-up research">
        <BulletList bullets={brief.uncertainties} emptyLabel="No structured uncertainty insight was recorded in this run." />
        {brief.follow_up_questions.length > 0 ? (
          <ol className="follow-up-list">{brief.follow_up_questions.map((question) => <li key={question}>{question}</li>)}</ol>
        ) : <p className="muted">No follow-up questions recorded.</p>}
      </Section>
      <Section title="6. Evidence and citations">
        <SourceEvidence report={report} />
      </Section>
      <Section title="7. Agent audit">
        <h3>Run activity</h3>
        <p className="muted">Persisted workflow steps and provider tool receipts. Hidden reasoning is never stored.</p>
        <RunActivity steps={report.steps} calls={report.tool_calls ?? []} />
        <dl className="audit-grid">
          <div><dt>Run</dt><dd><code>{brief.run_id}</code></dd></div>
          <div><dt>Requested model(s)</dt><dd>{report.requested_models?.join(", ") || brief.model_id}</dd></div>
          <div><dt>Resolved model(s)</dt><dd>{report.resolved_models?.join(", ") || report.models.join(", ") || brief.model_id}</dd></div>
          <div><dt>Prompt</dt><dd>{brief.prompt_version}</dd></div>
          <div><dt>As of</dt><dd>{timestampLabel(report.as_of)}</dd></div>
          <div><dt>Branch</dt><dd>{report.run?.neon_branch_id ?? "unknown"}</dd></div>
          <div><dt>Migration</dt><dd>{report.run?.migration_version ?? "unknown"}</dd></div>
          <div><dt>Source hashes</dt><dd>{report.source_hashes.length}</dd></div>
        </dl>
        <h3>Workflow states</h3>
        <ul className="check-list">{workflowStates.map(({ agentName, step }) => <li key={agentName}><span>{agentName}</span><span>{step?.status ?? "not recorded"}</span></li>)}</ul>
        <AgentStepList steps={report.steps} />
        <h3>Tool receipts ({report.tool_calls?.length ?? 0})</h3>
        <ToolCallList calls={report.tool_calls ?? []} />
        {checks.length > 0 && <ul className="check-list">{checks.map((check) => <li key={check.name}><span>{check.name}</span><span>{check.status}</span></li>)}</ul>}
      </Section>
    </div>
  );
}

export function UnavailableState({ error }: { error: string }) {
  return <div className="unavailable" role="alert"><h1>Research API unavailable</h1><p>{error}. Start the FastAPI service at 127.0.0.1:8787 for local development. Production uses the configured research API. No stale report data is shown.</p></div>;
}

export function ReportLink({ runId, summary }: { runId: string; summary: WeeklyReportSummary }) {
  const ready = summary.decision_ready === true || summary.readiness_status === "decision_ready";
  const archived = summary.archived === true || summary.archived_at != null;
  const href = `/reports/${encodeURIComponent(runId)}${archived ? "?archive_scope=archived" : ""}`;
  return (
    <Link className="report-row" href={href}>
      <span className="report-row-title">
        <span className="eyebrow">{archived ? "Archived" : ready ? "Decision-ready" : `${summary.run_status} / ${summary.validation_status}`}</span>
        <strong>{summary.title}</strong>
      </span>
      <span className="report-row-period">{periodLabel(summary.covered_from, summary.covered_until)}</span>
      <span className="report-row-metrics">
        <span>{summary.source_count} sources</span>
        <span>{summary.distillation_count} distillations</span>
        <span>{summary.claim_count} claims</span>
      </span>
      <span className="report-row-state">
        {archived ? summary.archive_reason ?? "archived" : `${summary.validation_status} / ${summary.review_state}`}
      </span>
      <span className="card-arrow">Open report</span>
    </Link>
  );
}
