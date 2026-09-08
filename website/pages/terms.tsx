import Head from "next/head";

import { NoticePage } from "@/components/notice-page";

const sections = [
  {
    heading: "Local marketing Preview",
    body: "The page recreates the currently selected SheperD marketing direction for design and engineering review. It does not evaluate a charge, determine compliance, or provide legal advice.",
  },
  {
    heading: "No submitted request",
    body: "Online enquiries and invoice uploads are disabled in this preview. Browsing the site does not submit a service request or create a commercial relationship.",
  },
  {
    heading: "Use current sources and qualified review",
    body: "Official material can change and case conclusions depend on specific facts. Verify current source text and keep interpretation with a qualified human reviewer.",
  },
] as const;

export default function TermsPage() {
  return (
    <>
      <Head>
        <title>Use notice | SheperD Preview</title>
        <meta name="robots" content="noindex,nofollow,noarchive" />
      </Head>
      <NoticePage
        eyebrow="Preview use notice"
        title="A design Preview, not a service decision."
        summary="Use this local build to review the selected visual system and conversion path before publication approvals are complete."
        sections={sections}
      />
    </>
  );
}
