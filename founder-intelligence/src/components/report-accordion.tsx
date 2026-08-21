import Link from "next/link";
import type {
  AgentStep,
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

function BulletList({ bullets }: { bullets: ReportBullet[] }) {
  if (bullets.length === 0) return <p className="muted">No observations recorded.</p>;
  return (
    <ul className="report-bullets">
      {bullets.map((bullet, index) => (
        <li key={`${bullet.text}-${index}`}>
          <span>{bullet.text}</span>
          <span className="bullet-meta">
            <span className={`evidence-badge evidence-${bullet.evidence_status}`}>{bullet.evidence_status}</span>
            <CitationLinks urls={bullet.source_urls} />
          </span>
        </li>
      ))}
    </ul>
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
                <p>{distillation.summary}</p>
                {distillation.summary_original && distillation.summary_original !== distillation.summary ? <p className="muted">Original: {distillation.summary_original}</p> : null}
                {distillation.key_points.length > 0 && <ul>{distillation.key_points.map((point) => <li key={point}>{point}</li>)}</ul>}
                <p className="muted">{distillation.model_id} / {distillation.prompt_version} / {distillation.evidence_status} / language {distillation.source_language ?? "und"} / translation {distillation.translation_status ?? "unknown"}</p>
                <code>Hash: {distillation.content_hash ?? "unknown"}</code>
                {distillation.claims.length > 0 && <ul>{distillation.claims.map((claim) => <ClaimRow key={claim.claim} claim={claim} />)}</ul>}
              </article>
            ))}
          </div>
        </>
      )}
      {report.claims.length > 0 && (
        <>
          <h3>Claims and citations</h3>
          <ul className="source-list">{report.claims.map((claim) => <ClaimRow key={claim.claim} claim={claim} />)}</ul>
        </>
      )}
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
  const blocked = !(runStatus === "succeeded" && validationStatus === "pass");
  const workflowStates = ["critic", "synthesis", "validation"].map((agentName) => ({
    agentName,
    step: report.steps.find((item) => item.agent_name === agentName),
  }));
  return (
    <div className="report-stack">
      <div className="report-heading">
        <div>
          <p className="eyebrow">Weekly intelligence / draft</p>
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

      <Section title="1. Executive readout" open>
        <p className="report-summary">{brief.summary}</p>
        <BulletList bullets={brief.executive_bullets} />
      </Section>
      <Section title="2. Developments by lane and geography">
        <BulletList bullets={brief.developments} />
        <p className="lane-line">Coverage: {report.lane_coverage.join(", ") || "none recorded"}</p>
      </Section>
      <Section title="3. Risks"><BulletList bullets={brief.risks} /></Section>
      <Section title="4. Opportunities"><BulletList bullets={brief.opportunities} /></Section>
      <Section title="5. Uncertainty and follow-up research">
        <BulletList bullets={brief.uncertainties} />
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
  const ready = summary.run_status === "succeeded" && summary.validation_status === "pass";
  const archived = summary.archived === true || summary.archived_at != null;
  const href = `/reports/${encodeURIComponent(runId)}${archived ? "?archive_scope=archived" : ""}`;
  return (
    <Link className="report-row" href={href}>
      <span className="report-row-title">
        <span className="eyebrow">{archived ? "Archived" : ready ? "Decision-ready" : `${summary.run_status} · ${summary.validation_status}`}</span>
        <strong>{summary.title}</strong>
      </span>
      <span className="report-row-period">{periodLabel(summary.covered_from, summary.covered_until)}</span>
      <span className="report-row-metrics">
        {summary.source_count} sources · {summary.distillation_count} distillations · {summary.claim_count} claims
      </span>
      <span className="report-row-state">
        {archived ? summary.archive_reason ?? "archived" : `${summary.validation_status} · ${summary.review_state}`}
      </span>
      <span className="card-arrow">Open report →</span>
    </Link>
  );
}
