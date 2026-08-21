import {
  ArrowRight,
  CalendarCheck,
  CheckCircle,
  CurrencyDollar,
  FileArrowUp,
  Receipt,
  ShieldCheck,
  ShippingContainer,
  WarningCircle,
} from "@phosphor-icons/react";
import Image from "next/image";

import {
  evidenceLayers,
  faqItems,
  pilotScope,
  processSteps,
  sourceLinks,
} from "@/lib/content";

import { MotionShell, Reveal } from "./motion-shell";
import { SiteFooter } from "./site-footer";
import { SiteHeader } from "./site-header";

const evidenceIcons = {
  billing: Receipt,
  timeline: CalendarCheck,
  terms: ShieldCheck,
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
          <div className="hero-aurora" aria-hidden="true" />
          <div className="container hero-layout">
            <Reveal className="hero-copy">
              <p className="eyebrow eyebrow-blue">
                For importer finance + logistics teams
              </p>
              <p className="hero-kicker">The record before the recovery</p>
              <h1 id="hero-title">
                <span>Recover the D&amp;D money</span>
                <span>hiding in your invoices.</span>
              </h1>
              <p className="hero-summary">
                SheperD connects detention and demurrage invoices, shipment
                events, and governing terms to identify case-specific recovery
                opportunities and support the path toward carrier credit or
                refund.
              </p>
              <div className="hero-actions">
                <a className="button" href="/pilot">
                  Request a pilot
                  <ArrowRight aria-hidden="true" size={18} />
                </a>
                <a className="button button-secondary" href="#process">
                  See the recovery path
                </a>
              </div>
              <p className="hero-boundary">
                Case-specific review <span aria-hidden="true">·</span> No
                guaranteed recovery
              </p>
            </Reveal>

            <Reveal className="hero-art" delay={0.08}>
              <figure className="route-visual">
                <div className="route-visual-label">
                  Illustrative record <span>·</span> No customer data
                </div>

                <div className="route-stage">
                  <div className="invoice-card artifact-card">
                    <div className="artifact-topline">
                      <span>D&amp;D invoice</span>
                      <Receipt aria-hidden="true" size={18} />
                    </div>
                    <h2>Invoice 87423</h2>
                    <dl>
                      <div>
                        <dt>Charge</dt>
                        <dd>Detention</dd>
                      </div>
                      <div>
                        <dt>Period</dt>
                        <dd>04/15–04/28</dd>
                      </div>
                      <div>
                        <dt>State</dt>
                        <dd>Review pending</dd>
                      </div>
                    </dl>
                    <div className="artifact-total">
                      <span>Record status</span>
                      <strong>Open review</strong>
                    </div>
                  </div>

                  <div className="route-path" aria-hidden="true">
                    <span className="route-path-line route-path-line-one" />
                    <span className="route-path-line route-path-line-two" />
                    <span className="route-path-line route-path-line-three" />
                    <span className="route-path-node route-path-node-one" />
                    <span className="route-path-node route-path-node-two" />
                    <span className="route-path-node route-path-node-three" />
                  </div>

                  <div className="evidence-stack">
                    <div className="evidence-chip">
                      <FileArrowUp aria-hidden="true" size={20} />
                      <span>Billing record</span>
                    </div>
                    <div className="evidence-chip">
                      <CalendarCheck aria-hidden="true" size={20} />
                      <span>Event timeline</span>
                    </div>
                    <div className="evidence-chip">
                      <ShieldCheck aria-hidden="true" size={20} />
                      <span>Governing terms</span>
                    </div>
                  </div>

                  <div className="review-gate">
                    <ShippingContainer aria-hidden="true" size={30} />
                    <span>Human review gate</span>
                    <strong>Potential credit or refund</strong>
                  </div>
                </div>

                <figcaption className="visually-hidden">
                  An illustrative D&amp;D invoice connects to billing, event,
                  and governing records before reaching a human review gate.
                </figcaption>
              </figure>
            </Reveal>
          </div>

          <div className="container hero-route-caption" aria-hidden="true">
            <span>Invoice</span>
            <span>Evidence</span>
            <span>Review</span>
            <span>Outcome</span>
          </div>
        </section>

        <section className="problem-section" aria-labelledby="problem-title">
          <div className="container problem-layout">
            <Reveal className="section-intro">
              <p className="eyebrow">The financial problem</p>
              <h2 id="problem-title">
                A D&amp;D charge is a finance line item. The answer lives in
                the record.
              </h2>
            </Reveal>

            <Reveal className="problem-copy" delay={0.08}>
              <p className="lead-copy">
                Detention and demurrage decisions rarely live in one document.
                The invoice shows what was billed. The operating record shows
                what happened. The governing terms show what should be tested.
              </p>
              <div className="problem-notes">
                <div className="problem-note">
                  <span>01</span>
                  <p>Find the charge inside the close, not after it.</p>
                </div>
                <div className="problem-note">
                  <span>02</span>
                  <p>Replace scattered records with one review path.</p>
                </div>
                <div className="problem-note">
                  <span>03</span>
                  <p>Stop where the evidence stops.</p>
                </div>
              </div>
            </Reveal>
          </div>
        </section>

        <section
          id="process"
          className="process-section"
          aria-labelledby="process-title"
        >
          <div className="container">
            <Reveal className="dark-section-intro">
              <p className="eyebrow eyebrow-blue">How it works</p>
              <h2 id="process-title">
                From invoice and data to a defensible next step.
              </h2>
              <p>
                The pilot follows the record in order. No black-box score and
                no shortcut around the facts.
              </p>
            </Reveal>

            <ol className="process-list">
              {processSteps.map((step, index) => (
                <Reveal
                  className="process-item"
                  delay={0.06 * index}
                  key={step.number}
                >
                  <li>
                    <span className="process-number">{step.number}</span>
                    <div>
                      <h3>{step.title}</h3>
                      <p>{step.description}</p>
                    </div>
                    {index < processSteps.length - 1 ? (
                      <ArrowRight
                        className="process-arrow"
                        aria-hidden="true"
                        size={22}
                      />
                    ) : (
                      <CheckCircle
                        className="process-check"
                        aria-hidden="true"
                        size={24}
                      />
                    )}
                  </li>
                </Reveal>
              ))}
            </ol>
          </div>
        </section>

        <section className="story-band" aria-labelledby="story-title">
          <div className="story-band-image">
            <Image
              src="/media/container-terminal-operations.jpg"
              alt="Container terminal operations at blue hour."
              fill
              sizes="(max-width: 820px) 100vw, 45vw"
              quality={88}
            />
          </div>
          <div className="container story-band-content">
            <Reveal>
              <p className="eyebrow eyebrow-blue">Why the detail matters</p>
              <h2 id="story-title">
                The record moves through the terminal before it reaches the
                ledger.
              </h2>
              <p>
                Availability, appointments, holds, closures, gate-out, empty
                return, and communications can change what a billed day means.
                A premium review makes those connections visible.
              </p>
            </Reveal>
          </div>
        </section>

        <section
          id="evidence"
          className="evidence-section"
          aria-labelledby="evidence-title"
        >
          <div className="container">
            <Reveal className="section-intro evidence-intro">
              <p className="eyebrow">What we review</p>
              <h2 id="evidence-title">Three records. One review path.</h2>
              <p>
                No single record proves the outcome. The useful work is in
                matching the records, dates, owners, and gaps.
              </p>
            </Reveal>

            <div className="evidence-panel">
              {evidenceLayers.map((layer, index) => {
                const Icon = evidenceIcons[layer.icon];
                return (
                  <Reveal
                    className="evidence-row"
                    delay={0.06 * index}
                    key={layer.title}
                  >
                    <div className="evidence-icon">
                      <Icon aria-hidden="true" size={24} />
                    </div>
                    <div className="evidence-row-title">
                      <span>{layer.label}</span>
                      <h3>{layer.title}</h3>
                    </div>
                    <p>{layer.description}</p>
                    <ArrowRight aria-hidden="true" size={20} />
                  </Reveal>
                );
              })}
            </div>

            <Reveal className="evidence-note" delay={0.1}>
              <WarningCircle aria-hidden="true" size={22} />
              <p>
                Missing a category? Mark the gap. Do not fill it with an
                assumption.
              </p>
            </Reveal>
          </div>
        </section>

        <section
          id="pilot-scope"
          className="pilot-scope-section"
          aria-labelledby="pilot-scope-title"
        >
          <div className="container pilot-scope-layout">
            <Reveal className="section-intro">
              <p className="eyebrow">Pilot scope</p>
              <h2 id="pilot-scope-title">
                Start small enough to trust the record.
              </h2>
              <p>
                The public form collects context, not invoices. Scope and data
                handling come before any secure file handoff.
              </p>
              <a className="text-link" href="/pilot">
                Request a pilot <ArrowRight aria-hidden="true" size={18} />
              </a>
            </Reveal>

            <div className="pilot-scope-list">
              {pilotScope.map((scope, index) => (
                <Reveal
                  className="pilot-scope-item"
                  delay={0.06 * index}
                  key={scope.number}
                >
                  <span>{scope.number}</span>
                  <div>
                    <h3>{scope.title}</h3>
                    <p>{scope.description}</p>
                  </div>
                </Reveal>
              ))}
            </div>
          </div>
        </section>

        <section
          id="trust"
          className="trust-section"
          aria-labelledby="trust-title"
        >
          <div className="container">
            <Reveal className="dark-section-intro trust-intro">
              <p className="eyebrow eyebrow-blue">Trust through restraint</p>
              <h2 id="trust-title">Evidence first. Claims second.</h2>
              <p>
                D&amp;D review is fact-specific. Official sources help frame
                the work; they do not guarantee eligibility, liability, or a
                refund.
              </p>
            </Reveal>

            <div className="trust-grid">
              <Reveal className="trust-card">
                <p className="card-label">Official sources</p>
                <h3>Check the source that governs the question.</h3>
                <div className="source-list">
                  {sourceLinks.map((source) => (
                    <a
                      href={source.href}
                      key={source.title}
                      target="_blank"
                      rel="noopener noreferrer"
                    >
                      <span>
                        <strong>{source.title}</strong>
                        <small>{source.issuer}</small>
                      </span>
                      <ArrowRight aria-hidden="true" size={18} />
                    </a>
                  ))}
                </div>
              </Reveal>

              <Reveal className="trust-card trust-card-warning" delay={0.08}>
                <p className="card-label">Where the Preview stops</p>
                <h3>No blanket eligibility. No guaranteed outcome.</h3>
                <ul className="boundary-list">
                  <li>Case facts and available evidence still control.</li>
                  <li>This public form does not accept invoice files.</li>
                  <li>Interpretation stays with a qualified human reviewer.</li>
                </ul>
              </Reveal>
            </div>

            <div className="faq-block">
              <Reveal className="faq-heading">
                <p className="card-label">Questions worth answering</p>
                <h3>Before a pilot conversation</h3>
              </Reveal>
              <div className="faq-list">
                {faqItems.map((item, index) => (
                  <Reveal delay={0.03 * index} key={item.question}>
                    <details>
                      <summary>{item.question}</summary>
                      <p>{item.answer}</p>
                    </details>
                  </Reveal>
                ))}
              </div>
            </div>
          </div>
        </section>

        <section className="closing-cta" aria-labelledby="closing-title">
          <div className="container closing-cta-layout">
            <div className="closing-route" aria-hidden="true">
              <span />
              <span />
              <span />
              <span />
            </div>
            <Reveal className="closing-copy">
              <p className="eyebrow eyebrow-blue">Start with the record</p>
              <h2 id="closing-title">
                Find the next question before you fight the charge.
              </h2>
              <p>
                Request a pilot conversation about scope, records, owners, and
                the right next step.
              </p>
              <a className="button" href="/pilot">
                Request a pilot
                <ArrowRight aria-hidden="true" size={18} />
              </a>
            </Reveal>
            <div className="closing-gate" aria-hidden="true">
              <CurrencyDollar size={32} />
              <span>Potential outcome</span>
              <strong>Human review required</strong>
            </div>
          </div>
        </section>
      </main>

      <SiteFooter />
    </MotionShell>
  );
}
