import type { ReactElement } from "react";
import { ContactForm } from "@/components/contact-form";
import { RecoveryLayout } from "@/components/recovery-layout";

export default function ContactPage(): ReactElement {
  return (
    <RecoveryLayout
      title="Contact SheperD"
      description="Contact SheperD about detention and demurrage invoice recovery."
    >
      <ContactForm formName="contact-page" />
    </RecoveryLayout>
  );
}
