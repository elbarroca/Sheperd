import Head from "next/head";

import { NoticePage } from "@/components/notice-page";

const sections = [
  {
    heading: "Information in a contact inquiry",
    body: "The contact forms ask for your name, email address, company, inquiry type, and message. The forms do not accept file uploads. Do not include confidential invoice, shipment, or financial details in a message.",
  },
  {
    heading: "Purpose and recipient",
    body: "SheperD uses these details to understand and reply to your inquiry. When Netlify Forms is enabled, Netlify receives the submission and stores it in the site's Netlify account. Configured email notifications go to michaelk@sheperd.io. The visitor's email field is named email so the notification can use it as Reply-to.",
  },
  {
    heading: "Retention and processing terms",
    body: "The retention period, deletion process, data owner, and additional processing terms still require approval. Confirm them before enabling live collection.",
  },
] as const;

export default function PrivacyPage() {
  return (
    <>
      <Head>
        <title>Privacy notice | SheperD</title>
        <meta name="robots" content="noindex,nofollow,noarchive" />
      </Head>
      <NoticePage
        eyebrow="Privacy notice"
        title="Contact form information."
        summary="The SheperD contact forms collect details to help the team understand and answer inquiries."
        sections={sections}
      />
    </>
  );
}
