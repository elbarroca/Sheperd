import Link from "next/link";
import type {
  AgentStep,
  ReportBullet,
  ReportPayload,
  ResearchClaim,
  ResearchSignal,
  ToolCallReceipt,
  WeeklyBrief,
} from "@/lib/research-api";
import type { ReactNode } from "react";

function dateLabel(value: string): string {
  return new Intl.DateTimeFormat("en", { dateStyle: "medium" }).format(new Date(value));
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
          <span>{call.tool_name} · {call.lane ?? "unknown lane"} · attempt {call.attempt ?? "—"}</span>
          <span>{call.status}</span>
          <span>{call.result_count ?? "—"} results · {call.latency_ms ?? "—"} ms</span>
          <span>{call.error_code ?? "no error"}</span>
          <small>Args: {call.sanitized_args ? JSON.stringify(call.sanitized_args) : "none"}</small>
          <small>Input: {call.input_hash ?? "—"} · Result: {call.result_hash ?? "—"}</small>
        </li>
      ))}
    </ul>
  );
}

function SourceEvidence({ report }: { report: ReportPayload }) {
  return (
    <>
      <p>
        {report.sources.length} persisted sources · {report.distillations.length} distillations · {report.claims.length} claims · {report.signals.length} signals.
        Citation coverage: {Math.round((report.validation?.citation_coverage ?? 0) * 100)}%.
      </p>
      {report.sources.length > 0 && (
        <>
          <h3>Sources</h3>
          <ul className="source-list">
            {report.sources.map((source) => (
              <li key={source.url}>
                <a href={source.url} target="_blank" rel="noreferrer">{source.title}</a>
                <span className="bullet-meta">{source.publisher} · {source.lane} · {source.evidence_status}</span>
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
                {distillation.key_points.length > 0 && <ul>{distillation.key_points.map((point) => <li key={point}>{point}</li>)}</ul>}
                <p className="muted">{distillation.model_id} · {distillation.prompt_version} · {distillation.evidence_status}</p>
                <code>Hash: {distillation.content_hash ?? "—"}</code>
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
      <p className="muted">Source snapshot hashes: {report.source_hashes.length ? report.source_hashes.join(" · ") : "none recorded"}</p>
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
      <span>{claim.claim}</span>
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
          <strong>{step.agent_name} · {step.lane} · attempt {step.attempt}</strong>
          <span>{step.status} · {step.duration_ms ?? "—"} ms</span>
          <span>{step.requested_model ?? "—"} → {step.resolved_model ?? "—"}</span>
          <span>{step.prompt_version ?? "—"} · {step.total_tokens ?? "—"} tokens</span>
          <small>Input: {step.input_hash ?? "—"} · Output: {step.output_hash ?? "—"} · Error: {step.error_code ?? "none"}</small>
        </li>
      ))}
    </ul>
  );
}

export function ReportAccordion({ report }: { report: ReportPayload }) {
  const brief: WeeklyBrief = report.brief;
  const checks = report.validation?.checks ?? [];
  const validationStatus = report.validation?.status ?? "blocked";
  const blocked =
    report.run?.status === "failed" ||
    validationStatus === "blocked" ||
    validationStatus === "failed";
  const workflowStates = ["critic", "synthesis", "validation"].map((agentName) => ({
    agentName,
    step: report.steps.find((item) => item.agent_name === agentName),
  }));
  return (
    <div className="report-stack">
      <div className="report-heading">
        <div>
          <p className="eyebrow">Weekly intelligence · Draft</p>
          <h1>{brief.title}</h1>
          <p className="report-period">{dateLabel(brief.covered_from)} – {dateLabel(brief.covered_until)}</p>
        </div>
        <div className="status-cluster">
          <span className={`status-badge status-${report.run?.status ?? "unknown"}`}>{report.run?.status ?? "unknown"}</span>
          <span className={`status-badge status-${report.validation?.status ?? "blocked"}`}>{report.validation?.status ?? "blocked"}</span>
        </div>
      </div>

      {blocked && (
        <div className="unavailable" role="alert">
          <strong>Run is blocked or failed.</strong>
          <p>{report.run?.error ?? "Validation did not pass; this report is not decision-ready."}</p>
        </div>
      )}

      <Section title="1. Executive readout" open>
        <p className="report-summary">{brief.summary}</p>
        <BulletList bullets={brief.executive_bullets} />
      </Section>
      <Section title="2. Developments by lane and geography">
        <BulletList bullets={brief.developments} />
        <p className="lane-line">Coverage: {report.lane_coverage.join(" · ") || "none recorded"}</p>
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
        <dl className="audit-grid">
          <div><dt>Run</dt><dd><code>{brief.run_id}</code></dd></div>
          <div><dt>Requested model(s)</dt><dd>{report.requested_models?.join(", ") || brief.model_id}</dd></div>
          <div><dt>Resolved model(s)</dt><dd>{report.resolved_models?.join(", ") || report.models.join(", ") || brief.model_id}</dd></div>
          <div><dt>Prompt</dt><dd>{brief.prompt_version}</dd></div>
          <div><dt>As of</dt><dd>{dateLabel(report.as_of)}</dd></div>
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
  return <div className="unavailable" role="alert"><h1>Research API unavailable</h1><p>{error}. Start the local FastAPI dashboard and reload. No stale report data is shown.</p></div>;
}

export function ReportLink({ runId, title, period }: { runId: string; title: string; period: string }) {
  return <Link className="report-card" href={`/reports/${encodeURIComponent(runId)}`}><span className="eyebrow">Weekly draft</span><h2>{title}</h2><p>{period}</p><span className="card-arrow">Open report →</span></Link>;
}
