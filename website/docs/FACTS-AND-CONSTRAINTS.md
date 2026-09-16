# SheperD Facts and Constraints

Historical 2026-07-15 checkpoint. For the 2026-09-08 implementation, the user
confirmed invoice-only customer participation, SheperD-managed recovery, $0
upfront and payment on recovered value. Those approved copy decisions supersede
conflicting copy restrictions below. No outcome guarantee or fee percentage was
approved. Intake activation and deployment are not part of this implementation.

Status: controlling clean-room input
Checked: 2026-07-15
Publication state: Preview only; Production blocked

## Recovery checkpoint

- Archive: `/Users/barroca888/Downloads/Dev/Partners/Mikey/SheperD/recovery/sheperd-website-before-clean-room-20260715T092520Z.tar.gz`
- Scope: the prior `website/` tree, excluding reproducible `node_modules/`, `.next/`, and `tsconfig.tsbuildinfo`
- Size: `15,872,568` bytes
- SHA-256: `fdb5b475140fd73cf61566c5cea374c4ae71a4086586833ad24b0e6fa6364f2d`
- Archive list check: passed; `256` entries
- Read check: passed; archived and live `website/PRODUCT.md` both hash to `d0821447ca38463c4748adb7a6326175f7e4902840bf613c6b9c722fcbd047fb`
- Prior port-3000 owner: `next dev` from the prior `website/`; stopped gracefully before archive creation

At the recovery checkpoint, the workspace was already an uncommitted Git repository on branch `feat/open-design-rebuild`, contrary to the prompt's starting snapshot; no remote was observed then. The current repository and remote state is recorded separately in `website/DEPLOYMENT.md`. This rebuild does not claim repository initialization, remote creation, or publication as a completed project checkpoint.

## What is verified

- Company-controlled public materials consistently use the project label `SheperD`. The registered legal entity and publishable brand identity are not verified.
- Current primary government material confirms that D&D review can depend on invoice contents, issuance timing, dispute procedures, operational records, applicable rules, route, deadlines, and case facts.
- Current 46 CFR Part 541 contains D&D invoice-content, issuance-timing, and dispute-process requirements. The rule version applicable to the invoice date still matters.
- 46 U.S.C. 41301 contains a three-year complaint limitation; it is not blanket refund eligibility.
- The FMC's interim Charge Complaint process is enforcement intake. It is not representation of a complainant and does not guarantee a refund.
- The rebuilt Preview can truthfully state its own tested behavior: no forms, uploads, contact capture, analytics, cookies, CRM, or personal-information collection.

## Audience hypothesis, not validated fact

The working primary audience is finance, supply-chain, logistics, operations, AP, and review stakeholders at U.S. importers. This is an internal ICP hypothesis with sample size zero, not a validated market claim. Public copy may use a narrow audience label as neutral navigation context but must not imply customer adoption or validation.

## Company and product claims that remain suppressed

Do not publish or imply any of the following without a new exact claim row, primary evidence, named approval, approval date, channel, and expiry:

- Current service, software, portal, automation, AI, integrations, or `160+ checks`
- Free audit, contingency fee, success fee, pricing, timing, recovery mechanics, or commercial terms
- Recovery eligibility, recovery amount, probability, guarantee, savings, error rate, market size, or refund entitlement
- Customers, logos, testimonials, case studies, invoice counts, disputes, outcomes, or comparative proof
- Legal entity, founder role, team size, office, address, email, phone, or contact destination
- Security, privacy, retention, deletion, encryption, access, compliance, or subprocessor claims
- `25% non-compliant`, `$2.1B unlawfully charged`, `$6.2B recoverable`, `$100B leakage`, `85% avoidable`, `$750 per container`, `24-hour estimate`, or `three years of refunds`

## Preview publication contract

- The site is a noindex, nofollow, noarchive Preview. `noindex` is not access control.
- No form, upload, mail link, contact destination, analytics, tracking, cookie, CRM, or third-party runtime.
- No company capability section, product UI, fake dashboard, roadmap promise, customer scene, or outcome imagery.
- The approved AI positioning exception is limited to the exact AI-APPROVED-001 through AI-APPROVED-004 rows in `CLAIM-LEDGER.md`; all other AI capability, agent, engine, autonomous, guarantee, and outcome language remains suppressed.
- Source-gated regulatory explanations may render only after the exact text is independently approved for `preview-web`. Current candidate claim rows have no approver and therefore must remain suppressed.
- Neutral UI copy may identify the audience, explain that invoice review starts with records, describe generic evidence categories, state Preview behavior, and point to current official sources. It must not make a company, legal, commercial, or outcome claim.
- Privacy and Terms routes are Preview notices only, not approved production policies.
- Production builds must fail closed while any blocker below remains unresolved.

## Production blockers

1. Verified legal entity, authority, brand assets, footer identity, and contact owner.
2. Approved company positioning and demonstrated current service/product wording.
3. Exact claim evidence, named domain/legal approvers, channel scope, dates, and expiry.
4. Approved privacy notice and terms.
5. Approved intake, consent, storage, access, retention, deletion, incident, and subprocessor controls.
6. Approved commercial model, fees, timing, recovery definition, and customer authority.
7. Approved contact/CTA destination and response owner.
8. Permissioned customer proof or an explicit decision to launch without it.
9. Canonical production origin, indexing, metadata, analytics, structured-data, and deployment authority.
10. Explicit authority to publish, deploy, attach a domain, or mutate a live site.

## Official source register

| Source | Issuer | Checked | Direct URL | Use boundary |
|---|---|---|---|---|
| 46 CFR Part 541 | eCFR | 2026-07-15 | https://www.ecfr.gov/current/title-46/chapter-IV/subchapter-B/part-541 | Current rule context; case-specific conclusions require review |
| 46 U.S.C. 41301 | U.S. Code | 2026-07-15 | https://www.govinfo.gov/link/uscode/46/41301?link-type=html&year=mostrecent | Complaint limitation, not blanket refund eligibility |
| 46 U.S.C. 41310 | U.S. House OLRC | 2026-07-15 | https://uscode.house.gov/view.xhtml?edition=prelim&num=0&req=granuleid%3AUSC-prelim-title46-section41310 | Charge-complaint authority; route remains case-specific |
| Charge Complaint interim guidance | Federal Maritime Commission | 2026-07-15 | https://www.fmc.gov/ocean-shipping-reform-act-of-2022-implementation/guidance-on-charge-complaint-interim-procedure/ | Interim procedure; not representation or a refund guarantee |
| Complaints and assistance | Federal Maritime Commission | 2026-07-15 | https://www.fmc.gov/complaints-and-assistance/ | Route overview; not SheperD endorsement |

## Internal controlling evidence

- `01_Company/Claims and Evidence Register.md`
- `01_Company/Company Brief.md`
- `01_Company/Product and Business Model.md`
- `03_GTM/ICP and Stakeholder Personas.md`
- `03_GTM/Website and Content Audit.md`
- `04_Operations/Customer Data Intake and Security.md`
- `05_AI/Human Approval Policy.md`
- `10_Sources/Source - 46 CFR Part 541.md`
- `10_Sources/Source - 46 USC 41301.md`
- `10_Sources/Source - 46 USC 41310 and FMC Complaint Routes - 2026-07-15.md`
- `10_Sources/Source - FMC Charge Complaint Guidance.md`

Inference, internal proposals, company statements, and dated observations do not become public facts by appearing in these files.
