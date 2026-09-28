import { ArrowUpRight } from "@phosphor-icons/react";

import { MotionShell } from "@/components/motion-shell";
import { PilotForm } from "@/components/pilot-form";
import { RecoveryLayout } from "@/components/recovery-layout";

const CALENDLY_EVENT_URL = "";

export default function ContactPage() {
  return (
    <RecoveryLayout
      title="Start a recovery enquiry | SheperD"
      description="Talk with SheperD about detention and demurrage recovery for your import invoices."
    >
      <section className="recovery-container enquiry-page" aria-labelledby="contact-title">
        <div>
          <p className="section-label">Your next step</p>
          <h1 id="contact-title">
            Put your shipping<br />history to work.
          </h1>
          <p>You send the invoices.<br />We handle the recovery.</p>
          <p className="enquiry-terms">No upfront cost. We get paid when you recover value.</p>
        </div>
        <MotionShell>
          <PilotForm />
        </MotionShell>
      </section>

      <section className="calendly-section" id="schedule" aria-labelledby="schedule-title">
        <div className="recovery-container calendly-content">
          <div className="calendly-intro">
            <p className="section-label">Your next step</p>
            <h2 id="schedule-title">Choose a time to talk.</h2>
            <p>
              Book a conversation about your invoices, the records around the charges,
              and what a focused recovery review would involve.
            </p>
          </div>
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
            <p className="calendly-unavailable" role="status">
              Online scheduling is not available yet. No booking details are collected here.
            </p>
          )}
        </div>
      </section>
    </RecoveryLayout>
  );
}
