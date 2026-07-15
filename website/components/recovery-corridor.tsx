import {
  ArrowRight,
  CalendarCheck,
  Circle,
  Coins,
  CurrencyDollar,
  Eye,
  FileArrowUp,
  MagnifyingGlass,
  ChartLineUp,
  Receipt,
  ShieldCheck,
  ShippingContainer,
  Truck,
  UsersThree,
  Warehouse,
} from "@phosphor-icons/react";
import Image from "next/image";

import {
  benefits,
  containerEvents,
  marketStats,
  missionOutcomes,
  recoverySteps,
} from "@/lib/content";

import { LeadForm } from "./lead-form";
import { MotionShell, Reveal } from "./motion-shell";
import { SiteFooter } from "./site-footer";
import { SiteHeader } from "./site-header";

const benefitIcons = {
  cost: Coins,
  workload: UsersThree,
  visibility: Eye,
} as const;

const stepIcons = {
  invoice: FileArrowUp,
  audit: MagnifyingGlass,
  refund: CurrencyDollar,
} as const;

const missionIcons = {
  prevent: ShieldCheck,
  recover: CurrencyDollar,
  accountability: ChartLineUp,
} as const;

const containerEventIcons = {
  freeTime: CalendarCheck,
  availability: Warehouse,
  gateOut: Truck,
  emptyReturn: ShippingContainer,
  invoice: Receipt,
} as const;

export function RecoveryCorridor() {
  return (
    <MotionShell>
      <a className="skip-link" href="#main-content">
        Skip to content
      </a>

      <SiteHeader />

      <main id="main-content" tabIndex={-1}>
        <section className="hero-section" aria-labelledby="hero-title">
          <div className="container hero-layout">
            <Reveal className="hero-copy">
              <p className="eyebrow eyebrow-blue">Shipping container charge recovery</p>
              <h1 id="hero-title">
                <span>Recover</span>
                {" "}
                <span className="hero-title-line">What’s Yours</span>
              </h1>
              <p className="hero-summary">
                Recover demurrage and detention overcharges
                <br />
                {" "}
                from shipping-container invoices. SheperD audits,
                <br />
                {" "}
                disputes, and tracks every eligible refund.
              </p>
              <div className="hero-actions">
                <a className="button" href="#audit-form">
                  Get a Free Invoice Audit
                </a>
                <a className="button button-secondary" href="#how-it-works">
                  See how it works
                </a>
              </div>
            </Reveal>

            <Reveal className="hero-mark-wrap" delay={0.1}>
              <span className="hero-mark-glow" aria-hidden="true" />
              <Image
                className="hero-mark"
                src="/brand/sheperd-logo.png"
                width={512}
                height={395}
                sizes="(max-width: 719px) 76vw, 42vw"
                quality={100}
                loading="eager"
                fetchPriority="high"
                alt="SheperD shepherd mark"
              />
            </Reveal>
          </div>

          <div className="container metric-corridor" aria-label="Shipping charge recovery context">
            {marketStats.map((stat, index) => (
              <Reveal className="metric" delay={0.08 * index} key={stat.value}>
                <Circle className="metric-node" aria-hidden="true" size={18} weight="fill" />
                <strong>{stat.value}</strong>
                <span>{stat.label}</span>
              </Reveal>
            ))}
          </div>
        </section>

        <section
          id="why-sheperd"
          className="recovery-explainer"
          aria-labelledby="problem-title"
        >
          <div className="container explainer-layout">
            <Reveal className="problem-column">
              <p className="eyebrow">Where container losses happen</p>
              <h2 id="problem-title" className="visually-hidden">
                The overcharge problem
              </h2>
              <p>
                Demurrage and detention are fees charged when a shipping
                container stays at a port or outside a terminal beyond its
                allowed free time.
              </p>
              <p>
                Some charges may be wrong when pickup was impossible, port
                disruptions were ignored, or an invoice missed required
                details. SheperD finds those exceptions and manages recovery.
              </p>

              <div className="benefit-row">
                {benefits.map((benefit) => {
                  const Icon = benefitIcons[benefit.icon];
                  return (
                    <article className="benefit" key={benefit.title}>
                      <span className="icon-ring">
                        <Icon aria-hidden="true" size={24} />
                      </span>
                      <div>
                        <h3>{benefit.title}</h3>
                        <p>{benefit.description}</p>
                      </div>
                    </article>
                  );
                })}
              </div>
            </Reveal>

            <Reveal className="process-column" delay={0.08}>
              <p className="eyebrow">A simple recovery process</p>
              <h2 id="how-it-works" className="visually-hidden">
                How SheperD works
              </h2>
              <ol className="process-list">
                {recoverySteps.map((step) => {
                  const Icon = stepIcons[step.icon];
                  return (
                    <li className="process-step" key={step.number}>
                      <span className="process-icon">
                        <Icon aria-hidden="true" size={30} />
                      </span>
                      <div className="process-copy">
                        <span className="process-number">{step.number}</span>
                        <h3>{step.title}</h3>
                        <p>{step.description}</p>
                      </div>
                    </li>
                  );
                })}
              </ol>
            </Reveal>
          </div>
        </section>

        <section
          id="container-journey"
          className="container-journey-section"
          aria-labelledby="container-journey-title"
        >
          <div className="container container-journey-layout">
            <Reveal className="container-journey-media">
              <Image
                className="container-journey-image"
                src="/media/container-terminal-operations.jpg"
                fill
                sizes="(max-width: 820px) calc(100vw - 40px), 52vw"
                quality={90}
                loading="eager"
                alt="Import containers, terminal handling equipment, and a tractor operating in a marine container yard at blue hour."
              />
              <div className="container-journey-caption">
                <span>Import container event record</span>
                <strong>Availability → gate-out → empty return</strong>
              </div>
            </Reveal>

            <Reveal className="container-journey-copy" delay={0.08}>
              <p className="eyebrow">What the charge review follows</p>
              <h2 id="container-journey-title">
                Follow the container, not just the invoice.
              </h2>
              <p className="container-journey-summary">
                Demurrage usually concerns time the import container remains
                inside the marine terminal after free time. Detention—often
                billed as per diem—usually concerns time after gate-out until
                the empty equipment is returned. A useful review connects
                those billed days to the actual event record.
              </p>

              <ol className="container-event-list">
                {containerEvents.map((event) => {
                  const Icon = containerEventIcons[event.icon];
                  return (
                    <li className="container-event" key={event.title}>
                      <span className="container-event-icon">
                        <Icon aria-hidden="true" size={23} />
                      </span>
                      <div>
                        <h3>{event.title}</h3>
                        <p>{event.description}</p>
                      </div>
                    </li>
                  );
                })}
              </ol>
            </Reveal>
          </div>
        </section>

        <section
          id="mission"
          className="mission-section"
          aria-labelledby="mission-title"
        >
          <div className="container mission-layout">
            <Reveal className="mission-intro">
              <p className="eyebrow">What SheperD is building</p>
              <h2 id="mission-title">
                Make container-charge recovery a standard part of import
                operations.
              </h2>
              <p>
                Import teams should not have to choose between paying a
                questionable fee and spending hours disputing it. SheperD is
                building the operating layer that reviews every demurrage and
                detention invoice, identifies exceptions, manages eligible
                disputes, and keeps a clear record from charge to refund.
              </p>
            </Reveal>

            <div className="mission-outcomes">
              {missionOutcomes.map((outcome, index) => {
                const Icon = missionIcons[outcome.icon];
                return (
                  <Reveal
                    className="mission-outcome"
                    delay={0.06 * index}
                    key={outcome.title}
                  >
                    <span className="mission-icon">
                      <Icon aria-hidden="true" size={25} />
                    </span>
                    <div>
                      <h3>{outcome.title}</h3>
                      <p>{outcome.description}</p>
                    </div>
                  </Reveal>
                );
              })}
            </div>
          </div>
        </section>

        <section
          id="recovery-dashboard"
          className="dashboard-section"
          aria-labelledby="dashboard-title"
        >
          <div className="container dashboard-layout">
            <Reveal className="dashboard-intro">
              <p className="eyebrow eyebrow-blue">Container charge visibility</p>
              <h2 id="dashboard-title">
                See every shipping-container charge from invoice to refund.
              </h2>
            </Reveal>

            <Reveal className="dashboard-frame" delay={0.08}>
              <Image
                className="dashboard-image"
                src="/media/recovery-dashboard.png"
                width={1892}
                height={945}
                sizes="(max-width: 719px) calc(100vw - 40px), 1220px"
                quality={90}
                loading="eager"
                alt="SheperD shipping-container charge Recovery Summary showing invoices, disputes, credits, and monthly activity."
              />
            </Reveal>

            <div className="audit-layout">
              <Reveal className="audit-copy">
                <p className="eyebrow eyebrow-blue">Free container invoice audit</p>
                <h2>Estimate recoverable container charges within 24 hours.</h2>
                <p>No obligation. No spam. Just a first recovery estimate.</p>
                <ArrowRight className="audit-arrow" aria-hidden="true" size={42} />
              </Reveal>
              <Reveal className="audit-form-wrap" delay={0.08}>
                <LeadForm />
              </Reveal>
            </div>
          </div>
        </section>
      </main>

      <SiteFooter />
    </MotionShell>
  );
}
