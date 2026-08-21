import Head from "next/head";

import { MotionShell, Reveal } from "@/components/motion-shell";
import { PilotForm } from "@/components/pilot-form";
import { SiteFooter } from "@/components/site-footer";
import { SiteHeader } from "@/components/site-header";

export default function PilotPage() {
  return (
    <>
      <Head>
        <title>Request a pilot | SheperD Preview</title>
        <meta
          name="description"
          content="Request a case-specific SheperD pilot conversation for detention and demurrage invoice review."
        />
        <meta name="robots" content="noindex,nofollow,noarchive,noimageindex" />
      </Head>

      <MotionShell>
        <a className="skip-link" href="#main-content">
          Skip to content
        </a>
        <SiteHeader />
        <main id="main-content" className="pilot-page" tabIndex={-1}>
          <section className="pilot-hero" aria-labelledby="pilot-title">
            <div className="container pilot-hero-layout">
              <Reveal className="pilot-hero-copy">
                <p className="eyebrow eyebrow-blue">
                  Case-specific pilot conversation
                </p>
                <h1 id="pilot-title">Start with the record.</h1>
                <p>
                  Tell us what your team is trying to understand. The first
                  step is scope, ownership, and evidence readiness—not an
                  invoice upload.
                </p>
                <p className="hero-boundary">
                  No guaranteed recovery. No public file upload.
                </p>
              </Reveal>

              <Reveal className="pilot-form-card" delay={0.08}>
                <div className="section-marker">PILOT INTAKE / METADATA ONLY</div>
                <PilotForm />
              </Reveal>
            </div>
          </section>
        </main>
        <SiteFooter />
      </MotionShell>
    </>
  );
}
