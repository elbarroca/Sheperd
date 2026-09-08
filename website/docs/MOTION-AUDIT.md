# Motion audit: September 8, 2026

## Findings and changes

- The invoice-only customer workload, conditional recovery wording and disabled enquiry intake remain unchanged.
- Existing port art is a rendered still with a brief shipping/recovery line animation, not a video.
- Added staggered vertical entrances for headings, supporting text, process steps, responsibility flow and industry items across recovery pages.
- Headings use an 850ms upward mask reveal, with 90ms stagger intervals capped at 270ms. Other content moves upward without opacity changes.
- Content masks out over 300ms only after more than 85% of its section has crossed the upper viewport edge. It resets fully offscreen and reveals again on re-entry. Focused content bypasses animation. Observers track stationary sections, not animated text, to prevent clipping from interrupting its own animation.
- Server HTML starts visible. No JavaScript, missing IntersectionObserver and reduced-motion preferences retain static content. Preference changes are applied immediately; observers are cleaned up on navigation.
- Initial opacity fades failed automated contrast checks during animation. Removed opacity animation rather than masking the failure in tests.

## Video still pending

No video generator is connected and no clip has been generated or added. No account was created, credits purchased or intake enabled.

Runway's official free-plan documentation currently lists 125 one-time credits and watermarks on every free-plan video. Model availability must be checked in the signed-in account:
https://help.runwayml.com/hc/en-us/articles/50404627334547-Free-plan-details

Suggested image-to-video prompt for the existing port artwork:

> Preserve the exact architectural composition, camera and dark negative space above the port. Locked camera. Subtle water movement, slow crane activity and restrained port traffic. No added text, logos, objects or scene transitions. Match the opening and closing frame for a seamless six-second loop. Keep the area behind the website headline still and uncluttered.

Before integration: inspect geometry and loop seam, confirm usage rights and watermark status, encode a small muted WebM/MP4, retain the existing responsive poster, add keyboard-accessible pause, suppress video loading for reduced motion and data saving, and pause offscreen or in a hidden tab. Re-run mobile performance measurements with the actual clip.

## Verification

- `pnpm check`: lint, typecheck and 10 unit tests passed.
- `pnpm exec playwright test`: production build and 75 tests passed across Chromium, Firefox and WebKit, including existing visual baselines and animation re-entry/preference-change coverage. Exit stability is also asserted after the mask animation finishes.
- Captured all six homepage widths and supporting routes at 375/1440px; inspected mobile process and desktop hero screenshots. Existing no-JavaScript, image failure, keyboard, overflow and zoom assertions passed.
- Mobile Lighthouse: performance 97, accessibility 100, best practices 100, SEO 66 (intentional noindex remains). LCP 2.63s, CLS 0, TBT 0ms. Single local lab run, not evidence of conversion improvement.
- Preview: http://127.0.0.1:3211/how-it-works. Nothing deployed.
