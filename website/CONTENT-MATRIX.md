# SheperD Website Content Matrix

Status: Preview-safe; Production blocked
Checked: 2026-07-15

## Publication rule

Every public sentence is one of:

1. neutral interface copy that makes no company, product, commercial, legal, or outcome claim;
2. mechanically tested Preview behavior;
3. official-source metadata with a direct link; or
4. an exact approved registry claim.

When an item does not fit one of those categories, it is suppressed. No candidate registry claim is currently approved for either public channel.

## Rendered homepage matrix

| Surface | Rendered content class | Authority | Source module | Preview | Production |
|---|---|---|---|---|---|
| Wordmark | Project label | Preview project identity only | `site.ts` | Render | Requires approved brand/entity |
| Audience line | Neutral audience marker | UI-neutral | `site.ts` | Render | Requires content approval |
| Hero H1 | Interaction framing | UI-neutral | `site.ts` | Render | Requires content approval |
| Hero support | Description of the Preview structure | UI-neutral, no SheperD capability | `site.ts` | Render | Replace only with approved positioning |
| Primary CTA | Same-page navigation | Tested application behavior | `site.ts` | `#review-requirements` | Contact destination blocked |
| Manifest | Review questions | UI-neutral | `site.ts` | Render | Render only within approved story |
| Requirements | Generic checklist prompts | UI-neutral | `site.ts` | Render | Exact educational claims require approval |
| Process | Conditional human review prompts | UI-neutral, not a SheperD workflow | `site.ts` | Render | Capability wording blocked |
| FAQ | Preview mechanics and suppression reason | Tested behavior or UI-neutral | `site.ts` | Render | Replace with approved product FAQ |
| Limits | No-decision, no-collection, and suppression notices | Tested behavior or Preview boundary | `site.ts` | Render | Production notices blocked |
| Sources | Title, issuer, checked date, HTTPS URL, final FMC action | Official source metadata | `sources.ts` | Render last | Recheck freshness and approve context |
| Footer | Preview mechanics | Tested behavior | `site.ts` | Render | Entity/contact fields blocked |

## Legal-route matrix

| Route | Rendered status | What it states | Production treatment |
|---|---|---|---|
| `/privacy` | `Preview Data Notice` | No application form, upload, account, analytics, ad pixel, cookie, or contact capture; hosting may process delivery/security request data | Must be replaced by approved privacy notice |
| `/terms` | `Preview Use Notice` | Design review purpose, no case reliance, and explicit production gate | Must be replaced by approved terms |
| 404 | Preview route notice | Requested page is outside the current review set | Keep noindex |

These routes never claim to be counsel-approved policies.

## Official source matrix

| ID | Issuer | Title | Checked | Direct URL | Runtime use |
|---|---|---|---|---|---|
| `SRC-002` | Electronic Code of Federal Regulations | 46 CFR Part 541 | 2026-07-15 | `https://www.ecfr.gov/current/title-46/chapter-IV/subchapter-B/part-541` | Link metadata only |
| `SRC-003` | U.S. House Office of the Law Revision Counsel | 46 U.S.C. 41301 | 2026-07-15 | `https://uscode.house.gov/view.xhtml?edition=prelim&num=0&req=granuleid%3AUSC-prelim-title46-section41301` | Link metadata only |
| `SRC-008` | Federal Maritime Commission | Guidance on Charge Complaint Interim Procedure | 2026-07-15 | `https://www.fmc.gov/ocean-shipping-reform-act-of-2022-implementation/guidance-on-charge-complaint-interim-procedure/` | Link metadata only |

The Preview does not interpret or quote these sources. Links are not presented as endorsement.

## Suppressed claim registry

| Claim ID | Evidence state | Expires | Missing publication fields | Preview | Production |
|---|---|---|---|---|---|
| `EDU-EVIDENCE-001` | educational-primary-source | 2026-08-14 | channel, approver, approval date | Suppress | Suppress |
| `EDU-541-001` | educational-primary-source | 2026-08-14 | channel, approver, approval date | Suppress | Suppress |
| `EDU-41301-001` | educational-primary-source | 2026-08-14 | channel, approver, approval date | Suppress | Suppress |
| `EDU-FMC-001` | educational-primary-source | 2026-08-14 | channel, approver, approval date | Suppress | Suppress |
| `EDU-CASE-001` | educational-primary-source | 2026-08-14 | channel, approver, approval date | Suppress | Suppress |

The exact candidate sentences live only in `src/content/claims.ts`. Components do not duplicate them.

## Production blocker matrix

| ID | Required approval or authority | Current Preview treatment |
|---|---|---|
| `EXT-01` | Legal entity and publication authority | Omit entity fields |
| `EXT-02` | Approved privacy notice | Preview notice only |
| `EXT-03` | Approved terms | Preview notice only |
| `EXT-04` | Approved contact and CTA destination | Same-page action only |
| `EXT-05` | Approved product/service wording | Suppress |
| `EXT-06` | Approved commercial wording | Suppress |
| `EXT-07` | Approved data intake and security controls | No intake |
| `EXT-08` | Named reviewer and exact claim approvals | Suppress claim blocks |
| `EXT-09` | Approved canonical production origin | No canonical or `og:url` |
| `EXT-10` | Approved production metadata | Mechanical Preview metadata only |
| `EXT-11` | Approved brand assets | Temporary Preview-only icons |
| `EXT-12` | Vercel project/protection/promotion authority | Local verification only until authenticated |

Production validation reports blocker and claim IDs without printing candidate or sensitive content.
