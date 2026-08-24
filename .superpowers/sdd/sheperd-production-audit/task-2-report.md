# Task 2 report: Evidence-workspace UI

## Scope

Owned only `founder-intelligence/`. Backend files were not edited or reverted.

Implemented the UI deltas required by Task 2 on `feat/evidence-grade-insights`:

- Homepage now keeps the latest decision-ready report ahead of incomplete records, labels archived failures explicitly, and exposes persisted readiness metrics for article packets and report sections.
- Source explorer keeps server-side API access and database-backed filter/pagination links, shows the 24-record page size, preserves query filters across pagination, displays canonical URL detail, article insights, original/English summary fields, key points, claims, evidence excerpts/locators, hashes, extraction errors, fulfillment state, and legacy fulfillment absence.
- Report detail keeps the existing route and accordion structure, preserves audit timeline/model/tool/error details, and now labels missing quality snapshots as legacy instead of silently deriving quality from partial records.
- API runtime guards now validate `risk_assessment` and `opportunity_assessment` article insight packets before rendering.

No UI dependencies, static fallback data, client-side API rewrites, or backend contract rewrites were added.

## Verification

Red tests were confirmed before implementation:

- `src/lib/research-api.test.ts` rejected malformed article insight packets only after the parser guard was added.
- `src/app/routes.test.tsx` failed on raw `not_observed` status display, missing pagination page-size text, and missing readiness metrics.
- `src/components/report-accordion.test.tsx` failed on missing legacy quality snapshot labeling.

Final frontend gates:

- `pnpm lint`: pass
- `pnpm typecheck`: pass
- `pnpm test`: pass, 3 files / 20 tests
- `pnpm build`: pass, Next 16.2.10 production build

Command note: every pnpm command printed `Unsupported engine: wanted {"node":"24.x"} (current: {"node":"v26.0.0","pnpm":"9.15.4"})`; the commands still passed.

## Files changed

- `founder-intelligence/src/lib/research-api.ts`
- `founder-intelligence/src/lib/research-api.test.ts`
- `founder-intelligence/src/app/page.tsx`
- `founder-intelligence/src/app/sources/page.tsx`
- `founder-intelligence/src/app/routes.test.tsx`
- `founder-intelligence/src/components/report-accordion.tsx`
- `founder-intelligence/src/components/report-accordion.test.tsx`

## Remaining concerns

- Local shell uses Node v26.0.0 while the frontend declares Node 24.x.
- No live API/browser smoke was requested for Task 2; verification here is static/frontend build and focused rendering tests.

## Round 1 review fixes

Addressed four findings:

- Legacy or missing quality snapshots can no longer display as decision-ready. Report detail now requires canonical `quality.ready`, `quality_ready`, `readiness_status`, complete article counts, and complete report section counts before showing the decision-ready state.
- Homepage readiness metrics no longer infer denominators from source/distillation counts or section ratios. It renders the canonical complete count plus canonical completeness percentage when both fields exist, otherwise `Not recorded in this run`.
- Supported article insights now require `evidence_excerpt` or `evidence_locator` at the runtime API guard. `not_observed` and `uncertain` remain valid without evidence fields.
- Empty source snippets render `Snippet: Not recorded in this run.` instead of a blank paragraph.

Round 1 red tests were confirmed before implementation:

- `pnpm test src/components/report-accordion.test.tsx` failed on legacy decision-ready display.
- `pnpm test src/lib/research-api.test.ts` failed on supported insight without evidence.
- `pnpm test src/app/routes.test.tsx` failed on inferred homepage metrics and empty snippet display.

Round 1 final frontend gates:

- `pnpm lint`: pass
- `pnpm typecheck`: pass
- `pnpm test`: pass, 3 files / 24 tests
- `pnpm build`: pass, Next 16.2.10 production build

Command note remains unchanged: pnpm prints `Unsupported engine: wanted {"node":"24.x"} (current: {"node":"v26.0.0","pnpm":"9.15.4"})`; all commands exited 0.

## Round 2 review fixes

Addressed two findings:

- Homepage selection, report archive rows, and report detail now use one shared fail-closed summary predicate in `founder-intelligence/src/lib/readiness.ts`. A summary or report with `decision_ready=true` or `readiness_status=decision_ready` still renders review/legacy unless canonical article completeness and report-section completeness fields are present and complete.
- Source rows now render `Original: Not recorded in this run.` when an English normalized snippet exists but the original snippet is empty.

Round 2 red tests were confirmed before implementation:

- `pnpm test src/components/report-accordion.test.tsx` failed because a summary with `decision_ready=true` and missing completeness fields still rendered `Decision-ready`.
- `pnpm test src/app/routes.test.tsx` failed because the homepage featured a legacy ready flag and the source row rendered a blank Original line.

Round 2 final frontend gates:

- `pnpm lint`: pass
- `pnpm typecheck`: pass
- `pnpm test`: pass, 3 files / 26 tests
- `pnpm build`: pass, Next 16.2.10 production build

Command note remains unchanged: pnpm prints `Unsupported engine: wanted {"node":"24.x"} (current: {"node":"v26.0.0","pnpm":"9.15.4"})`; all commands exited 0.

## Round 4 review fixes

Addressed four frontend findings:

- Shared readiness remains fail-closed when weekly summaries lack canonical `report_section_completeness`; `report_sections_complete` alone is never enough.
- Report quality messaging now uses the shared readiness predicate, so article/report completeness copy cannot disagree with the review state.
- Readiness normalization now carries canonical `quality.ready`, `quality_ready`, quality readiness status, top-level and quality blocking reasons, and article/report denominator fields through full report payload summaries.
- Article insight statuses are restricted to the backend contract (`supported`, `not_observed`, `uncertain`), blank/placeholder insight text is rejected by the API guard, and source-page blank status/text fields render `Not recorded in this run.` Explicit source extraction and fulfillment states remain visible.

Round 4 red tests were confirmed before implementation:

- `pnpm test -- src/lib/research-api.test.ts` failed while `incomplete` was accepted as an article insight status.
- `pnpm test -- src/app/routes.test.tsx` failed while stale full-payload denominator contradictions still rendered `Latest decision-ready report`.
- `pnpm test -- src/app/routes.test.tsx` failed while a blank insight status rendered an empty status badge.

Round 4 final frontend gates:

- `pnpm lint`: pass
- `pnpm typecheck`: pass
- `pnpm test`: pass, 3 files / 32 tests
- `pnpm build`: pass, Next 16.2.10 production build

Command note remains unchanged: pnpm prints `Unsupported engine: wanted {"node":"24.x"} (current: {"node":"v26.0.0","pnpm":"9.15.4"})`; all commands exited 0.
