import { NoticePage } from "@/components/notice-page";
import { SeoHead } from "@/components/seo-head";

const sections = [
  {
    heading: "Information, not a case decision",
    body: "This website describes SheperD's managed detention and demurrage services and invoice review approach. It does not assess a charge, determine eligibility or liability, or provide legal advice.",
  },
  {
    heading: "No guaranteed recovery",
    body: "Any recovery opportunity depends on the available records, governing terms, operational facts, and applicable process. A carrier credit or refund is never guaranteed.",
  },
  {
    heading: "Pilot availability",
    body: "Pilot intake on this website is currently unavailable. Viewing the form does not submit a request or establish an engagement. Scope, responsibilities, commercial terms, and data handling are agreed before work begins. Payment, financing, and credit arrangements require separate agreement.",
  },
  {
    heading: "Sources and imagery",
    body: "Official source material can change. Verify the current source and keep interpretation with a qualified human reviewer. Terminal imagery is illustrative and does not depict a customer shipment, actual case, or recovery outcome.",
  },
] as const;

export default function TermsPage() {
  return (
    <>
      <SeoHead title="Use notice | SheperD" description="The scope and limits of information on the SheperD website, including pilot availability and case-specific review." path="/terms" indexable={false} />
      <NoticePage eyebrow="Use notice" title="A clear starting point. A defined boundary." summary="Use this website to understand the review approach and the records involved. Case decisions require current sources and qualified human review." sections={sections} />
    </>
  );
}
