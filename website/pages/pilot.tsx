import { PilotForm } from "@/components/pilot-form";
import { SeoHead } from "@/components/seo-head";
import { SiteFooter } from "@/components/site-footer";
import { SiteHeader } from "@/components/site-header";

export default function PilotPage() {
  return (
    <>
      <SeoHead
        title="Request a pilot | SheperD"
        description="Request a case-specific SheperD pilot conversation for detention and demurrage invoice review."
        path="/pilot"
        indexable={false}
      />

      <a className="skip-link" href="#main-content">
        Skip to content
      </a>
      <SiteHeader />
      <main id="main-content" className="pilot-page" tabIndex={-1}>
        <section className="pilot-hero" aria-labelledby="pilot-title">
          <div className="container pilot-hero-layout">
            <div className="pilot-hero-copy">
              <p className="eyebrow eyebrow-blue">
                Case-specific pilot conversation
              </p>
              <h1 id="pilot-title">Start with the record.</h1>
              <p>
                Tell us what your team is trying to understand. The first step
                is scope, ownership, and evidence readiness—not an invoice
                upload.
              </p>
              <p className="hero-boundary">
                No guaranteed recovery. No public file upload.
              </p>
            </div>

            <div className="pilot-form-card">
              <div className="section-marker">PILOT INTAKE / METADATA ONLY</div>
              <PilotForm />
            </div>
          </div>
        </section>
      </main>
      <SiteFooter />
    </>
  );
}
