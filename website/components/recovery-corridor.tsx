import { ArrowDown, ArrowUpRight, Check, Plus } from "@phosphor-icons/react";
import Image from "next/image";

import { evidenceLayers, faqItems, pilotScope, processSteps, sourceLinks } from "@/lib/content";

import { PilotLink } from "./pilot-link";
import { RecoveryHero } from "./recovery-hero";
import { SiteFooter } from "./site-footer";
import { SiteHeader } from "./site-header";

export function RecoveryCorridor() {
  return (
    <>
      <a className="skip-link" href="#main-content">Skip to content</a>
      <div className="announcement">
        <p>D&amp;D recovery for importer finance teams</p>
        <a href="#process">A closer look at the method <ArrowUpRight aria-hidden="true" size={13} /></a>
      </div>
      <SiteHeader />
      <main id="main-content" tabIndex={-1}>
        <RecoveryHero />

        <section className="intro-section section-paper" aria-labelledby="intro-title">
          <div className="container intro-layout">
            <h2 id="intro-title">The invoice starts the question.<br />The record carries it.</h2>
            <p>
              A charge is easy to see. The dates, events, and terms behind it take
              a closer look. We bring those records together so your team can
              understand what supports the charge, what is missing, and what to
              review next.
            </p>
          </div>
        </section>

        <section id="process" className="process-section section-teal" aria-labelledby="process-title">
          <div className="container">
            <div className="section-heading">
              <div>
                <p className="eyebrow">How it works</p>
                <h2 id="process-title">From billed<br />to reviewed.</h2>
              </div>
              <p>Three deliberate steps. One clear record. Every conclusion stays tied to the evidence.</p>
            </div>
            <ol className="process-list">
              {processSteps.map((step) => (
                <li className="process-item" key={step.number}>
                  <span className="step-number" aria-hidden="true">{step.number}</span>
                  <h3>{step.title}</h3>
                  <p>{step.description}</p>
                </li>
              ))}
            </ol>
            <p className="process-boundary"><Check aria-hidden="true" size={17} /> Human review before any carrier credit or refund outcome.</p>
          </div>
        </section>

        <section id="evidence" className="evidence-section section-ice" aria-labelledby="evidence-title">
          <div className="container evidence-layout">
            <div className="evidence-intro">
              <p className="eyebrow">What we review</p>
              <h2 id="evidence-title">One charge.<br />Three records.</h2>
              <p>No single document tells the whole story. The useful work is in connecting what was billed to what happened, and what governs it.</p>
              <a className="text-link" href="#pilot-scope">Explore the pilot scope <ArrowDown aria-hidden="true" size={17} /></a>
            </div>
            <div className="evidence-list">
              {evidenceLayers.map((layer) => (
                <article className="evidence-row" key={layer.icon}>
                  <p className="record-label">{layer.label}</p>
                  <h3>{layer.title}</h3>
                  <p>{layer.description}</p>
                </article>
              ))}
              <p className="evidence-note">Missing a record? Mark the gap. Keep the question open.</p>
            </div>
          </div>
        </section>

        <section className="story-band" aria-labelledby="story-title">
          <div className="story-band-image">
            <Image src="/media/container-terminal-operations.jpg" alt="An illustrative container terminal at blue hour." fill sizes="100vw" quality={78} />
          </div>
          <div className="container story-band-copy">
            <p className="eyebrow">Beyond the line item</p>
            <h2 id="story-title">The details move<br />through the terminal<br />before the ledger.</h2>
            <p>Availability, appointments, holds, and empty returns can change what a billed day means.</p>
          </div>
        </section>

        <section id="pilot-scope" className="pilot-scope-section section-paper" aria-labelledby="pilot-scope-title">
          <div className="container pilot-scope-layout">
            <div className="pilot-scope-copy">
              <p className="eyebrow">Pilot scope</p>
              <h2 id="pilot-scope-title">Start with<br />a focused review.</h2>
              <p>Bring the charge and the surrounding record into the same conversation. Agree the scope before the work begins.</p>
              <PilotLink className="button">Request a pilot</PilotLink>
              <p className="availability-note">Pilot intake is currently unavailable.</p>
            </div>
            <dl className="pilot-scope-list">
              {pilotScope.map((scope) => (
                <div className="pilot-scope-item" key={scope.number}>
                  <dt>{scope.title}</dt>
                  <dd>{scope.description}</dd>
                </div>
              ))}
              <div className="pilot-scope-item">
                <dt>A clear boundary</dt>
                <dd>No public invoice uploads. No guaranteed recovery. Any engagement and data handling are agreed separately.</dd>
              </div>
            </dl>
          </div>
        </section>

        <section id="trust" className="trust-section section-paper" aria-labelledby="trust-title">
          <div className="container">
            <div className="trust-layout">
              <div>
                <p className="eyebrow">Trust and transparency</p>
                <h2 id="trust-title">Evidence first.<br />Claims second.</h2>
                <p className="trust-summary">D&amp;D review is fact-specific. Start with the source, keep the gaps visible, and leave interpretation to a qualified reviewer.</p>
              </div>
              <div className="source-list">
                <p className="record-label">Read the original sources</p>
                {sourceLinks.map((source) => (
                  <a href={source.href} key={source.title} target="_blank" rel="noopener noreferrer">
                    <span><strong>{source.title}</strong><small>{source.issuer}</small></span>
                    <ArrowUpRight aria-hidden="true" size={20} />
                  </a>
                ))}
                <p className="source-note">Official sources frame the review. They do not guarantee eligibility, liability, or a refund.</p>
              </div>
            </div>
            <div className="faq-block">
              <h3>Questions before a pilot</h3>
              <div className="faq-list">
                {faqItems.map((item) => (
                  <details key={item.question}>
                    <summary>{item.question}<Plus aria-hidden="true" size={19} /></summary>
                    <p>{item.answer}</p>
                  </details>
                ))}
              </div>
            </div>
          </div>
        </section>

        <section className="closing-cta" aria-labelledby="closing-title">
          <div className="container closing-copy">
            <p className="eyebrow">The next step</p>
            <h2 id="closing-title">Bring the next question<br />to the record.</h2>
            <p>A clearer starting point for your team, your records, and the review ahead.</p>
            <PilotLink className="button button-light">Request a pilot</PilotLink>
            <p className="hero-boundary">Case-specific review. No guaranteed recovery.</p>
          </div>
        </section>
      </main>
      <SiteFooter />
    </>
  );
}
