# Invoice-only recovery site

Approved direction: 2026-09-15; AI positioning approval: 2026-09-16. This
document supersedes older visual/copy directions for this implementation; it
does not activate intake or publication.

## Copy deck and wireframe mapping

| Homepage section | Approved copy | PDF sections |
| --- | --- | --- |
| Hero | SheperD. A clear path from invoice to recovery. You send the invoices. We handle the recovery. | 01 |
| AI positioning | AI-assisted D&D recovery with human review. AI helps organize the complex recovery record; human reviewers decide what the evidence supports. | 01, 09, 11 |
| CFO | You send the invoices. We handle the recovery. SheperD manages review, recovery follow-up, and outcome tracking. | 09, 11 |
| Process | A clear path. An entirely managed process. Send invoices. We review. We pursue recovery. Refund or carrier credit. | 03, 11 |
| Market opportunity | Paid charges can hold a second opportunity. SheperD brings the invoice and shipping history together, then reviews the record for potential recovery. | 02, 04, 06, 10 |
| Economics | $0 upfront. We get paid when you recover value. | 07 |
| Importer fit / FAQ | Built for importers. Invoice-only participation; fees, records, outcomes and timing explained. | 08, supporting page 02 |
| Closing | Find recoverable value in your shipping history. You send the invoices. We handle the recovery. | 12 |

Supporting routes: /how-it-works, /for-importers, /about. The homepage includes a
Calendly contact section after the importer FAQ; legacy /contact and /pilot URLs
redirect there. No upload, delivery activation, CRM, analytics or deploy.

Customer responsibility: send invoices. SheperD responsibility: supporting-record
work, review, recovery follow-up, outcome tracking. No customer evidence-gathering
or dispute-management task is introduced. Refunds and credits remain distinct.

$0 upfront and payment on recovered value were confirmed by the user. No fee
percentage, fixed timing, recovery guarantee or three-year eligibility claim.

## Art direction

Generated port artwork and glass-green icon sheets are documented in
`ASSET-PROVENANCE.md`. Local PNG derivatives are used; no runtime third-party
asset service is required. The process and importer families use minimal
frosted green forms on transparent backgrounds, not cartoon or glossy dashboard artwork.

The hero uses the earlier terminal artwork as a static composition with no
decorative story, caption or replay control.
The process section is a single semantic timeline with PNG illustrations.
Mobile, reduced motion and no-JavaScript views retain the full static
explanation. The approved AI positioning is limited to the exact rows recorded
in `CLAIM-LEDGER.md`; agent, engine, autonomous, guarantee and bottom-line
outcome language remains suppressed. The homepage renders `$13B` only with the
source-scoped annual port-delay-cost meaning recorded in `CLAIM-LEDGER.md`.

## Baseline

The implementation remains on the dedicated branch `feat/invoice-only-recovery-site`;
unrelated research changes remain untouched. Browser assertions for the older
headline, audit form and dashboard were replaced. Final command results are
recorded in `RECOVERY-VERIFICATION.md`.
