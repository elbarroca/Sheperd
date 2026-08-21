# SheperD Premium Landing Page Specification

Status: visual direction and copy architecture for mockup generation; not implementation code.

## Core job

In five seconds, an importer finance or logistics lead should understand:

> SheperD helps them turn one D&D invoice into a clear, evidence-led review path.

The page must move the visitor through one story:

`isolated charge → surrounding records → visible timeline → evidence gap → review packet`

The experience is an educational Preview. It must not imply uploads, automated recovery, legal conclusions, customer outcomes, or a verified SheperD service capability that is not documented.

## Message hierarchy

- Audience: `For importer finance + logistics teams`
- Memorable idea: `The record before the claim.`
- Hero thesis: `The invoice tells you what was billed. The record tells you what happened.`
- Explanation: `A D&D invoice is one record. The review needs the rest.`
- Primary CTA: `See what to gather`
- Secondary CTA: `Explore the method`
- Trust boundary: `Educational Preview · No uploads · No case decision`

## Page architecture

### 1. Header: establish authority

Purpose: make the site feel like a considered financial-infrastructure product before the visitor reads the hero.

Components:

- SheperD lion and wordmark at the left.
- Four quiet links: `Method`, `What to gather`, `Sources`, `Limits`.
- One primary button: `See what to gather`.
- No hamburger-style overflow, announcement bar, fake trust logos, or secondary CTA clutter.

### 2. Hero: name the tension, then show the mechanism

Purpose: communicate the problem and the answer within one viewport.

Recommended copy:

- Eyebrow: `FOR IMPORTER FINANCE + LOGISTICS TEAMS`
- Kicker: `THE RECORD BEFORE THE CLAIM`
- H1: `The invoice tells you what was billed. The record tells you what happened.`
- Body: `A D&D invoice is one record. The review needs the rest.`
- Supporting line: `Bring the billing record, the operational timeline, and the governing terms into one clearer starting point.`

Visual component: a single contained `Review field`, not a collage. One illustrative invoice sits at the origin. Three labeled rails leave it:

1. Billing — invoice, bill of lading, payment state, charge dates.
2. Operations — availability, pickup, return, terminal timing, communications.
3. Governing — free-time terms, tariff or contract language, route, rule version.

The rails converge into a quiet `Review packet` destination. The visual must explain the product idea without relying on tiny labels.

### 3. Stakes section: explain why context matters

Purpose: replace generic problem copy with a concrete operational truth.

Headline: `A charge is easy to name. Harder to explain.`

Copy: `The number is usually visible. The dates, events, hand-offs, and terms around it are what make the next question clearer.`

Component: one wide blue-tinted container with three stacked evidence bands. Each band expands on hover in the real build; the mockup shows one expanded state only. Do not use three equal marketing cards.

### 4. Story module: one charge, three records

Purpose: teach the mental model.

Headline: `One charge. Three records.`

Layout: a large left narrative column and one connected right-side record map. The map should read vertically, like a case file being assembled.

Record copy:

- Billing record: `What was billed, by whom, for which dates, and against which terms.`
- Operational record: `What happened at the terminal, in the appointment trail, and in the communications around it.`
- Governing record: `Which free-time terms, tariff or contract language, route, and source date belong beside the record.`

### 5. Method: make the sequence obvious

Purpose: answer “how does this work?” without claiming an automated product workflow.

Headline: `Build the record before framing the question.`

Use five chapters with one active detail panel:

1. `Anchor the charge` — confirm invoice, amount, period, and references.
2. `Reconstruct the timeline` — place operational events and communications in order.
3. `Locate the terms` — match tariff, contract, route, and effective dates.
4. `Mark the gaps` — make missing evidence visible instead of filling it with assumptions.
5. `Take the packet to qualified human review` — carry a clearer record into the next conversation.

The production interaction should let the active chapter update the detail panel. The mockup should show the first chapter active and the other four visible as a calm progress spine.

### 6. Product proof: the review packet

Purpose: provide the strongest proof of usefulness without inventing outcomes.

Headline: `A better packet starts with a visible gap.`

Component: one large, bordered packet surface with six evidence rows. Use row separators, not six separate cards. Include:

- Invoice + bill of lading
- Payment record
- Free-time, tariff, or contract terms
- Availability, pickup, return, and terminal timing
- Appointment, hold, closure, and communication records
- One highlighted gap state: `Select any missing category`

Every row has four quiet columns: `Evidence category`, `Why it matters`, `Source / date`, `Status`. The visual should show two added rows, three not-added rows, and one gap. This is more credible than a completed-success state.

Note below the surface: `Missing a category? Mark the gap. Do not fill it with an assumption.`

### 7. Audience module: make it personal

Purpose: show each buyer why this matters without adding unsupported product claims.

Use three horizontal role moments, not feature cards:

- Finance: `See which records belong beside the charge before the variance becomes a conclusion.`
- Operations: `Put terminal events, holds, appointments, and hand-offs in one timeline.`
- AP: `Carry the invoice, payment state, and source references into a cleaner review packet.`

Keep this section compact. The page already explains the mechanism; this section only helps the visitor self-identify.

### 8. Limits and sources: earn trust

Purpose: convert restraint into credibility.

Use two large sibling containers:

- `Where this Preview stops.` — `It does not accept invoices or shipment files, determine compliance or liability, make a recovery decision, or provide legal advice.`
- `Check the current source.` — show source title, issuer, checked date, and an `Open official sources` action.

Avoid legal-looking seals, compliance badges, or claims of official endorsement.

### 9. Closing CTA: give the page a complete ending

Headline: `Start with the record. Stop at the evidence gap.`

Supporting line: `See the categories, sequence, and sources worth bringing into the next review.`

CTA: `See what to gather`

Footer line: `SheperD · Preview only · No information is collected`

## Component system

### Container grammar

- Max content width: 1,280px.
- Section rhythm: 112px desktop / 72px tablet / 48px mobile.
- Use three surface levels only: canvas, narrative container, evidence surface.
- Containers are rectangular with 14–20px radius; pills are reserved for status and metadata.
- One major container per section; no card-inside-card nesting.
- Use borders and spacing first; use shadows only on the invoice and packet surfaces.

### Type

- Display: an elegant high-contrast serif with compact line-height.
- UI/body: one neutral grotesk with strong tabular numerals.
- H1: 72–88px desktop, max 8 words per line where possible.
- Section headings: 40–56px.
- Body: 16–18px, max 62 characters per line.
- Labels: 11–12px uppercase with generous tracking.

### Palette: production blue theme

- Ink: `#071B3A`
- Navy surface: `#0A2144`
- Cobalt action: `#1557D6`
- Azure signal: `#3F82F7`
- Ice surface: `#EDF4FF`
- Canvas: `#FBFCFE`
- Rule: `#C9D7EC`
- Slate text: `#53647D`
- Gap marker: `#C48A2A`

Blue is structural: it owns the story rail, primary CTA, active state, and selected packet row. It must not become decoration scattered across every icon.

### Motion direction

- As the hero enters, the three evidence rails draw from the invoice to the packet.
- The method spine advances one chapter at a time on scroll.
- The packet rows reveal source/date/status progressively.
- The gap marker remains still and visible; it is the honesty signal.
- No parallax photos, bouncy cards, cursor-following effects, or gratuitous 3D.

## Quality gates for the next mockup

- The headline is understandable without reading the nav.
- The first visual explains invoice → records → packet without a legend.
- Each section has one job and advances the story.
- No section is a generic feature grid.
- No unsupported recovery, automation, customer, ROI, or legal claim appears.
- Blue defines hierarchy; it does not become neon decoration.
- The page feels like one designed system, not nine unrelated screens.
- The checklist shows a visible gap rather than a fake success state.
- Copy addresses finance, operations, and AP with concrete nouns.
- Every CTA has one clear next action.
