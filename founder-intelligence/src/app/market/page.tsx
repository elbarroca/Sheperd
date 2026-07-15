import type { Metadata } from "next";
import { ArrowSquareOutIcon } from "@phosphor-icons/react/dist/ssr/ArrowSquareOut";
import { PageHeader } from "@/components/page-header";
import { SourceLink } from "@/components/source-link";
import {
  marketEvidenceGroups,
  marketFriction,
  marketSignals,
  marketTiming,
  MARKET_SOURCE_PATH,
} from "@/lib/focused-content";

export const metadata: Metadata = { title: "Market situation" };

export default function MarketPage() {
  return (
    <div className="focused-page">
      <PageHeader
        eyebrow="Market situation"
        title="The problem is material. The market size is not proven."
        description="Official evidence shows meaningful D&D charges, formal complaints, relief, enforcement, and recurring operational pressure. It does not yet show SheperD's recoverable market or commercial economics."
        meta={<><span>Current decision</span><strong>Problem supported</strong><small>TAM, SAM, and SOM unknown</small></>}
      />

      <section className="focus-section market-proof" aria-labelledby="proof-signals-title">
        <div className="focus-heading">
          <div><p className="focus-label">Proof signals</p><h2 id="proof-signals-title">What the public evidence actually establishes</h2></div>
          <SourceLink path={MARKET_SOURCE_PATH} label="Read complete market map" />
        </div>
        <div className="market-signal-grid">
          {marketSignals.map((signal) => (
            <article key={signal.id} className="market-signal">
              <strong>{signal.value}</strong>
              <h3>{signal.label}</h3>
              <p>{signal.meaning}</p>
              <small>{signal.boundary}</small>
              {signal.url ? <a href={signal.url} target="_blank" rel="noreferrer">Open primary source <ArrowSquareOutIcon size={15} aria-hidden="true" /></a> : <SourceLink path="10_Sources/Source - Competitor and Public Pain Signals - 2026-07-15.md" />}
            </article>
          ))}
        </div>
        <div className="evidence-shelf">
          <header><h3>Source shelf</h3><p>Reports, papers, and public problem language used in the market conclusion.</p></header>
          {marketEvidenceGroups.map((group) => (
            <article key={group.label}>
              <h4>{group.label}</h4>
              <p>{group.boundary}</p>
              <ul>
                {group.links.map((link) => (
                  <li key={link.url}><a href={link.url} target="_blank" rel="noreferrer">{link.label}<ArrowSquareOutIcon size={14} aria-hidden="true" /></a></li>
                ))}
              </ul>
            </article>
          ))}
        </div>
      </section>

      <section className="focus-section" aria-labelledby="friction-title">
        <div className="focus-heading">
          <div><p className="focus-label">Market struggle</p><h2 id="friction-title">The hard part is turning disruption into a defensible decision</h2></div>
          <p>A delay can create an invoice. It does not automatically make that invoice invalid or recoverable.</p>
        </div>
        <ol className="market-route">
          {marketFriction.map((item, index) => (
            <li key={item.step}>
              <span>{index + 1}</span>
              <h3>{item.step}</h3>
              <p>{item.issue}</p>
              <small>{item.proof}</small>
            </li>
          ))}
        </ol>
      </section>

      <section className="focus-section" aria-labelledby="timing-title">
        <div className="focus-heading">
          <div><p className="focus-label">Market timing</p><h2 id="timing-title">Good time to learn, wrong time to claim scale</h2></div>
        </div>
        <div className="timing-grid">
          {marketTiming.map((item) => (
            <article key={item.label}><span>{item.label}</span><h3>{item.title}</h3><p>{item.detail}</p></article>
          ))}
        </div>
      </section>

      <section className="focus-section sizing-truth" aria-labelledby="sizing-title">
        <div>
          <p className="focus-label">Sizing truth</p>
          <h2 id="sizing-title">TAM, SAM, and SOM stay unknown</h2>
          <p>Do not multiply total charges by importer counts or vendor recovery claims. Each layer needs an invoice-level denominator, a valid eligibility method, realized outcomes, and approved fee economics.</p>
        </div>
        <dl>
          <div><dt>TAM</dt><dd>Eligible U.S. ocean-container D&D value with supported recovery and fee assumptions.</dd><strong>Unknown</strong></div>
          <div><dt>SAM</dt><dd>TAM restricted to reachable accounts, evidence access, geography, and delivery capability.</dd><strong>Unknown</strong></div>
          <div><dt>SOM</dt><dd>Capacity-constrained cases with measured qualification, cycle, quality, outcome, and fee.</dd><strong>Unknown</strong></div>
        </dl>
      </section>
    </div>
  );
}
