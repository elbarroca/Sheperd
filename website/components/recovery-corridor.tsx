import { ArrowDown, ArrowUpRight, Check, Plus } from "@phosphor-icons/react";
import Image from "next/image";

import { evidenceLayers, faqItems, pilotScope, processSteps, sourceLinks } from "@/lib/content";

import { PilotLink } from "./pilot-link";
import { RecoveryHero } from "./recovery-hero";
import { ScrollHeading, ScrollReveal } from "./scroll-reveals";
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
            <ScrollHeading id="intro-title" lines={["The invoice starts the question.", "The record carries it."]} />
            <ScrollReveal as="p">
              A charge is easy to see. The dates, events, and terms behind it take
              a closer look. We bring those records together so your team can
              understand what supports the charge, what is missing, and what to
              review next.
            </ScrollReveal>
          </div>
        </section>

        <section id="process" className="process-section section-teal" aria-labelledby="process-title">
          <div className="container">
            <div className="section-heading">
              <div>
                <p className="eyebrow">How it works</p>
                <ScrollHeading id="process-title" lines={["From billed", "to reviewed."]} />
              </div>
              <ScrollReveal as="p">Three deliberate steps. One clear record. Every conclusion stays tied to the evidence.</ScrollReveal>
            </div>
            <ol className="process-list">
              {processSteps.map((step, index) => (
                <ScrollReveal as="li" className="process-item" delay={index * 0.08} key={step.number}>
                  <span className="step-number" aria-hidden="true">{step.number}</span>
                  <h3>{step.title}</h3>
                  <p>{step.description}</p>
                </ScrollReveal>
              ))}
            </ol>
            <ScrollReveal as="p" className="process-boundary" delay={0.28}><Check aria-hidden="true" size={17} /> Human review before any carrier credit or refund outcome.</ScrollReveal>
          </div>
        </section>

        <section id="evidence" className="evidence-section section-ice" aria-labelledby="evidence-title">
          <div className="container evidence-layout">
            <div className="evidence-intro">
              <p className="eyebrow">What we review</p>
              <ScrollHeading id="evidence-title" lines={["One charge.", "Three records."]} />
              <ScrollReveal as="p">No single document tells the whole story. The useful work is in connecting what was billed to what happened, and what governs it.</ScrollReveal>
              <a className="text-link" href="#pilot-scope">Explore the pilot scope <ArrowDown aria-hidden="true" size={17} /></a>
            </div>
            <div className="evidence-list">
              {evidenceLayers.map((layer, index) => (
                <ScrollReveal as="article" className="evidence-row" delay={index * 0.08} key={layer.icon}>
                  <p className="record-label">{layer.label}</p>
                  <h3>{layer.title}</h3>
                  <p>{layer.description}</p>
                </ScrollReveal>
              ))}
              <ScrollReveal as="p" className="evidence-note" delay={0.24}>Missing a record? Mark the gap. Keep the question open.</ScrollReveal>
            </div>
          </div>
        </section>

        <section className="story-band" aria-labelledby="story-title">
          <div className="story-band-image">
            <Image src="/media/container-terminal-operations.jpg" alt="An illustrative container terminal at blue hour." fill sizes="100vw" quality={78} />
          </div>
          <div className="container story-band-copy">
            <p className="eyebrow">Beyond the line item</p>
            <ScrollHeading id="story-title" lines={["The details move", "through the terminal", "before the ledger."]} />
            <ScrollReveal as="p">Availability, appointments, holds, and empty returns can change what a billed day means.</ScrollReveal>
          </div>
        </section>

        <section id="pilot-scope" className="pilot-scope-section section-paper" aria-labelledby="pilot-scope-title">
          <div className="container pilot-scope-layout">
            <div className="pilot-scope-copy">
              <p className="eyebrow">Pilot scope</p>
              <ScrollHeading id="pilot-scope-title" lines={["Start with", "a focused review."]} />
              <ScrollReveal as="p">Bring the charge and the surrounding record into the same conversation. Agree the scope before the work begins.</ScrollReveal>
              <PilotLink className="button">Request a pilot</PilotLink>
              <p className="availability-note">Pilot intake is currently unavailable.</p>
            </div>
            <dl className="pilot-scope-list">
              {pilotScope.map((scope, index) => (
                <ScrollReveal as="div" className="pilot-scope-item" delay={index * 0.07} key={scope.number}>
                  <dt>{scope.title}</dt>
                  <dd>{scope.description}</dd>
                </ScrollReveal>
              ))}
              <ScrollReveal as="div" className="pilot-scope-item" delay={0.21}>
                <dt>A clear boundary</dt>
                <dd>No public invoice uploads. No guaranteed recovery. Any engagement and data handling are agreed separately.</dd>
              </ScrollReveal>
            </dl>
          </div>
        </section>

        <section id="trust" className="trust-section section-paper" aria-labelledby="trust-title">
          <div className="container">
            <div className="trust-layout">
              <div>
                <p className="eyebrow">Trust and transparency</p>
                <ScrollHeading id="trust-title" lines={["Evidence first.", "Claims second."]} />
                <ScrollReveal as="p" className="trust-summary">D&amp;D review is fact-specific. Start with the source, keep the gaps visible, and leave interpretation to a qualified reviewer.</ScrollReveal>
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
              <ScrollReveal as="h3">Questions before a pilot</ScrollReveal>
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
            <ScrollHeading id="closing-title" lines={["Bring the next question", "to the record."]} />
            <ScrollReveal as="p">A clearer starting point for your team, your records, and the review ahead.</ScrollReveal>
            <PilotLink className="button button-light">Request a pilot</PilotLink>
            <p className="hero-boundary">Case-specific review. No guaranteed recovery.</p>
          </div>
        </section>
      </main>
      <SiteFooter />
    </>
  );
}
