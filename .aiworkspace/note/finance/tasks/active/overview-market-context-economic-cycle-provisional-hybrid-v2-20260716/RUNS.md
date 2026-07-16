# Economic Cycle Provisional Hybrid V2 Runs

Last Updated: 2026-07-16

- Existing V1 design, plan, status, code ownership, pipeline, service, React component, tests, and actual handoff state inspected.
- TDD RED confirmed LIMITED probabilities were removed, service hid them, and the source still required a circular clock.
- Pipeline/results/service focused verification: 18 passed, then missing-phase regression included in the focused suite.
- React production build passed and Market Context economic-cycle/valuation regression passed 43 tests.
- Existing 122 snapshot/artifact pairs were rematerialized with one primed PIT panel: 336/366 horizon estimates available, all publication statuses still LIMITED.
- DB-backed read model: history 121, recent path 18, three current horizon distributions sum to 1.0.
- Browser QA: desktop and 420px screenshots captured; custom Chromium checks verified visible provisional cards/quadrant/paths, 123 ribbon cells, zero console/page errors, and mobile overflow <= 1px.
- Final review regressions: a malformed single-horizon artifact is isolated to that horizon, and unavailable history/forecast points now break chart segments instead of being visually interpolated.
- Final focused verification: 116 passed, Python compile passed, and the economic-cycle React production build passed.
- Display-window follow-up: TDD changed the read model from 121 to 60 history rows and the Cycle Map from 18 to 12 months without rewriting DB snapshots.
- Display-window Browser QA: visible 12-month/5-year copy, 62 ribbon cells, zero console/page errors, and 420px overflow <= 1px.
- Display-window final verification: 117 focused tests passed, Python compile and React production build passed, and `git diff --check` was clean.
- Ribbon/hover TDD: source contract reproduced the stale `repeat(121, ...)` grid and missing tooltip, then passed with dynamic `--history-month-count` and accessible SVG hover groups.
- Ribbon/hover Browser QA: 62 cells fill the ribbon to within 2px of the right edge; tooltip opacity is 0 by default and 1 on pointer hover/keyboard focus; browser errors 0 and 420px overflow <= 1px.
- Ribbon/hover final verification: 120 focused tests passed, Python compile and React production build passed, and `git diff --check` was clean.
- Review follow-up: empty history and missing h1 fixtures now preserve the wide history placeholder and fixed +1M/+2M slots; re-review found no remaining Critical/Important issue.
