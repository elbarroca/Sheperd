import Head from "next/head";

import { NoticePage } from "@/components/notice-page";

const sections = [
  {
    heading: "Online enquiries are disabled",
    body: "This preview does not display enquiry fields or accept invoice uploads. No enquiry details are transmitted, stored, emailed, or sent to a CRM.",
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
        summary="Online enquiries are disabled in this preview. No customer details are collected, stored, or sent."
        sections={sections}
      />
    </>
  );
}
