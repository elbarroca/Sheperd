import type { ReactElement } from "react";
import { RecoveryLayout } from "./recovery-layout";
import {
  CfoSection,
  ClosingSection,
  EconomicsSection,
  ImporterSection,
  MissedValueSection,
  ProcessSection,
  RecoveryHero,
} from "./recovery-sections";

export function RecoveryCorridor(): ReactElement {
  return (
    <RecoveryLayout
      title="SheperD | Detention & Demurrage Recovery"
      description="You send the invoices. SheperD handles detention and demurrage recovery for importers. No upfront cost. Paid when you recover value."
    >
      <RecoveryHero />
      <CfoSection />
      <ProcessSection />
      <MissedValueSection />
      <EconomicsSection />
      <ImporterSection />
      <ClosingSection />
    </RecoveryLayout>
  );
}
