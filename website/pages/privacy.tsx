import Head from "next/head";

import { NoticePage } from "@/components/notice-page";

const sections = [
  {
    heading: "Calendly scheduling",
    body: (
      <>
        When a Calendly link is configured, the contact page embeds a Calendly booking
        page. Calendly processes details submitted there to schedule the meeting. Read
        the{" "}
        <a href="https://calendly.com/legal/privacy-notice" target="_blank" rel="noopener noreferrer">
          Calendly Privacy Notice
        </a>
        .
      </>
    ),
  },
  {
    heading: "SheperD enquiry form",
    body: "The enquiry form remains disabled in this Preview. It does not send details to SheperD. The Calendly booking page is separate and follows Calendly’s own cookie settings.",
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
        title="Calendly booking disclosure."
        summary="When configured, the contact page embeds Calendly for meeting bookings. Details entered in that booking page are processed by Calendly. The SheperD enquiry form remains disabled in this Preview."
        sections={sections}
      />
    </>
  );
}
