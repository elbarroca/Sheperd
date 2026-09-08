import { RecoveryLayout } from "@/components/recovery-layout";
import { ClosingSection, MissedValueSection, PortArt } from "@/components/recovery-sections";

export default function AboutPage() {
  return <RecoveryLayout title="About SheperD | Freight recovery for importers" description="SheperD looks back at historical detention and demurrage charges to find and pursue potential recovered value for importers."><section className="support-hero recovery-container"><p className="section-label">About SheperD</p><h1>Freight moves forward.<br />We look back for value.</h1><p>Our mission is to make freight recovery a standard financial discipline for importers.</p></section><div className="about-port"><PortArt /></div><MissedValueSection /><section className="section-pad recovery-container support-copy"><h2>Recovery is the entire mission.</h2><p>Once freight expenses are paid, they are often treated as final. Historical detention and demurrage activity can deserve a second look.</p><p>SheperD gives that history a dedicated recovery process, from review through resolution. You send the invoices. We handle the work.</p></section><ClosingSection /></RecoveryLayout>;
}
