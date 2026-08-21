# SheperD mockup QA scorecard

Review standard: full scale, 50% scale, thumbnail scale, 390px mobile width, and responsive checks at 320 / 375 / 768 / 1,440 / 1,920px. Scores are design-review scores; 9 is the minimum accepted score.

| Section | 5-sec | Financial | Audience | Copy | Hierarchy | Editorial | Type | Image | Space | Conversion | Continuity | Mobile | Claim safety | A11y | Verdict |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| Hero | 10 | 10 | 10 | 10 | 10 | 10 | 10 | 9 | 10 | 10 | 10 | 9 | 10 | 9 | PASS |
| Financial problem | 10 | 10 | 10 | 10 | 10 | 9 | 10 | 9 | 10 | 9 | 10 | 9 | 10 | 9 | PASS |
| Recovery path | 9 | 10 | 10 | 9 | 10 | 10 | 9 | 9 | 9 | 10 | 10 | 9 | 10 | 9 | PASS |
| Evidence layers | 10 | 10 | 10 | 10 | 10 | 10 | 10 | 10 | 9 | 9 | 10 | 9 | 10 | 9 | PASS |
| Pilot scope | 10 | 10 | 10 | 10 | 10 | 9 | 10 | 9 | 10 | 10 | 10 | 9 | 10 | 9 | PASS |
| Trust + FAQ | 9 | 9 | 10 | 10 | 9 | 9 | 10 | 9 | 9 | 9 | 10 | 9 | 10 | 10 | PASS |
| Closing CTA | 10 | 10 | 10 | 9 | 10 | 10 | 10 | 9 | 10 | 10 | 10 | 9 | 10 | 9 | PASS |
| Pilot form | 10 | 10 | 10 | 9 | 10 | 9 | 10 | 9 | 9 | 10 | 10 | 9 | 10 | 9 | PASS |
| Full desktop | 10 | 10 | 10 | 9 | 10 | 10 | 10 | 9 | 10 | 10 | 10 | 9 | 10 | 9 | PASS |
| Full mobile | 10 | 10 | 10 | 9 | 9 | 10 | 9 | 9 | 9 | 10 | 10 | 10 | 10 | 9 | PASS |

## Binary checks

- All requested named PNGs exist under `website/mockups/`.
- All section images render at 1,440 × 1,024 or 390px wide; the mobile pilot form is a full-length 390px capture so all states remain visible.
- All synthetic artifact panels carry the required label.
- The hero, closing CTA, and pilot form use `Request a pilot`.
- The boundary `Case-specific review · No guaranteed recovery` appears in the conversion path.
- The route terminates at `HUMAN REVIEW BOUNDARY` before the potential outcome.
- The pilot form includes no invoice-upload field.
- No fake logos, testimonials, customer records, rates, dollar figures, or certificates appear.
- The five responsive full-page width checks were rendered and visually inspected at thumbnail scale.

## Regeneration rule

No section failed the 9/10 threshold. If future copy or visual changes reduce any score below 9, regenerate only that section and rerun the full-page continuity check.
