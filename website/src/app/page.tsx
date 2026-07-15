import { ContainerHero } from "@/components/logistics/container-hero";
import { EvidenceStack } from "@/components/logistics/evidence-stack";
import { InvoiceManifest } from "@/components/logistics/invoice-manifest";
import { PortGrid } from "@/components/logistics/port-grid";
import { RecoveryRoute } from "@/components/logistics/recovery-route";
import { SectionReveal } from "@/components/motion/section-reveal";
import { FaqSection } from "@/components/sections/faq-section";
import { LimitsSection } from "@/components/sections/limits-section";

export default function HomePage(): React.JSX.Element {
  return (
    <main id="main-content">
      <div id="top" />
      <ContainerHero />
      <SectionReveal variant="lift">
        <InvoiceManifest />
      </SectionReveal>
      <SectionReveal variant="shift">
        <EvidenceStack />
      </SectionReveal>
      <SectionReveal variant="settle">
        <RecoveryRoute />
      </SectionReveal>
      <SectionReveal variant="lift">
        <FaqSection />
      </SectionReveal>
      <SectionReveal variant="shift">
        <LimitsSection />
      </SectionReveal>
      <SectionReveal variant="settle">
        <PortGrid />
      </SectionReveal>
    </main>
  );
}
