# Invoice-only recovery site

Approved direction: 2026-09-08. This document supersedes older visual/copy
directions for this implementation; it does not activate intake or publication.

## Copy deck and wireframe mapping

| Homepage section | Approved copy | PDF sections |
| --- | --- | --- |
| Hero | SheperD. Turn historical shipping charges into money back. Send your invoices. We handle the rest. | 01 |
| CFO | You send the invoices. We handle the recovery. SheperD manages review, recovery follow-up, and outcome tracking. | 09, 11 |
| Process | Send invoices. We review. We pursue recovery. Refund or carrier credit. | 03, 11 |
| Missed value | Paid doesn't have to mean forgotten. We review historical detention and demurrage charges for potential recovery. | 02, 04, 06, 10 |
| Economics | $0 upfront. We get paid when you recover value. | 07 |
| Importer fit / FAQ | Built for importers. Invoice-only participation; fees, records, outcomes and timing explained. | 08, supporting page 02 |
| Closing | Find recoverable value in your shipping history. You send the invoices. We handle the recovery. | 12 |

Supporting routes: /how-it-works, /for-importers, /about. Existing /pilot remains
the enquiry destination. No upload, delivery activation, CRM, analytics or deploy.

Customer responsibility: send invoices. SheperD responsibility: supporting-record
work, review, recovery follow-up, outcome tracking. No customer evidence-gathering
or dispute-management task is introduced. Refunds and credits remain distinct.

$0 upfront and payment on recovered value were confirmed by the user. No fee
percentage, fixed timing, recovery guarantee or three-year eligibility claim.

## Art direction

Generated port artwork: OpenAI image generation, 2026-09-08. Conceptual 3D render,
not a customer site or recovery result. Original retained in Codex generated images.
Responsive WebP assets are local. HTML invoice and value diagrams contain no
fabricated financial figures. Neutral charcoal, white, blue and recovery green.

Asset originals retained under the Codex generated-images directory for this
task: `exec-e644b7aa-3c0a-4bd9-88a6-6f3138b52c03.png` (port),
`exec-b75cfc4e-931d-426d-9c3b-c94e0670c5e8.png` (process objects),
`exec-a10d50cb-2570-4a16-8d4c-29c2c9788e68.png` (industry objects).
The asset sheets were cropped into individual WebP files with Sharp. No runtime
third-party asset service is required. Final results: `RECOVERY-VERIFICATION.md`.

Forward freight / reverse recovery motion runs once, settles, and can be replayed.
Reduced motion and no-JavaScript views retain the entire static explanation.

## Baseline

Website source was clean on codex/production-api-query-fix; unrelated research
changes remain untouched. Dedicated branch: feat/invoice-only-recovery-site.
Existing browser tests reference an older headline, audit form and dashboard;
these assertions need replacement. Baseline and final command results are recorded
in the delivery report after verification.
