import Head from "next/head";

import { NoticePage } from "@/components/notice-page";

const sections = [
  {
    heading: "Preview interaction only",
    body: "The audit form demonstrates the intended interaction locally. Submitting it resets the fields and shows a confirmation state; no value is transmitted, stored, emailed, or sent to a CRM.",
  },
  {
    heading: "No measurement layer",
    body: "The local Preview includes no analytics, advertising pixels, cookies, session replay, CRM routing, or third-party runtime requests.",
  },
  {
    heading: "Publication boundary",
    body: "This is a local design and engineering Preview. A production privacy notice, data owner, retention policy, and approved processing terms have not been established here.",
  },
] as const;

export default function PrivacyPage() {
  return (
    <>
      <Head>
        <title>Privacy notice | SheperD Preview</title>
        <meta name="robots" content="noindex,nofollow,noarchive" />
      </Head>
      <NoticePage
        eyebrow="Preview privacy notice"
        title="No transmission in this Preview."
        summary="The current form is an interaction prototype. It is not connected to an intake, email, analytics, or storage service."
        sections={sections}
      />
    </>
  );
}
