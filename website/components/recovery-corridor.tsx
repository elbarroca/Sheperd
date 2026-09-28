import type { ReactElement } from "react";
import { RecoveryLayout } from "./recovery-layout";
import {
  CalendlySection,
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
      title="SheperD | D&D recovery potential for U.S. importers"
      description="Could three years of U.S. detention and demurrage charges put real money back on your bottom line? Explore potential refunds and carrier credits."
    >
      <RecoveryHero />
      <MarketOpportunitySection />
      <ProcessSection />
      <EconomicsSection />
      <ImporterSection />
      <CalendlySection />
      <ClosingSection />
    </RecoveryLayout>
  );
}
