# Founder Intelligence Design System

## Design intent

A private founder control room, not a public marketing site. The supplied SheperD reference establishes the visual language: near-black navy, electric-blue signal, crisp white analytical surfaces, compact navigation, and connected decision modules.

The product preserves that energy while prioritizing auditability and dense research navigation.

## Design read

- Variance: 5/10
- Motion: 4/10
- Density: 7/10
- Primary accent: electric blue
- Core rhythm: dark control header and hero, then light evidence workspace

## Information hierarchy

Every primary view follows this order:

1. Page purpose and current boundary.
2. Decision-critical summary.
3. Flow, map, chart, or evidence visualization.
4. Supporting detail and source traceability.

Navigation uses founder tasks: Brief, Decision map, Operating plan, Evidence library, and Ricardo notes.

## Visual language

- Near-black navy anchors navigation, identity, and decision posture.
- Electric blue communicates interaction, retrieval, and informational connection.
- Cool paper separates the private workspace from white evidence surfaces.
- Red means blocked or unsafe.
- Green means permitted inside the current boundary.
- Amber means a decision or approval is required.
- Panels use a 14px radius, controls use an 8px radius, and status labels may use pills.
- Fine borders carry structure; restrained shadows lift only major analytical surfaces.
- The interface uses one dark-to-light theme rhythm rather than independent themed sections.

## Typography

- Product copy uses the native Avenir Next stack with Segoe UI and Arial fallbacks.
- Page titles are large, sentence case, and tightly tracked to echo the supplied reference without using all caps.
- Body copy is at least 16px in decision-critical areas.
- Metadata remains legible and passes contrast requirements.
- Monospace is reserved for IDs, source paths, and numeric indices.

## Source library

- The catalog lists all 88 admitted files, including the two template files with no indexable section body.
- File metadata loads with the page; full section text loads only after selection.
- Folder, layer, text, tag, and evidence-state filtering never mutates source data.
- Empty, loading, malformed-response, network-error, and copy-failure states are explicit.
- The selected file exposes its full repository path, indexed word count, section count, evidence-state count, and every retrievable section.

## Visualization rules

- Decision readiness uses a radar chart backed by four exact score values.
- Corpus shape compares file coverage and section depth by knowledge layer.
- Evidence state uses a donut chart backed by direct source-ledger counts.
- Every chart has an accessible exact-data disclosure.
- Decision flow is a semantic ordered list.
- Blocker and ownership maps remain meaningful as nested lists without connector lines.
- Planning scores use native meters plus named bands and a method disclosure.
- Priority matrix is supplementary; the accessible ranked list carries the same decision.

## Interaction and accessibility

- All primary interactive targets are at least 42px tall, with 44px preferred.
- Focus states use a visible 3px blue outline.
- Active mobile navigation scrolls inside its own rail and never shifts the document.
- Motion respects `prefers-reduced-motion`; chart animation is disabled for reduced-motion users.
- Semantic meaning does not depend on color alone.
- Full source paths remain selectable and copyable.

## Responsive behavior

- Wide screens use a compact sticky top control bar and a centered 1260px workspace.
- Tablet screens preserve the top bar while reducing icon and label density.
- Small screens use a two-row header with a horizontally scrollable task rail that centers the active view.
- Charts, maps, score cards, analysis rows, and search results collapse to one column.
- The source catalog becomes a bounded file list followed by the full source reader.
- Dense tables remain horizontally scrollable inside a labeled focusable region.
