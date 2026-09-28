# Design QA

- Source reference: `/var/folders/41/_dw_pjd939j0k29gkmp2rlbw0000gn/T/codex-clipboard-b00f6f90-50bd-4b59-a913-07f2158f2710.png`
- Implemented desktop capture: `/tmp/sheperd-qa-prod-section-1440.png`
- Implemented mobile capture: `/tmp/sheperd-qa-prod-section-375.png`
- Comparison capture: `/tmp/sheperd-qa-opportunity-comparison.png`
- Viewports checked: 1440 × 1000 and 375 × 900, plus visual baselines at 320, 375, 768, 1024, 1440 and 1920px.
- Focus: opportunity-map composition, responsive reflow, transparent PNG compositing, overflow, and claim-safe fallback.
- Result: the selected composition is implemented for desktop and mobile. The map is a real RGBA PNG over the off-white surface. The literal market figure remains suppressed until its meaning, source, checked date and approval are recorded.
- final result: passed
