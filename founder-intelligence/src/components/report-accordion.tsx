import Link from "next/link";
import { isDecisionReadySummary, readinessSummaryFromReport } from "../lib/readiness";
import type {
  AgentStep,
  ArticleInsight,
  ReaderArticle,
  ReportBullet,
  ReportPayload,
  ResearchClaim,
  ResearchSignal,
  ResearchSource,
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

function codeLabel(value: string | null | undefined): string {
  return value?.replaceAll("_", " ") ?? "not recorded";
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

function EvidenceTable({
  sources,
  hashes,
}: {
  sources: ResearchSource[];
  hashes: Record<string, string>;
}) {
  if (sources.length === 0) return <p className="muted">No sources recorded.</p>;
  return (
    <div className="evidence-table-wrap">
      <table className="evidence-table">
        <thead><tr><th>Source</th><th>Published</th><th>Period</th><th>Eligible</th><th>Snapshot hash</th></tr></thead>
        <tbody>
          {sources.map((source) => (
            <tr key={source.url}>
              <td><a href={source.url} target="_blank" rel="noreferrer">{source.title.trim() || "Untitled source"}</a><small>{source.publisher || "Unknown publisher"} / {source.region ?? "global"} / {source.lane}</small></td>
              <td>{source.published_at ? dateLabel(source.published_at) : "Undated"}</td>
              <td>{codeLabel(source.period_status)}</td>
              <td>{source.eligible_for_weekly ? "Yes" : "No"}</td>
              <td><code>{hashes[source.url] ?? "not recorded"}</code></td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function EventTimeline({ title, signals }: { title: string; signals: ResearchSignal[] }) {
  return (
    <div className="event-timeline">
      <h3>{title}</h3>
      {signals.length > 0
        ? <ol className="source-list">{signals.map((signal) => <SignalRow key={signal.event_id} signal={signal} />)}</ol>
        : <p className="muted">No events recorded.</p>}
    </div>
  );
}

function SourceEvidence({ report }: { report: ReportPayload }) {
  const currentSources = report.sources.filter((source) => source.eligible_for_weekly && source.period_status === "in_period");
  const backgroundSources = report.sources.filter((source) => !source.eligible_for_weekly || source.period_status !== "in_period");
  const currentSignals = report.signals.filter((signal) => signal.eligible_for_weekly && signal.period_status === "in_period");
  const backgroundSignals = report.signals.filter((signal) => !signal.eligible_for_weekly || signal.period_status !== "in_period");
  return (
    <>
      <p>
        {report.sources.length} persisted sources, {report.distillations.length} distillations, {report.claims.length} claims, {report.signals.length} signals.
        Citation coverage: {Math.round((report.validation?.citation_coverage ?? 0) * 100)}%.
      </p>
      <EventTimeline title="Current event timeline" signals={currentSignals} />
      <EventTimeline title="Background event timeline" signals={backgroundSignals} />
      <h3>Current-week evidence</h3>
      <EvidenceTable sources={currentSources} hashes={report.source_hash_by_url} />
      <h3>Background context</h3>
      <EvidenceTable sources={backgroundSources} hashes={report.source_hash_by_url} />
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
      <p className="muted">Source snapshot hashes: {report.source_hashes.length ? report.source_hashes.join(", ") : "none recorded"}</p>
      <ul className="source-list">
        {briefSourceUrls(report.brief).map((url) => <li key={url}><a href={url} target="_blank" rel="noreferrer">{url}</a></li>)}
      </ul>
      {report.brief.limitations.length > 0 && <><h3>Limitations</h3><ul>{report.brief.limitations.map((item) => <li key={item}>{item}</li>)}</ul></>}
    </>
  );
}

type ScoreComponent = "sheperd_relevance" | "operational_impact" | "actionability" | "recency" | "source_authority";

const SCORE_COMPONENTS: Array<[ScoreComponent, string, number]> = [
  ["sheperd_relevance", "SheperD relevance", 30],
  ["operational_impact", "Operational impact", 25],
  ["actionability", "Actionability", 20],
  ["recency", "Recency", 15],
  ["source_authority", "Source authority", 10],
];

function ScoreBreakdown({ article }: { article: ReaderArticle }) {
  if (!article.score) return <p className="muted">Priority score not recorded.</p>;
  return (
    <dl className="reader-score-breakdown" aria-label="Priority score breakdown">
      {SCORE_COMPONENTS.map(([field, label, maximum]) => (
        <div key={field}>
          <dt>{label}</dt>
          <dd>{article.score?.[field]}/{maximum}</dd>
        </div>
      ))}
    </dl>
  );
}

function ReaderArticleCard({ article, rank }: { article: ReaderArticle; rank: number }) {
  return (
    <article className="reader-article">
      <header className="reader-article-heading">
        <div>
          <p className="eyebrow">#{rank} · {article.publisher}</p>
          <h3>{article.headline}</h3>
          <p className="reader-meta">
            Published {article.published_at ? dateLabel(article.published_at) : "undated"}
            {article.event_at ? ` · Event ${dateLabel(article.event_at)}` : ""}
            {` · ${codeLabel(article.date_basis)} · ${codeLabel(article.lane)} · ${codeLabel(article.region)}`}
          </p>
        </div>
        <strong className="reader-priority">
          Priority {article.score ? `${article.score.total}/100` : "not scored"}
        </strong>
      </header>
      <ScoreBreakdown article={article} />
      <section className="reader-card-section">
        <h4>Three key points</h4>
        <ul>{article.key_points.map((point) => <li key={point}>{point}</li>)}</ul>
      </section>
      <div className="reader-card-grid">
        <section className="reader-card-section"><h4>What changed</h4><p>{article.what_changed}</p></section>
        <section className="reader-card-section"><h4>Why SheperD cares</h4><p>{article.why_sheperd_cares}</p></section>
      </div>
      <section className="reader-card-section reader-action">
        <h4>Recommended action</h4>
        <p>{article.recommended_action}</p>
      </section>
      {article.risk || article.opportunity ? (
        <div className="reader-card-grid">
          {article.risk ? <section className="reader-card-section"><h4>Supported risk</h4><p>{article.risk}</p></section> : null}
          {article.opportunity ? <section className="reader-card-section"><h4>Supported opportunity</h4><p>{article.opportunity}</p></section> : null}
        </div>
      ) : null}
      {article.limitations.length > 0 ? <p className="reader-limitations"><strong>Limitations:</strong> {article.limitations.join(" ")}</p> : null}
      <a href={article.source_url} target="_blank" rel="noreferrer">Read source</a>
    </article>
  );
}

function ReaderCompactList({ title, articles }: { title: string; articles: ReaderArticle[] }) {
  return (
    <section className="reader-compact-list">
      <h2>{title}</h2>
      {articles.length > 0 ? (
        <ul>
          {articles.map((article) => (
            <li key={article.source_url}>
              <a href={article.source_url} target="_blank" rel="noreferrer">{article.headline}</a>
              <span>{article.publisher} · {article.published_at ? dateLabel(article.published_at) : "Undated"} · {codeLabel(article.validation_status)}</span>
            </li>
          ))}
        </ul>
      ) : <p className="muted">None recorded.</p>}
    </section>
  );
}

function ReaderReportView({ report }: { report: ReportPayload }) {
  const reader = report.reader_report;
  return (
    <section className="reader-report" aria-labelledby="reader-report-title">
      <div className="reader-overview">
        <div>
          <p className="eyebrow">Reader brief</p>
          <h2 id="reader-report-title">Three things to know</h2>
          {reader.three_things.length > 0
            ? <ol>{reader.three_things.map((item) => <li key={item}>{item}</li>)}</ol>
            : <p className="muted">No validated current-week findings.</p>}
        </div>
        <aside className="reader-top-action">
          <p className="eyebrow">Top action</p>
          <p>{reader.top_action}</p>
          <span className={`status-badge status-${reader.validation_status}`}>{codeLabel(reader.validation_status)}</span>
        </aside>
      </div>
      <div className="reader-ranked-articles">
        {reader.ranked_articles.map((article, index) => (
          <ReaderArticleCard key={article.source_url} article={article} rank={index + 1} />
        ))}
      </div>
      {reader.ranked_articles.length === 0 ? <p className="muted">No validated current-week articles.</p> : null}
      <div className="reader-secondary-grid">
        <ReaderCompactList title="Watchlist" articles={reader.watchlist} />
        <ReaderCompactList title="Background context" articles={reader.background_articles} />
      </div>
      <section className="reader-source-index">
        <h2>Source index and validation</h2>
        {reader.source_index.length > 0 ? (
          <div className="evidence-table-wrap">
            <table className="evidence-table">
              <thead><tr><th>Source</th><th>Published</th><th>Date basis</th><th>Page</th><th>Use</th><th>Validation</th></tr></thead>
              <tbody>{reader.source_index.map((source) => (
                <tr key={source.url}>
                  <td><a href={source.url} target="_blank" rel="noreferrer">{source.title}</a><small>{source.publisher}</small></td>
                  <td>{source.published_at ? dateLabel(source.published_at) : "Undated"}</td>
                  <td>{codeLabel(source.date_basis)}</td>
                  <td>{codeLabel(source.page_type)}</td>
                  <td>{source.eligible_for_weekly ? "Current" : "Background"}</td>
                  <td>{codeLabel(source.validation_status)}</td>
                </tr>
              ))}</tbody>
            </table>
          </div>
        ) : <p className="muted">No sources recorded.</p>}
      </section>
    </section>
  );
}

function ReportQuality({ report }: { report: ReportPayload }) {
  const completeSections = report.quality?.report_sections_complete;
  const sectionCount = report.quality?.report_section_count;
  const coverage = Math.round((report.validation?.citation_coverage ?? 0) * 100);
  const sectionCheck = report.validation?.checks.find((check) => check.name === "report_sections");
  const decisionReady = isDecisionReadySummary(readinessSummaryFromReport(report));
  const completeArticles = report.quality?.complete_article_count;
  const articleCount = report.quality?.article_count;
  return (
    <section className={`report-quality ${decisionReady ? "is-ready" : "is-review"}`} aria-label="Report quality">
      <div className="quality-heading">
        <div className="quality-title"><p className="eyebrow">Readiness</p><strong>{decisionReady ? "Decision-ready" : "Review required"}</strong></div>
        <span className={`status-badge status-${decisionReady ? "pass" : "blocked"}`}>{decisionReady ? "Pass" : "Not ready"}</span>
      </div>
      <div className="quality-metrics">
        <div><strong>{completeSections === undefined || sectionCount === undefined ? "not recorded" : `${completeSections}/${sectionCount}`}</strong><span>report sections</span></div>
        <div><strong>{coverage}%</strong><span>citation coverage</span></div>
        <div><strong>{report.sources.length}</strong><span>sources</span></div>
        <div><strong>{report.distillations.length}</strong><span>distillations</span></div>
        <div><strong>{report.claims.length}</strong><span>claims</span></div>
        <div><strong>{completeArticles === undefined || articleCount === undefined ? "not recorded" : `${completeArticles}/${articleCount}`}</strong><span>article packets</span></div>
        <div><strong>{sectionCheck?.status ?? "not recorded"}</strong><span>section validator</span></div>
      </div>
      <p>{decisionReady
        ? "All required insight sections and article packets are complete."
        : "This run requires review before it can be decision-ready."}</p>
      {!report.quality ? <p className="muted">Legacy quality snapshot: Not recorded in this run.</p> : null}
      {report.blocking_reasons?.length ? <p className="muted">Blocking reasons: {report.blocking_reasons.join(", ")}</p> : null}
      {report.quality?.report_quality_issues.length ? <p className="muted">Report quality issues: {report.quality.report_quality_issues.join(", ")}</p> : null}
      {report.quality?.article_quality_issues && Object.keys(report.quality.article_quality_issues).length > 0 ? <p className="muted">Article quality issues recorded for {Object.keys(report.quality.article_quality_issues).length} source(s).</p> : null}
      </section>
  );
}

function briefSourceUrls(brief: WeeklyBrief): string[] {
  return brief.source_urls.filter(isHttpUrl);
}

function ClaimRow({ claim }: { claim: ResearchClaim }) {
  return (
    <li>
      <span>{claim.claim || claim.original_claim || "Not recorded in this run."}{claim.evidence_excerpt ? `: ${claim.evidence_excerpt}` : ""}</span>
      {claim.original_claim && claim.original_claim !== claim.claim ? <small className="muted">Original: {claim.original_claim}</small> : null}
      <span className="bullet-meta"><span className={`evidence-badge evidence-${claim.evidence_status}`}>{claim.evidence_status}</span><span>Confidence: {claim.confidence || "not recorded"}</span><span>{claim.independent_source_count ?? 0} independent sources</span><CitationLinks urls={claim.source_urls} /></span>
      {claim.citation_status ? <small className="muted">Citation: {claim.citation_status}</small> : null}
      {claim.verification_basis ? <small className="muted">Verification basis: {claim.verification_basis}</small> : null}
      {claim.support_locator ? <small className="muted">Locator: {claim.support_locator}</small> : null}
      {claim.conflicts.length > 0 ? <small className="muted">Conflicts: {claim.conflicts.join("; ")}</small> : null}
    </li>
  );
}

function SignalRow({ signal }: { signal: ResearchSignal }) {
  return (
    <li>
      <strong>{recorded(signal.headline)}</strong>
      <span>{signal.what_changed || signal.summary}</span>
      {signal.summary !== signal.what_changed ? <small className="muted">{signal.summary}</small> : null}
      <span className="bullet-meta"><span className={`evidence-badge evidence-${signal.evidence_status}`}>{signal.evidence_status}</span><span>Event: {timestampLabel(signal.event_at ?? signal.published_at)}</span><span>{signal.region || "region not recorded"} / {signal.lane || "lane not recorded"}</span><span>{codeLabel(signal.period_status)} / {signal.eligible_for_weekly ? "eligible" : "background"}</span><CitationLinks urls={signal.source_urls} /></span>
      <small><strong>Impact:</strong> {recorded(signal.impact)}</small>
      <small><strong>Risk:</strong> {recorded(signal.risk)}</small>
      <small><strong>Opportunity:</strong> {recorded(signal.opportunity)}</small>
      <small><strong>Next step:</strong> {recorded(signal.next_step)}</small>
      <small className="muted">Locator: {recorded(signal.evidence_locator)}</small>
      {signal.ports.length > 0 ? <small className="muted">Ports: {signal.ports.join(", ")}</small> : null}
      {signal.carriers.length > 0 ? <small className="muted">Carriers: {signal.carriers.join(", ")}</small> : null}
      {signal.limitations.length > 0 ? <small className="muted">Limitations: {signal.limitations.join("; ")}</small> : null}
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
  const storedValidationStatus = report.validation?.status ?? "missing";
  const validationStatus = report.reader_report?.validation_status
    ?? storedValidationStatus;
  const blocked = !isDecisionReadySummary(readinessSummaryFromReport(report));
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
          <span className={`status-badge status-${validationStatus}`}>{validationStatus}</span>
          <a className="secondary-action" href={`/reports/${encodeURIComponent(brief.run_id)}/markdown${report.run?.archived ? "?archive_scope=archived" : ""}`}>
            Download Markdown
          </a>
          {report.pdf?.available ? (
            <a className="secondary-action" href={`/reports/${encodeURIComponent(brief.run_id)}/pdf${report.run?.archived ? "?archive_scope=archived" : ""}`}>
              Download PDF
            </a>
          ) : <span className="status-badge status-blocked">PDF unavailable: {codeLabel(report.pdf.unavailable_reason)}</span>}
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
          <p>Run status: {runStatus}. Validation status: {validationStatus}. {report.run?.error ?? report.run?.error_code ?? "This report is not decision-ready."}</p>
        </div>
      )}

      <ReaderReportView report={report} />
      <Section title="1. Executive findings" open><BulletList bullets={brief.executive_bullets} /></Section>
      <Section title="2. Developments by lane and geography">
        <BulletList bullets={brief.developments} />
        <p className="lane-line">Coverage: {report.lane_coverage.join(", ") || "none recorded"}</p>
      </Section>
      <ReportQuality report={report} />
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
          <div><dt>Stored validation</dt><dd>{storedValidationStatus}</dd></div>
          <div><dt>Current reader validation</dt><dd>{validationStatus}</dd></div>
          <div><dt>Requested model(s)</dt><dd>{report.requested_models?.join(", ") || brief.model_id}</dd></div>
          <div><dt>Resolved model(s)</dt><dd>{report.resolved_models?.join(", ") || report.models.join(", ") || brief.model_id}</dd></div>
          <div><dt>Prompt</dt><dd>{brief.prompt_version}</dd></div>
          <div><dt>As of</dt><dd>{timestampLabel(report.as_of)}</dd></div>
          <div><dt>Branch</dt><dd>{report.run?.neon_branch_id ?? "unknown"}</dd></div>
          <div><dt>Migration</dt><dd>{report.run?.migration_version ?? "unknown"}</dd></div>
          <div><dt>Context version</dt><dd><code>{report.run?.context_version ?? "unknown"}</code></dd></div>
          <div><dt>Research timezone</dt><dd>{report.run?.research_timezone ?? "unknown"}</dd></div>
          <div><dt>Canonical hash</dt><dd><code>{report.canonical_hash}</code></dd></div>
          <div><dt>Source hashes</dt><dd>{report.source_hashes.length}</dd></div>
        </dl>
        {report.run?.run_kind === "repair" ? (
          <>
            <h3>Repair lineage</h3>
            <dl className="audit-grid">
              <div><dt>Parent run</dt><dd><code>{report.run.parent_run_id ?? "not recorded"}</code></dd></div>
              <div><dt>Repair round</dt><dd>Round {report.run.repair_round ?? "not recorded"}</dd></div>
            </dl>
          </>
        ) : null}
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
  const ready = isDecisionReadySummary(summary);
  const archived = summary.archived === true || summary.archived_at != null;
  const qualityBlocked = summary.quality_ready === false;
  const completeArticles = summary.complete_article_count;
  const articleCount = summary.article_count ?? summary.source_count;
  const qualityState = completeArticles === undefined
    ? "quality blocked"
    : `${completeArticles}/${articleCount} complete`;
  const href = `/reports/${encodeURIComponent(runId)}${archived ? "?archive_scope=archived" : ""}`;
  return (
    <Link className="report-row" href={href}>
      <span className="report-row-title">
        <span className="eyebrow">{archived ? "Archived" : ready ? "Decision-ready" : `${summary.run_status} / ${qualityBlocked ? "quality blocked" : "review required"}`}</span>
        <strong>{summary.title}</strong>
      </span>
      <span className="report-row-period">{periodLabel(summary.covered_from, summary.covered_until)}</span>
      <span className="report-row-metrics">
        <span>{summary.source_count} sources</span>
        <span>{summary.distillation_count} distillations</span>
        <span>{summary.claim_count} claims</span>
      </span>
      <span className="report-row-state">
        {archived ? summary.archive_reason ?? "archived" : `${qualityBlocked ? qualityState : "review required"} / ${summary.review_state}`}
      </span>
      <span className="card-arrow">Open report</span>
    </Link>
  );
}
