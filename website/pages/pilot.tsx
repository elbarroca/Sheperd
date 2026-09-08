import { RecoveryLayout } from "@/components/recovery-layout";
import { PilotForm } from "@/components/pilot-form";
import { MotionShell } from "@/components/motion-shell";

export default function PilotPage() {
  return <RecoveryLayout title="Find recoverable value | SheperD" description="Start a SheperD recovery enquiry. No upfront cost. You send the invoices; we handle the recovery."><section className="recovery-container enquiry-page"><div><p className="section-label">Your next step</p><h1>Put your shipping<br />history to work.</h1><p>You send the invoices.<br />We handle the recovery.</p><p className="enquiry-terms">No upfront cost. We get paid when you recover value.</p></div><MotionShell><PilotForm /></MotionShell></section></RecoveryLayout>;
}
