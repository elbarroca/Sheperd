# Motion audit: September 15, 2026

## Current implementation

- The invoice-only customer workload, conditional recovery wording and disabled enquiry intake remain unchanged.
- The hero uses the approved static maritime terminal composition with no decorative story, caption or replay control. The commercial copy and CTA remain visible in the first view.
- The homepage process section is now one semantic four-step timeline. It keeps the PNG illustrations and removes the duplicate sticky visual/list panel. `/how-it-works` keeps the same timeline with the fuller step descriptions.
- The hero remains a bounded static layout at every width. Reduced motion leaves the same composition visible. No scroll event listener, video asset or GSAP dependency is used.
- Server HTML starts visible. No JavaScript and missing `IntersectionObserver` retain the static hero and process content. Focused content bypasses entrance animation. Existing section entrance transitions still reset after the section leaves the viewport.

## Visual direction

- The hero uses the earlier maritime terminal still with a restrained charcoal overlay and sea-green interface accents. The generated blue-hour still remains available to supporting routes.
- Process and importer artwork uses one local glass-green PNG family: minimal frosted forms on transparent backgrounds for the white surfaces, with no readable text, logos, customer data or fake metrics.
- The visual direction is premium and industrial rather than cartoon, glossy 3D, or copied Apple trade dress.

## Claims constraints

- Candidate AI positioning remains in the claim ledger only. No AI agent, AI engine, autonomous recovery, guaranteed recovery or bottom-line outcome claim is rendered.
- The market opportunity section renders `$13B` only as the NAM-sourced annual cost of port delays to manufacturers. It is not presented as a SheperD recovery guarantee or as a claim that the entire figure is recoverable.
- The hero artwork is illustrative only. It is not presented as proof of container pickup or recovery performance.

## Verification record

- Unit coverage includes suppressed and approved market-figure states.
- Browser coverage includes static hero visibility, reduced motion, no-JavaScript content, image failure, forced colors, keyboard access, responsive opportunity layout, 320px/375px/768px/1024px/1440px/1920px overflow checks and 200% zoom.
- No hero video or video-generation account request is part of this implementation.
