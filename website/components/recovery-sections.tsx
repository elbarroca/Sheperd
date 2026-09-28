import {
  ArrowLeft,
  Armchair,
  ArrowDown,
  ArrowRight,
  ArrowUpRight,
  Check,
  Coins,
  Cube,
  Desktop,
  Factory,
  ForkKnife,
  GearSix,
  HorseIcon,
  Receipt,
  ShoppingBag,
  Stack,
  Plus,
  CurrencyDollar,
  Package,
} from "@phosphor-icons/react";
import Image from "next/image";
import { type ReactElement } from "react";
import {
  aiRecoveryPositioning,
  industries,
  recoveryCta,
  recoveryFaqs,
  recoveryPromise,
} from "@/lib/recovery-content";
import { ProcessStepList } from "./process-step-list";

const industryIcons = {
  Furniture: Armchair,
  "Consumer goods": Cube,
  "Food & beverage": ForkKnife,
  Electronics: Desktop,
  Manufacturing: GearSix,
  Retail: ShoppingBag,
  Wholesale: Stack,
  Industrial: Factory,
} as const;

const CALENDLY_EVENT_URL = "";

export function RecoveryAction(): ReactElement {
  return (
    <a className="recovery-action" href="/#contact">
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
          <div className="cfo-editorial-shell">
            <div className="cfo-editorial-copy">
              <h2 id="cfo-title">
                Your time
                <br />
                stays yours.
              </h2>
              <p className="cfo-promise">
                You send the invoices. <span>We handle the recovery.</span>
              </p>
            </div>
            <figure
              className="cfo-editorial-scene"
              aria-label="Your team sends invoices to SheperD, which manages the recovery."
            >
              <Image
                src="/media/cfo-port-blue-hour.jpg"
                alt=""
                fill
                sizes="(max-width: 820px) 100vw, 60vw"
              />
              <figcaption className="cfo-handoff-graphic">
                <div className="cfo-handoff-card cfo-handoff-card--team">
                  <Receipt size={32} aria-hidden="true" />
                  <span>
                    <strong>Your team</strong>
                    <small>Send invoices</small>
                  </span>
                </div>
                <span className="cfo-handoff-directions" aria-hidden="true">
                  <ArrowRight size={28} />
                  <ArrowLeft size={28} />
                </span>
                <div className="cfo-handoff-card cfo-handoff-card--sheperd">
                  <HorseIcon size={40} aria-hidden="true" />
                  <span>
                    <strong>SheperD</strong>
                    <small>Manage recovery</small>
                  </span>
                </div>
              </figcaption>
            </figure>
          </div>
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
  const invoiceYears = [
    { label: "Year 1", src: "/media/invoice-history/year-1.png" },
    { label: "Year 2", src: "/media/invoice-history/year-2.png" },
    { label: "Year 3", src: "/media/invoice-history/year-3.png" },
  ] as const;

  return (
    <section
      className="market-section section-pad"
      id="pilot-scope"
      aria-labelledby="market-title"
    >
      <div className="recovery-container market-layout" id="evidence">
        <div className="market-copy">
          <h2 id="market-title">Past invoices may hold money for your bottom line.</h2>
          <p className="section-description">
            Three years of past U.S. detention and demurrage invoices may hold
            potential cash refunds or carrier credits.
          </p>
          <RecoveryAction />
        </div>
        <figure
          className="invoice-history-visual"
          aria-labelledby="market-title"
          aria-describedby="invoice-history-note"
        >
          <ol
            className="invoice-history-timeline"
            aria-label="Past three years of invoice history"
          >
            {invoiceYears.map((year) => (
              <li key={year.label}>
                <span className="invoice-stack-art">
                  <Image
                    src={year.src}
                    alt=""
                    fill
                    sizes="(max-width: 820px) 30vw, (max-width: 1100px) 18vw, 20vw"
                  />
                </span>
                <span>{year.label}</span>
              </li>
            ))}
          </ol>
          <div className="invoice-history-bracket" aria-hidden="true">
            <span>Past 3 years</span>
          </div>
          <ul className="invoice-history-outcomes" aria-label="Potential recovery outcomes">
            <li>
              <Coins size={38} weight="regular" aria-hidden="true" />
              <span>Potential cash refund</span>
            </li>
            <li>
              <Package size={38} weight="regular" aria-hidden="true" />
              <span>Potential carrier credit</span>
            </li>
          </ul>
          <figcaption className="invoice-history-note" id="invoice-history-note">
            Three years is past invoice history, not a recovery estimate. Outcomes depend on each
            charge&apos;s facts and applicable deadlines.
          </figcaption>
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
        <p className="section-label importer-eyebrow">For importers</p>
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
          {industries.map((industry) => {
              const IndustryIcon = industryIcons[industry];
              return (
                <div className="industry" key={industry}>
                  <span className="industry-icon-frame" aria-hidden="true">
                    <IndustryIcon
                      className="industry-icon"
                      size={36}
                      weight="regular"
                      aria-hidden="true"
                    />
                  </span>
                  <span>{industry}</span>
                </div>
            );
          })}
        </div>
        {faq && (
          <div className="recovery-faq">
            <div className="recovery-faq-intro">
              <p className="section-label">A few practical answers</p>
              <h3>Before you begin.</h3>
            </div>
            <div className="recovery-faq-list">
              {recoveryFaqs.map((item) => (
                <details key={item.question}>
                  <summary>
                    {item.question}
                    <span className="faq-toggle" aria-hidden="true">
                      <Plus size={18} weight="regular" />
                    </span>
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

export function CalendlySection(): ReactElement {
  return (
    <section className="calendly-section" id="contact" aria-labelledby="contact-title">
      <div className="recovery-container calendly-content">
        <div className="calendly-intro">
          <p className="section-label">Your next step</p>
          <h2 id="contact-title">Let’s talk about your shipping history.</h2>
          <p>
            Book a conversation about your detention and demurrage invoices, the
            records around each charge, and whether a focused recovery review makes
            sense.
          </p>
        </div>
        <div className="calendly-booking">
          {CALENDLY_EVENT_URL ? (
            <>
              <iframe
                className="calendly-frame"
                id="calendly-booking"
                src={CALENDLY_EVENT_URL}
                title="Schedule a recovery conversation with SheperD"
                loading="lazy"
              />
              <p className="calendly-privacy">
                Scheduling is handled by Calendly. See the{" "}
                <a
                  href="https://calendly.com/legal/privacy-notice"
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  Calendly Privacy Notice
                  <ArrowUpRight size={14} aria-hidden="true" />
                </a>
                .
              </p>
              <a
                className="quiet-link calendly-fallback"
                href={CALENDLY_EVENT_URL}
                target="_blank"
                rel="noopener noreferrer"
              >
                Open the calendar in a new tab
                <ArrowUpRight size={16} aria-hidden="true" />
              </a>
            </>
          ) : (
            <div className="calendly-unavailable" role="status">
              <p className="calendly-unavailable-label">Calendly scheduling</p>
              <h3>Choose a time that works.</h3>
              <p>The booking calendar will appear here once scheduling is set up.</p>
              <p className="calendly-unavailable-note">
                No booking details are collected until then.
              </p>
            </div>
          )}
        </div>
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
