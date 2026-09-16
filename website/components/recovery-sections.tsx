import {
  ArrowDown,
  ArrowRight,
  ArrowUpRight,
  Check,
  FileMagnifyingGlass,
  Receipt,
  CurrencyDollar,
  Package,
} from "@phosphor-icons/react";
import Image from "next/image";
import { type ReactElement } from "react";
import {
  aiProcessCue,
  aiRecoveryPositioning,
  aiReviewSupport,
  industries,
  recoveryCta,
  recoveryFaqs,
  recoveryPromise,
} from "@/lib/recovery-content";
import {
  getMarketOpportunityDisplay,
  marketOpportunity,
} from "@/lib/market-opportunity";
import { ProcessStepList } from "./process-step-list";

const industryAssets = [
  "furniture",
  "consumer-goods",
  "food-beverage",
  "electronics",
  "manufacturing",
  "retail",
  "wholesale",
  "industrial",
] as const;

export function RecoveryAction(): ReactElement {
  return (
    <a className="recovery-action" href="/pilot">
      {recoveryCta}
      <ArrowUpRight size={19} aria-hidden="true" />
    </a>
  );
}

export function PortArt({ priority = false }: { priority?: boolean }): ReactElement {
  return (
    <picture className="port-art">
      <source
        media="(max-width: 640px)"
        srcSet="/media/recovery-port-mobile.webp"
      />
      <Image
        src="/media/recovery-port.webp"
        alt="Architectural rendering of a container port with cranes, a vessel and shipping activity."
        width={1536}
        height={1024}
        unoptimized
        loading={priority ? "eager" : "lazy"}
        fetchPriority={priority ? "high" : "auto"}
      />
    </picture>
  );
}

export function RecoveryHero(): ReactElement {
  return (
    <section className="recovery-hero" aria-labelledby="hero-title">
      <PortArt priority />
      <div className="recovery-container hero-copy">
        <p className="section-label">
          <span className="status-dot" /> D&amp;D recovery for importers
        </p>
        <h1 id="hero-title">
          SheperD<span className="brand-period">.</span>
        </h1>
        <p className="hero-headline">
          A clear path from
          <br className="desktop-break" /> invoice to recovery.
        </p>
        <p className="hero-description">{recoveryPromise}</p>
        <p className="hero-ai">{aiRecoveryPositioning}</p>
        <div className="hero-actions">
          <RecoveryAction />
          <a className="quiet-link" href="#process">
            How it works <ArrowDown size={16} aria-hidden="true" />
          </a>
        </div>
        <p className="hero-terms">
          <Check size={15} aria-hidden="true" /> No upfront cost. Paid when you recover value.
        </p>
      </div>
    </section>
  );
}

export function CfoSection({ editorial = false }: { editorial?: boolean }): ReactElement {
  return (
    <section
      className={`cfo-section section-pad${editorial ? " cfo-section--editorial" : ""}`}
      id="pilot-scope"
      aria-labelledby="cfo-title"
    >
      <div className="recovery-container">
        {editorial ? (
          <>
            <div className="cfo-editorial-top">
              <div className="cfo-copy">
                <h2 id="cfo-title">
                  Your time
                  <br />
                  stays yours.
                </h2>
                <p className="cfo-promise">
                  You send the invoices. <span>We handle the recovery.</span>
                </p>
                <p className="section-description">
                  SheperD manages review, recovery follow-up, and outcome tracking.
                  Your team has one job: send the invoices.
                </p>
                <p className="ai-review-copy">{aiReviewSupport}</p>
              </div>
              <figure className="cfo-dock-illustration">
                <Image
                  src="/media/motion-v2/cfo-dock-transfer.png"
                  alt="Cargo vessel at a quay while a gantry crane transfers a container."
                  width={1774}
                  height={887}
                  unoptimized
                  loading="lazy"
                />
              </figure>
            </div>
            <div className="responsibility-flow" aria-label="Recovery handoff">
              <div className="your-part">
                <span className="handoff-kicker">Your part</span>
                <div className="handoff-step">
                  <span className="handoff-icon">
                    <Receipt size={24} aria-hidden="true" />
                  </span>
                  <strong>Send invoices</strong>
                </div>
              </div>
              <ArrowRight className="handoff-arrow" size={28} aria-hidden="true" />
              <div className="our-part">
                <span className="handoff-kicker">Handled by SheperD</span>
                <ol>
                  {["Review the charges", "Pursue recovery", "Track the outcome"].map((item) => (
                    <li key={item}>
                      <span className="handoff-check">
                        <Check size={17} aria-hidden="true" />
                      </span>
                      <span>{item}</span>
                    </li>
                  ))}
                </ol>
              </div>
            </div>
          </>
        ) : (
          <>
            <p className="section-label">Your time stays yours</p>
            <div className="section-split cfo-layout">
              <div className="cfo-copy">
                <h2 id="cfo-title">
                  You send the invoices.
                  <br />
                  <span className="muted-heading">We handle the recovery.</span>
                </h2>
                <p className="section-description">
                  SheperD manages review, recovery follow-up, and outcome tracking.
                  Your team has one job: send the invoices.
                </p>
              </div>
              <div className="responsibility-flow" aria-label="Recovery handoff">
                <div className="your-part">
                  <Receipt size={28} aria-hidden="true" />
                  <span>Your part</span>
                  <strong>Send invoices</strong>
                </div>
                <ArrowRight className="handoff-arrow" size={28} aria-hidden="true" />
                <div className="our-part">
                  <span className="section-label">Handled by SheperD</span>
                  <div>
                    {["Review the charges", "Pursue recovery", "Track the outcome"].map((item) => (
                      <span key={item}>
                        <Check size={17} aria-hidden="true" />
                        {item}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </>
        )}
      </div>
    </section>
  );
}

export function ProcessSection({
  detailed = false,
}: {
  detailed?: boolean;
}): ReactElement {
  return (
    <section
      id="process"
      className="process-band section-pad"
      aria-labelledby="process-title"
    >
      <div className="recovery-container">
        <p className="section-label">How it works</p>
        <div className="process-heading">
          <h2 id="process-title">
            A clear path.
            <br />
            An entirely managed process.
          </h2>
          <p className="section-description">
            From historical charges to potential recovered value. SheperD owns
            the work after your invoice handoff.
          </p>
          <p className="process-ai">{aiProcessCue}</p>
        </div>
        <ProcessStepList detailed={detailed} />
        <div className="process-bottom">
          <p>Recovery depends on the facts of each charge.</p>
          {!detailed && (
            <a className="quiet-link" href="/how-it-works">
              Explore the process <ArrowUpRight size={17} aria-hidden="true" />
            </a>
          )}
        </div>
      </div>
    </section>
  );
}

export function MarketOpportunitySection(): ReactElement {
  const { figure, source } = getMarketOpportunityDisplay(marketOpportunity);

  return (
    <section
      className="market-section section-pad"
      id="evidence"
      data-market-state={marketOpportunity.status}
      aria-labelledby="market-title"
    >
      <div className="recovery-container market-layout">
        <div className="market-copy">
          <p className="section-label">The opportunity in the record</p>
          <h2 id="market-title">Global records create new opportunities.</h2>
          <p className="section-description">
            SheperD brings paid invoices and shipping history together, then
            reviews the record for potential recovery across global trade
            routes.
          </p>
          <a className="quiet-link" href="/about">
            Why SheperD exists <ArrowUpRight size={17} aria-hidden="true" />
          </a>
          <ul className="market-proof" aria-label="What connected records make visible">
            <li>
              <strong>More complete</strong>
              <span>records</span>
            </li>
            <li>
              <strong>Clearer</strong>
              <span>relationships</span>
            </li>
            <li>
              <strong>A larger</strong>
              <span>opportunity set</span>
            </li>
          </ul>
        </div>
        <figure className="market-visual" aria-labelledby="market-visual-caption">
          <div className="market-visual-shell">
            <ul className="market-records" aria-label="Records connected for review">
              <li className="market-input market-input--invoice">
                <Receipt size={25} aria-hidden="true" />
                <span>
                  <strong>Paid invoices</strong>
                  <small>Financial records, payments and counterparties.</small>
                </span>
              </li>
              <li className="market-input market-input--shipping">
                <Package size={25} aria-hidden="true" />
                <span>
                  <strong>Shipping history</strong>
                  <small>Vessel movements, ports and cargo events.</small>
                </span>
              </li>
            </ul>
            <div className="market-map-stage">
              <Image
                className="market-map"
                src="/media/motion-v2/opportunity-trade-map-transparent.png"
                alt=""
                width={1672}
                height={941}
                sizes="(max-width: 767px) 136vw, (max-width: 1100px) 60vw, 54vw"
                unoptimized
                loading="eager"
              />
              <div className="market-review-node">
                <div className="market-review-badge">
                  <FileMagnifyingGlass size={27} aria-hidden="true" />
                </div>
                <div className="market-review-copy">
                  <strong>SheperD review</strong>
                  <span>Reconciles records, matches events, and surfaces opportunities.</span>
                </div>
              </div>
            </div>
            <div className="market-output">
              <div className="market-trade-note">
                <strong>Global trade records</strong>
                <span>Invoices and voyages connected across ports and counterparties.</span>
              </div>
              <div
                className={`market-opportunity-node${figure ? "" : " market-opportunity-node--pending"}`}
                aria-label={
                  figure
                    ? `${figure} annual cost of port delays to manufacturers`
                    : "Opportunity figure withheld pending approval"
                }
              >
                {figure && (
                  <>
                    <strong>{figure}</strong>
                    <b>annual port-delay cost</b>
                  </>
                )}
                <small>
                  {figure
                    ? "NAM estimate for U.S. manufacturers. Recovery depends on the facts of each charge."
                    : "Opportunity figure withheld pending approval."}
                </small>
              </div>
            </div>
          </div>
          <figcaption id="market-visual-caption" className="visually-hidden">
            Paid invoices and shipping history connect through SheperD review to
            global trade records and a potential opportunity for recovery. The
            {figure
              ? ` sourced ${figure} figure describes annual port-delay costs to U.S. manufacturers; it is not a guarantee of value recoverable by SheperD.`
              : " market figure is suppressed until its meaning, source and approval are recorded."}
          </figcaption>
          {source && (
            <a
              className="market-source"
              href={source.href}
              target="_blank"
              rel="noreferrer"
            >
              <span>{source.title}</span>
              <span className="market-source-meta">Checked {source.checkedAt}</span>
            </a>
          )}
        </figure>
      </div>
    </section>
  );
}

export function MissedValueSection(): ReactElement {
  return (
    <section
      className="missed-section section-pad"
      id="evidence"
      aria-labelledby="missed-title"
    >
      <div className="recovery-container section-split">
        <div>
          <p className="section-label">A second look at spend</p>
          <h2 id="missed-title">
            Paid doesn&apos;t have
            <br />
            to mean forgotten.
          </h2>
          <p className="section-description">
            We review historical detention and demurrage charges for potential
            recovery, bringing the invoice and its supporting records together.
          </p>
          <a className="quiet-link" href="/about">
            Why SheperD exists <ArrowUpRight size={17} aria-hidden="true" />
          </a>
        </div>
        <div
          className="expense-diagram"
          role="img"
          aria-label="Paid invoices and shipping history enter SheperD review. Selected charges may return value to the importer."
        >
          <div className="record-row">
            <span>
              <Receipt size={22} /> Paid invoices
            </span>
            <span>
              <Package size={22} /> Shipping history
            </span>
          </div>
          <div className="record-connector" />
          <div className="review-wordmark">
            SheperD<span>Historical review</span>
          </div>
          <div className="return-line">
            <ArrowDown size={24} />
          </div>
          <div className="returned-value">
            <CurrencyDollar size={27} />
            <span>Potential recovered value</span>
            <ArrowUpRight size={24} />
          </div>
        </div>
      </div>
    </section>
  );
}

export function EconomicsSection(): ReactElement {
  return (
    <section
      className="economics-section section-pad"
      id="mission"
      aria-labelledby="economics-title"
    >
      <div className="recovery-container section-split">
        <div>
          <p className="section-label">Aligned from the start</p>
          <h2 id="economics-title">
            We get paid when
            <br />
            you recover value.
          </h2>
          <p className="section-description">
            No upfront cost. Our revenue share is tied to monetary value
            recovered, with terms agreed before we begin.
          </p>
          <div className="zero-upfront">
            <strong>$0</strong>
            <span>Upfront cost</span>
          </div>
        </div>
        <div className="recovery-ledger">
          <div className="ledger-caption">
            The financial picture <span>Illustrative</span>
          </div>
          <div className="ledger-row">
            <span>Historical D&amp;D</span>
            <span>Expense</span>
          </div>
          <div className="ledger-row">
            <span>SheperD review</span>
            <span>Opportunity</span>
          </div>
          <div className="ledger-row ledger-result">
            <span>Recovered value</span>
            <ArrowUpRight size={27} aria-hidden="true" />
          </div>
          <div className="ledger-outcomes">
            <span>
              Refund <small>Money returned</small>
            </span>
            <span>
              Carrier credit <small>Value credited</small>
            </span>
          </div>
          <p>Different outcomes. Each tracked through resolution.</p>
        </div>
      </div>
    </section>
  );
}

export function ImporterSection({ faq = true }: { faq?: boolean }): ReactElement {
  return (
    <section
      className="importer-section section-pad"
      id="trust"
      aria-labelledby="importer-title"
    >
      <div className="recovery-container">
        <p className="section-label">For importers</p>
        <div className="importer-heading">
          <h2 id="importer-title">
            Built around your imports.
            <br />
            Not added to your workload.
          </h2>
          <p className="section-description">
            A dedicated recovery function for businesses moving goods, without
            building one internally.
          </p>
        </div>
        <div className="industry-grid">
          {industries.map((industry, index) => {
            return (
              <div className="industry" key={industry}>
                <Image
                  src={`/media/motion-v2/industry-${industryAssets[index]}-glass-transparent.png`}
                  alt=""
                  width={72}
                  height={72}
                  loading="eager"
                  unoptimized
                />
                <span>{industry}</span>
              </div>
            );
          })}
        </div>
        {faq && (
          <div className="recovery-faq">
            <div>
              <p className="section-label">A few practical answers</p>
              <h3>Before you begin.</h3>
            </div>
            <div>
              {recoveryFaqs.map((item) => (
                <details key={item.question}>
                  <summary>
                    {item.question}
                    <span aria-hidden="true">+</span>
                  </summary>
                  <p>{item.answer}</p>
                </details>
              ))}
            </div>
          </div>
        )}
      </div>
    </section>
  );
}

export function ClosingSection(): ReactElement {
  return (
    <section className="recovery-closing" aria-labelledby="closing-title">
      <PortArt />
      <div className="recovery-container">
        <p className="section-label">Your history. Your opportunity.</p>
        <h2 id="closing-title">
          Find recoverable value
          <br />
          in your shipping history.
        </h2>
        <p>{recoveryPromise}</p>
        <RecoveryAction />
        <span className="closing-cost">No upfront cost.</span>
      </div>
    </section>
  );
}
