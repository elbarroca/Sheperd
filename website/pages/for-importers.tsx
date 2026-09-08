import { RecoveryLayout } from "@/components/recovery-layout";
import { CfoSection, ClosingSection, EconomicsSection, ImporterSection, RecoveryAction } from "@/components/recovery-sections";

export default function ForImportersPage() {
  return <RecoveryLayout title="For importers and finance teams | SheperD" description="A dedicated detention and demurrage recovery function for importers. Send invoices, pay nothing upfront, and let SheperD handle recovery."><section className="support-hero recovery-container"><p className="section-label">For importers / Finance leaders</p><h1>Your shipping history.<br />A potential source of capital.</h1><p>Recover potential value from historical freight expense without building an internal recovery team.</p><RecoveryAction /></section><CfoSection /><EconomicsSection /><ImporterSection /><ClosingSection /></RecoveryLayout>;
}
