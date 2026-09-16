# Claim Ledger

Status: controlling Preview copy gate
Default: suppress unless `render` is explicitly `yes`

## Renderable Preview copy

These entries describe audience context, interface behavior, generic workflow categories, or the source register. They do not establish a company capability, legal conclusion, commercial term, or outcome.

| ID | Exact text or field | State | Evidence | Render |
|---|---|---|---|---|
| UI-001 | `For importer finance and logistics teams` | neutral audience context | Internal ICP hypothesis; no validation claim | yes |
| UI-002A | `Before you assess the charge, reconstruct the record.` | editorial workflow thesis | Strategy recommendation; not a legal conclusion | A/B candidate; not selected |
| UI-002B | `A D&D invoice is one record. The review needs the rest.` | editorial workflow thesis | Strategy recommendation; not a legal conclusion | yes; A/B winner |
| UI-003 | `A practical map of the billing, operational, and governing records that shape a D&D invoice review.` | Preview description | Matches rendered information architecture | yes |
| UI-004 | `See what to gather` | on-page instruction | Anchor behavior | yes |
| UI-005 | `Open official sources` | source-link instruction | Direct links in source register | yes |
| UI-006 | `Billing record` | generic evidence category | FMC guidance and Part 541 context | yes |
| UI-007 | `Operational record` | generic evidence category | FMC guidance lists operational evidence examples | yes |
| UI-008 | `Governing record` | generic evidence category | Current rules and terms are source-linked | yes |
| UI-009 | `Educational Preview. No uploads. No case decision.` | tested boundary | Application behavior plus publication contract | yes |
| UI-010 | `This Preview does not collect files, contact details, or personal information.` | tested application behavior | Must pass form/network/third-party tests | yes after tests |
| UI-011 | Official source title, issuer, checked date, and URL | source metadata | Current internal source register | yes |
| UI-012 | `SheperD` | project label | Company-controlled spelling consistency | yes; no entity suffix |
| UI-013 | `Review the checklist` | on-page instruction | Anchor links to rendered checklist; no intake or creation | yes |
| UI-014 | `For importer finance and logistics teams preparing demurrage and detention evidence for qualified human review.` | audience and page-use context | Matches rendered static checklist and explicit stop | yes |
| UI-015 | `Follow the record, then stop.` | editorial sequence instruction | Matches three rendered records plus qualified-human stop | yes |
| UI-016 | `Official sources only.` | source-register description | Rendered register contains direct FMC and eCFR links only | yes |

## Source-gated candidate claims

The prior candidate rows are not approved for `preview-web`; they have no named approver or approval date. They remain suppressed even where the underlying official source is current.

| ID | Candidate | Current block |
|---|---|---|
| EDU-EVIDENCE-001 | `Reviewing a D&D invoice may require billing facts, operational evidence, governing terms, and current rules.` | exact wording lacks named publication approval |
| EDU-541-001 | `Current 46 CFR Part 541 contains invoice content, issuance timing, and dispute-process requirements.` | exact wording lacks named publication approval |
| EDU-41301-001 | `The three-year period in 46 U.S.C. 41301 is a complaint limitation, not blanket refund eligibility.` | exact wording lacks named publication approval |
| EDU-FMC-001 | `FMC investigations do not represent the complainant and do not guarantee a refund.` | exact wording lacks named publication approval |
| EDU-CASE-001 | `Outcomes depend on the applicable rules, route, deadlines, records, and case facts.` | exact wording lacks named publication approval |

## Prohibited or unresolved public claims

| Scope | Examples | State |
|---|---|---|
| Product capability | portal, automation, AI, integrations, `160+ checks` | mixed or unverified; suppress |
| Service capability | audit, filing, follow-up, recovery support, SLA | company claim or mixed; suppress |
| Commercial | free audit, success fee, pricing, carrier payment mechanics | contract not reviewed; suppress |
| Outcome | recovery, refund, savings, eligibility, compliance, liability | unverified or case-specific; suppress |
| Numbers | `$2.1B`, `$6.2B`, `25%`, `85%`, `$750`, `24 hours` | unverified, misleading, mixed, or contradicted; suppress |
| Proof | customers, logos, quotes, case studies, results | evidence and permission absent; suppress |
| Company | legal entity, founder role, team, address, contact | not independently verified or approved; suppress |
| Security/privacy | encryption, retention, access, compliance, subprocessors | proposed only; suppress |

## Deferred AI and market-opportunity copy

These candidates came from stakeholder feedback and are intentionally not rendered until the claim ledger records named evidence, an approver and an approval date.

| ID | Candidate direction | State |
|---|---|---|
| AI-POSITION-001 | `AI-powered D&D recovery` | gated; capability and workflow evidence required |
| AI-POSITION-002 | `AI-assisted recovery with human review` | superseded by the approved exact wording below; do not render the shorthand outside that row |
| AI-POSITION-003 | `AI helping recover overlooked freight value` | gated; outcome evidence required |

`AI agent`, `AI engine`, autonomous recovery, guaranteed recovery and `recover lost capital directly to your bottom line` remain suppressed. The eventual copy should name the specific assistive step and preserve human review; it must not imply that AI guarantees recovery, replaces review or recovers an entire market.

## Approved AI positioning — 2026-09-16

The CTO feedback and explicit user approval in the current task authorize only
the following exact positioning sentences for `preview-web`. This approval is
for bounded positioning copy with human review; it does not authorize an
autonomous agent, a recovery guarantee, an outcome claim, or adjacent AI copy.

| ID | Exact text | Evidence | Approval | Channel / expiry | Render |
|---|---|---|---|---|---|
| AI-APPROVED-001 | `AI-assisted D&D recovery with human review.` | CTO feedback and explicit user approval in the current task; exact draft in `COPY-DECK.md` | User, explicit approval in the current task, 2026-09-16 | `preview-web`; expires if wording or capability changes | yes |
| AI-APPROVED-002 | `AI helps organize the complex recovery record; human reviewers decide what the evidence supports.` | CTO feedback and explicit user approval in the current task; exact draft in `COPY-DECK.md` | User, explicit approval in the current task, 2026-09-16 | `preview-web`; expires if wording or capability changes | yes |
| AI-APPROVED-003 | `AI-assisted review. Human-led recovery follow-up.` | CTO feedback and explicit user approval in the current task; exact draft in `COPY-DECK.md` | User, explicit approval in the current task, 2026-09-16 | `preview-web`; expires if wording or capability changes | yes |
| AI-APPROVED-004 | `AI supports the process; it does not guarantee recovery or replace human judgment.` | CTO feedback and explicit user approval in the current task; exact draft in `COPY-DECK.md` | User, explicit approval in the current task, 2026-09-16 | `preview-web`; expires if wording or capability changes | yes |

## Approved source-scoped market figure

The homepage market figure is represented by the typed `MarketOpportunity` state.
The user requested the `$13B` highlight on 2026-09-15. Only the exact
source-scoped cost-burden wording below is approved for rendering; `$13B
recoverable by SheperD`, `$13B opportunity` as a recovery claim, and any claim
that the whole figure is recoverable remain suppressed.

| ID | Exact text or field | Evidence | Approval | Render |
|---|---|---|---|---|
| MKT-NAM-001 | `$13B annual cost of port delays to manufacturers` | [The Economic Value of America's Ports](https://nam.org/wp-content/uploads/securepdfs/2026/02/BTW-2026-Web.vF_.pdf), p. 13; checked 2026-09-15 | User-requested source-scoped implementation, 2026-09-15 | yes, exact cost-burden wording only |

## Build rule

Rendered factual sentences must resolve to a typed ledger entry. A missing, expired, unapproved, or unsafe entry removes its dependent block. Production mode fails while any production blocker is unresolved.
