# Institutional Holdings Content-First UI V1 Runs

## 2026-08-17 — Design Audit

- Read product direction, roadmap, project map, Institutional Holdings flow and prior context-first
  design records.
- Traced React manager event, Streamlit session state and manager normalization code.
- Inspected actual Institutional Holdings UI and active left-line CSS.
- Presented three visual layout directions in the local brainstorming companion.
- User selected A `Content-first hybrid` and approved the detailed interaction contract.

## 2026-08-17 — Implementation Planning

- User reviewed and approved the written design spec.
- Mapped current Streamlit event, React shell/workbench, state helpers, CSS, focused source/runtime
  tests and production Vite build ownership.
- Wrote a four-task TDD implementation plan with per-task interfaces, commands, expected failures,
  commits and actual Browser QA criteria.

## 2026-08-17 — Implementation And Verification

- Baseline: Python 63 passed / 4 subtests, Vitest 10 passed, TypeScript typecheck passed.
- Added two failing manager-selection regressions, observed both failures, then fixed successful
  search reset and load-failure body preservation. Focused tests passed; full Python became 65 passed.
- Replaced rail/drawer source contracts with failing content-first shell and bounded-picker contracts,
  then rewrote shell, manager/data controls, horizontal tabs, local pending/error feedback and next check.
- Removed manager drag helpers/tests, ran Vitest 8 passed, TypeScript typecheck passed and rebuilt the
  tracked Vite production bundle.
- Actual Browser QA on `localhost:8511`: Bill Ackman → David Tepper → Warren Buffett all changed the
  selected manager; `.stMain` scrollTop stayed 0 after the final fix; quarter-review selection used
  subtle tint + short underline; 390px stacked controls and horizontal tabs rendered without drawer.
- Browser console warnings/errors: 0. Final screenshot:
  `institutional-holdings-content-first-ui-v1-qa.png` (generated, not committed).
