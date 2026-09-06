import { ArrowDown, ArrowUpRight, Check, Plus } from "@phosphor-icons/react";
import Image from "next/image";

import { evidenceLayers, faqItems, pilotScope, processSteps, sourceLinks } from "@/lib/content";

import { PilotLink } from "./pilot-link";
import { RecoveryHero } from "./recovery-hero";
import { ScrollHeading, ScrollReveal } from "./scroll-reveals";
import { ScrollSection } from "./scroll-section";
import { SiteFooter } from "./site-footer";
import { SiteHeader } from "./site-header";

export function RecoveryCorridor() {
  return (
    <>
      <a className="skip-link" href="#main-content">Skip to content</a>
      <div className="announcement">
        <p>Detention &amp; demurrage support for U.S. importers</p>
        <a href="#process">A closer look at the method <ArrowUpRight aria-hidden="true" size={13} /></a>
      </div>
      <SiteHeader />
      <main id="main-content" tabIndex={-1}>
        <RecoveryHero />

        <ScrollSection className="intro-section section-paper" labelledBy="intro-title" variant="intro">
          <div className="container intro-layout">
            <ScrollHeading id="intro-title" lines={["One point of contact.", "Across the D&D process."]} treatment="line" />
            <p>
              Invoices, terminal events, and carrier correspondence often sit
              with different teams. SheperD brings them together, helping finance
              and logistics move from a billing question to a documented next
              step. A service team alongside yours.
            </p>
          </div>
        </ScrollSection>

        <ScrollSection id="process" className="process-section section-teal" labelledBy="process-title" variant="process">
          <div className="container">
            <div className="section-heading">
              <div>
                <p className="eyebrow">How it works</p>
                <ScrollHeading id="process-title" lines={["From billed", "to reviewed."]} treatment="word" />
              </div>
              <p>Share the context. Let the team coordinate the review. Follow the carrier response through to the outcome.</p>
            </div>
            <ol className="process-list">
              {processSteps.map((step, index) => (
                <ScrollReveal as="li" className="process-item" delay={index * 0.08} key={step.number} variant="slide">
                  <span className="step-number" aria-hidden="true">{step.number}</span>
                  <h3>{step.title}</h3>
                  <p>{step.description}</p>
                </ScrollReveal>
              ))}
            </ol>
            <ScrollReveal as="p" className="process-boundary" delay={0.28} variant="fade"><Check aria-hidden="true" size={17} /> Human review before any carrier credit or refund outcome.</ScrollReveal>
          </div>
        </ScrollSection>

        <ScrollSection id="evidence" className="evidence-section section-ice" labelledBy="evidence-title" variant="evidence">
          <div className="container evidence-layout">
            <div className="evidence-intro">
              <p className="eyebrow">What we review</p>
              <ScrollHeading id="evidence-title" lines={["One charge.", "Three records."]} treatment="plain" />
              <p>No single document tells the whole story. The useful work is in connecting what was billed to what happened, and what governs it.</p>
              <a className="text-link" href="#pilot-scope">Explore the pilot scope <ArrowDown aria-hidden="true" size={17} /></a>
            </div>
            <div className="evidence-list">
              {evidenceLayers.map((layer, index) => (
                <ScrollReveal as="article" className="evidence-row" delay={index * 0.08} key={layer.icon} variant="slide">
                  <p className="record-label">{layer.label}</p>
                  <h3>{layer.title}</h3>
                  <p>{layer.description}</p>
                </ScrollReveal>
              ))}
              <p className="evidence-note">Missing a record? Mark the gap. Keep the question open.</p>
            </div>
          </div>
        </ScrollSection>

        <ScrollSection className="story-band" labelledBy="story-title" variant="story">
          <div className="story-band-image">
            <Image src="/media/container-terminal-operations.jpg" alt="An illustrative container terminal at blue hour." fill sizes="100vw" quality={78} />
          </div>
          <div className="container story-band-copy">
            <p className="eyebrow">Beyond the line item</p>
            <ScrollHeading id="story-title" lines={["The details move", "through the terminal", "before the ledger."]} treatment="line" />
            <p>Availability, appointments, holds, and empty returns can change what a billed day means.</p>
          </div>
        </ScrollSection>

        <ScrollSection id="pilot-scope" className="pilot-scope-section section-paper" labelledBy="pilot-scope-title" variant="pilot">
          <div className="container pilot-scope-layout">
            <div className="pilot-scope-copy">
              <p className="eyebrow">Pilot scope</p>
              <ScrollHeading id="pilot-scope-title" lines={["Start with", "a focused review."]} treatment="block" />
              <p>Begin with the invoices and the support your team needs. Invoice monitoring, carrier coordination, and dispute work are agreed around your scope.</p>
              <PilotLink className="button">Request a pilot</PilotLink>
              <p className="availability-note">Pilot intake on this website is currently unavailable. Contact details are in the footer.</p>
            </div>
            <dl className="pilot-scope-list">
              {pilotScope.map((scope, index) => (
                <ScrollReveal as="div" className="pilot-scope-item" delay={index * 0.07} key={scope.number} variant="fade">
                  <dt>{scope.title}</dt>
                  <dd>{scope.description}</dd>
                </ScrollReveal>
              ))}
              <ScrollReveal as="div" className="pilot-scope-item" delay={0.21} variant="fade">
                <dt>A clear boundary</dt>
                <dd>No public invoice uploads. No guaranteed recovery. Any engagement and data handling are agreed separately.</dd>
              </ScrollReveal>
            </dl>
          </div>
        </ScrollSection>

        <ScrollSection id="trust" className="trust-section section-paper" labelledBy="trust-title" variant="trust">
          <div className="container">
            <div className="trust-layout">
              <div>
                <p className="eyebrow">Trust and transparency</p>
                <ScrollHeading id="trust-title" lines={["Evidence first.", "Claims second."]} treatment="plain" />
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
        </ScrollSection>

        <ScrollSection className="closing-cta" labelledBy="closing-title" variant="closing">
          <div className="container closing-copy">
            <p className="eyebrow">The next step</p>
            <ScrollHeading id="closing-title" lines={["Bring your D&D questions", "to one team."]} treatment="block" />
            <p>Start with the invoice, the shipment context, and the support your team needs.</p>
            <PilotLink className="button button-light">Request a pilot</PilotLink>
          </div>
        </ScrollSection>
      </main>
      <SiteFooter />
    </>
  );
}
