# Founder Intelligence Design System

## Design intent

A private founder decision cockpit, not a marketing site. The interface should feel trustworthy, operational, compact, and easy to audit.

## Information hierarchy

Every primary view follows this order:

1. Page purpose and current boundary.
2. Decision-critical summary.
3. Flow, map, or evidence visualization.
4. Supporting detail and source traceability.

Navigation uses founder tasks: Brief, Decision map, Operating plan, Evidence, and Analysis.

## Visual language

- Harbor navy anchors navigation and identity.
- Cool paper separates the private workspace from white evidence surfaces.
- Red means blocked or unsafe.
- Green means permitted inside the current boundary.
- Amber means a decision or approval is required.
- Blue means interactive or informational.
- Panels use an 8px radius, controls use a 6px radius, and status labels may use pills.
- Borders carry structure. Shadows are not used.

## Typography

- Product copy uses a system sans-serif stack.
- Page titles use sentence case and scale from 34px on small screens to 56px on wide screens.
- Body copy is at least 16px.
- Metadata is at least 12px and must pass contrast requirements.
- Monospace is reserved for IDs, source paths, and numeric indices.

## Visualization rules

- Decision flow is a semantic ordered list.
- Blocker and ownership maps remain meaningful as nested lists without connector lines.
- Planning scores use native meters plus named bands and a method disclosure.
- Evidence mix always exposes direct count and percentage labels.
- Priority matrix is supplementary; the accessible ranked list carries the same decision.
- Timelines use ordered lists, not generic table roles.

## Interaction and accessibility

- All interactive targets are at least 44px tall where practical.
- Focus states use a visible 3px blue outline.
- Research exposes loading, empty, malformed-response, network-error, and stale-request behavior.
- Details and summaries preserve full source paths without overwhelming the initial scan.
- Motion respects `prefers-reduced-motion`.
- Semantic meaning does not depend on color alone.
- Mobile navigation wraps into a visible grid and the external hold remains persistent.

## Responsive behavior

- Wide screens use a fixed 248px task navigation rail.
- Tablet screens move the navigation above the content without horizontal scrolling.
- Small screens use one-column flows, maps, score cards, analysis rows, and search results.
- Dense tables remain horizontally scrollable inside a labeled focusable region.
