import type { ReactElement } from "react";
import { RecoveryLayout } from "./recovery-layout";
import {
  CfoSection,
  ClosingSection,
  EconomicsSection,
  ImporterSection,
  MarketOpportunitySection,
  ProcessSection,
  RecoveryHero,
} from "./recovery-sections";

export function RecoveryCorridor(): ReactElement {
  return (
    <RecoveryLayout
      title="SheperD | A clear path through D&D recovery"
      description="A clear path from invoice to recovery. You send the invoices. SheperD handles detention and demurrage recovery for importers. No upfront cost. Paid when you recover value."
    >
      <RecoveryHero />
      <CfoSection editorial />
      <ProcessSection />
      <MarketOpportunitySection />
      <EconomicsSection />
      <ImporterSection />
      <ClosingSection />
    </RecoveryLayout>
  );
}
