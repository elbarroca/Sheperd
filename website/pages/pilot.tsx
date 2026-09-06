import { PilotForm } from "@/components/pilot-form";
import { SeoHead } from "@/components/seo-head";
import { SiteFooter } from "@/components/site-footer";
import { SiteHeader } from "@/components/site-header";
import { liveSource } from "@/lib/content";

export default function PilotPage() {
  return (
    <>
      <SeoHead
        title="Request a pilot | SheperD"
        description="Discuss managed D&D support for your import team. This website's pilot form is disabled; use the published SheperD contact details to get in touch."
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
                D&amp;D support for U.S. importers
              </p>
              <h1 id="pilot-title">Start with the record.</h1>
              <p>
                Discuss the invoices, carrier questions, and support your team
                needs. Scope, responsibilities, and a secure record handoff are
                agreed before work begins.
              </p>
              <p>
                This website&apos;s form is disabled. You can contact the team at{" "}
                <a className="text-link" href={`mailto:${liveSource.contactEmail}`}>{liveSource.contactEmail}</a>.
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
