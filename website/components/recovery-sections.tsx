import {
  ArrowDown,
  ArrowRight,
  ArrowUpRight,
  ArrowCounterClockwise,
  Check,
  Receipt,
  CurrencyDollar,
  Package,
} from "@phosphor-icons/react";
import Image from "next/image";
import { type ReactElement, useState } from "react";
import {
  industries,
  recoveryCta,
  recoveryFaqs,
  recoveryPromise,
  recoverySteps,
} from "@/lib/recovery-content";

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
  const [replay, setReplay] = useState(0);
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
          Turn historical shipping
          <br className="desktop-break" /> charges into money back.
        </p>
        <p className="hero-description">
          Detention and demurrage recovery.
          <br />
          Send your invoices. We handle the rest.
        </p>
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
      <div className="port-story" key={replay} aria-hidden="true">
        <span className="freight-label">
          Freight moves forward <ArrowRight size={14} />
        </span>
        <div className="freight-track">
          <span />
        </div>
        <div className="value-track">
          <span />
        </div>
        <span className="value-label">
          <ArrowRight size={14} /> Value comes back
        </span>
      </div>
      <div className="hero-caption">
        <span>Historical charges. A new direction.</span>
        <button
          type="button"
          className="replay-button"
          aria-label="Replay shipping and recovery animation"
          title="Replay animation"
          onClick={() => setReplay((value) => value + 1)}
        >
          <ArrowCounterClockwise size={18} aria-hidden="true" />
        </button>
      </div>
    </section>
  );
}

export function CfoSection(): ReactElement {
  return (
    <section
      className="cfo-section section-pad"
      id="pilot-scope"
      aria-labelledby="cfo-title"
    >
      <div className="recovery-container">
        <p className="section-label">01 / Your time stays yours</p>
        <div className="section-split">
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
        <div className="responsibility-flow">
          <div className="your-part">
            <Receipt size={28} aria-hidden="true" />
            <span>Your part</span>
            <strong>Send invoices</strong>
          </div>
          <ArrowRight className="handoff-arrow" size={28} aria-hidden="true" />
          <div className="our-part">
            <span className="section-label">Handled by SheperD</span>
            <div>
              {[
                "Review the charges",
                "Pursue recovery",
                "Track the outcome",
              ].map((item) => (
                <span key={item}>
                  <Check size={17} aria-hidden="true" />
                  {item}
                </span>
              ))}
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

const stepAssets = {
  invoice: "invoice",
  review: "review",
  recovery: "container",
  value: "value",
} as const;

export function ProcessSection({ detailed = false }: { detailed?: boolean }): ReactElement {
  return (
    <section
      id="process"
      className="process-band section-pad"
      aria-labelledby="process-title"
    >
      <div className="recovery-container">
        <p className="section-label">02 / How it works</p>
        <div className="section-split">
          <h2 id="process-title">
            A clear path.
            <br />
            An entirely managed process.
          </h2>
          <p className="section-description">
            From historical charges to potential recovered value. SheperD owns
            the work after your invoice handoff.
          </p>
        </div>
        <ol className="recovery-process">
          {recoverySteps.map((step, index) => (
            <li key={step.kind}>
              <span className="step-owner">{step.owner}</span>
              <div className={`step-art step-art-${step.kind}`}>
                <Image
                  src={`/media/recovery-${stepAssets[step.kind]}.webp`}
                  alt=""
                  width={160}
                  height={160}
                  unoptimized
                />
                <span className="step-number">0{index + 1}</span>
              </div>
              <h3>{step.title}</h3>
              {detailed && <p>{step.description}</p>}
            </li>
          ))}
        </ol>
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

export function MissedValueSection(): ReactElement {
  return (
    <section
      className="missed-section section-pad"
      id="evidence"
      aria-labelledby="missed-title"
    >
      <div className="recovery-container section-split">
        <div>
          <p className="section-label">03 / A second look at spend</p>
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
          <p className="section-label">04 / Aligned from the start</p>
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
        <p className="section-label">05 / For importers</p>
        <div className="section-split">
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
                <Image src={`/media/industry-${index}.webp`} alt="" width={72} height={72} unoptimized />
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
