import { NoticePage } from "@/components/notice-page";
import { SeoHead } from "@/components/seo-head";

const sections = [
  {
    heading: "Pilot intake is unavailable",
    body: "The pilot form is disabled. It does not accept or submit your details, upload files, send email, or create a record in a CRM. Please do not send invoice or shipment information through this website.",
  },
  {
    heading: "Analytics and advertising",
    body: "This website does not include analytics, advertising pixels, session replay, or marketing cookies. Its fonts and visual assets are served with the website.",
  },
  {
    heading: "Website hosting",
    body: "The site is hosted on Vercel. Visiting a website involves requests to its hosting provider, which may process technical connection information to deliver and secure the site.",
  },
  {
    heading: "Contact and external links",
    body: "Email and phone links use your own email or calling app. Those conversations are separate from this website's disabled form. Links to sheperd.io and official sources open separate websites. Their privacy practices may differ.",
  },
  {
    heading: "Before intake opens",
    body: "The data owner, information collected, purpose, retention period, and contact route will be stated before pilot intake is enabled. This notice describes the website as it operates today.",
  },
] as const;

export default function PrivacyPage() {
  return (
    <>
      <SeoHead title="Privacy notice | SheperD" description="How the SheperD website handles pilot intake, hosting, external links, and measurement." path="/privacy" indexable={false} />
      <NoticePage eyebrow="Privacy notice" title="Your information stays out of the form." summary="Pilot intake on this website is currently unavailable. The form is disabled, and this website does not accept invoice files or pilot submissions." sections={sections} />
    </>
  );
}
