# Futures Macro Pattern Outlook V1 Runs

## 2026-07-18 Analysis

- Read current finance docs, Overview flow boundaries, active Futures Macro research, and prior Futures Monitor task records.
- Inspected `futures_macro_thermometer.py`, `futures_macro_validation.py`, current React workbench, and economic-cycle React visual patterns.
- Ran read-only actual Futures Macro snapshot and validation against local DB.
- Confirmed 5.4-year stored history, 1,175 validation dates, and 915 `혼재된 매크로 흐름` dates without directional metrics.
- Reviewed CFTC, CME, Federal Reserve, and primary research evidence on price discovery, nearly continuous trading, market expectations, and risk premia.

## 2026-07-18 Design

- Created the active task shell and approved design contract.
- No code or data mutation was executed.

## 2026-07-18 Implementation Planning

- User approved `DESIGN.md` and requested continuation.
- Expanded `PLAN.md` into seven TDD implementation tasks covering point-in-time features, current state, independent episodes, chronological publication gates, Python payload V2, React workbench V2, and actual QA / documentation closeout.
- Implementation code was not changed during planning.

## 2026-07-18 UI Selection And Execution Start

- Compared three UI wireframes; user selected `A · 맥락→전망형`.
- Confirmed this workspace is an existing linked worktree on `codex/sub-dev`; no nested worktree was created.
- Baseline `pytest` command stopped before collection because `.venv` has no pytest module.
- Root-cause check confirmed `pyproject.toml` has no pytest dependency and durable finance docs identify `unittest` as the current local verification path.
- `.venv/bin/python -m unittest tests.test_service_contracts.FuturesMacroThermometerContractTests` passed 23 tests; only existing third-party deprecation warnings appeared.

## 2026-07-18 Task 1 — Multi-Window Features

- RED: `.venv/bin/python -m unittest tests.test_futures_macro_pattern` failed 3 tests because `app.services.futures_macro_pattern` did not exist.
- GREEN: the same command passed 3 tests after adding trailing-only 1D / 5D / 20D family features.
- Regression: `.venv/bin/python -m unittest tests.test_service_contracts.FuturesMacroThermometerContractTests` passed 23 tests.
- `.venv/bin/python -m py_compile app/services/futures_macro_pattern.py` and `git diff --check` passed.

## 2026-07-18 Task 2 — Current Pattern State

- RED: `.venv/bin/python -m unittest tests.test_futures_macro_pattern.FuturesMacroCurrentPatternTests` failed 4 tests because the current pattern API did not exist.
- A fixture-only pandas 3.0 dtype error was traced to assigning `pd.NA` into float columns and corrected to numeric `NaN` before evaluating production behavior.
- GREEN: `.venv/bin/python -m unittest tests.test_futures_macro_pattern` passed 7 tests.
- Regression: `FuturesMacroThermometerContractTests` passed 23 tests; py_compile and diff check passed.

## 2026-07-18 Task 3 — Forward Outcomes And Similar Episodes

- RED: `.venv/bin/python -m unittest tests.test_futures_macro_pattern_validation` failed 4 tests because the validation module did not exist.
- First GREEN established exclusive 5D / 20D outcome labels, future-row stability, overlap exclusion, and trading-row anchor spacing.
- A second RED showed path IQR was still a placeholder (`0.0`); the implementation now measures intermediate cumulative paths using only as-of volatility.
- GREEN: pattern validation passed 4 tests in 4.392s; current pattern regression passed 7 tests; py_compile and diff check passed.

## 2026-07-18 Task 4 — Publication Gate And Cache

- RED: five publication tests failed on absent Brier, fold, gate, and outlook APIs.
- The first outlook fixture produced only 26 independent 5D episodes after warm-up and spacing; the gate remained unchanged and the fixture was extended from 260 to 300 days to exercise `PROVISIONAL` behavior.
- Publication tests passed 5 tests; the complete validation module passed 9 tests before the cache cycle.
- Cache TDD was restarted from RED by removing the uncommitted public loader; the missing cache API failed as expected, then passed after marker-keyed loader restoration.
- Final GREEN: validation module passed 10 tests, legacy Futures Macro contracts passed 23 tests, py_compile and diff check passed.

## 2026-07-18 Task 5 — Default Outlook And Payload V2

- RED covered missing V2 payload shape, current/future horizon separation, unavailable probability suppression, cache clearing, and the thermometer-pattern handoff.
- The active tab now loads the pattern outlook by default for both React and native fallback; the legacy `load_validation` action and button are absent from the active panel and event path.
- Refresh and reload clear both the thermometer snapshot cache and the latest-marker pattern validation cache.
- GREEN: pattern feature / validation modules plus Futures Macro service and Overview contracts passed 46 tests in 10.975s; only existing third-party and bare-Streamlit warnings appeared.

## 2026-07-18 Task 6 — React Workbench V2

- RED: reading-order and responsive contracts failed because the five V2 section sources did not exist.
- Implemented A안 with a current-regime hero, separate current / 5D / 20D horizon cards, observed path plus non-connected conditional zones, evidence bridge, 60D ribbon, five asset pathways, and collapsed method disclosure.
- Vite production build passed in 489ms and emitted a new static CSS / JS bundle.
- GREEN: focused React source contracts passed 3 tests; combined Futures Macro feature, validation, service, and UI selection passed 48 tests in 11.605s.
- Repository-wide reference check found the legacy Recent Flow and Historical Validation files were referenced only by themselves, so both were removed rather than retained as dead compatibility code.

## 2026-07-18 Task 7 — Actual QA, Performance, And Docs

- Focused verification before actual QA: pattern modules passed 17 tests in 8.396s; service-contract selection passed 26 tests in 2.823s; py_compile and diff check passed.
- First read-only actual measurement: `2026-07-17`, `mixed / transition_attempt`; 5D `PROVISIONAL` / 120 episodes / Brier 0.7181676141 vs 0.7155593658, 20D `PROVISIONAL` / 42 episodes / Brier 0.6585791797 vs 0.6936063270; both `방향 우위 미확인`; uncached 21.791s.
- cProfile recorded 269,434,679 calls and 63.239s profiler runtime; 13,722 `_forward_path_statistics` calls consumed 53.014s cumulative under profiling.
- Added a vectorized/reference parity RED/GREEN contract and replaced repeated path objects with vectorized as-of matrices. Outcome tests passed 5 tests in 1.828s.
- Second actual measurement: same published values, uncached 4.963s, cached 0.031s, cached object identity true. No DB materialization was added.
- Browser QA URL: `http://localhost:8512`; desktop structure 3 horizon cards / map / evidence / ribbon / 5 pathways / method, 0 console errors. At 420px, horizon / pattern / asset grids were one column and root `clientWidth == scrollWidth` (377px).
- Desktop screenshot: `/Users/taeho/.codex/visualizations/2026/07/18/019f730e-7ff9-7720-b5c6-359d96ca1a4d/futures-macro-a-desktop.png` (generated, not staged).
- `finance-doc-sync` aligned flow, architecture, project map, root milestone, and durable decision logs with the V2 behavior.
- Final verification after docs: pattern modules passed 18 tests in 2.853s; selected service contracts passed 26 tests in 2.702s; Vite production build passed in 441ms; py_compile and `git diff --check` exited cleanly.

## 2026-07-18 Task 8 — Readable Observed Path / Conditional Branches

- Root cause: `PatternMapSection.tsx` connected all 60 daily path points with one stroke, while `_pattern_outlook_zones()` collapsed each horizon into a single ellipse with a fixed y-radius. The UI therefore hid time order and made a conditional distribution look like one forecast location.
- RED: the focused contract failed because the component still rendered `<ellipse>`, did not receive `horizons`, lacked `관측만 / 다음 5D / 다음 20D`, and the payload still contained `zones`.
- GREEN: the two focused UI/payload contracts passed; Vite emitted the new production bundle. Python now sends the current path only, while React reuses existing horizon probability rows, status, edge label, episode count, and reason.
- Actual Browser QA at `http://localhost:8512`: default 5D rendered three observed anchors and four branches with `38/5/23/34%`, `PROVISIONAL`, `방향 우위 미확인`, 120 episodes. 20D switched to `43/10/21/26%`, 42 episodes. `관측만` reduced branches from four to zero.
- 420px QA: root `clientWidth == scrollWidth` (`377px`), pattern body and evidence grid each resolved to one column, console errors 0.
- Final bundle reload: three anchors, four 5D branches, selected button state, desktop `clientWidth == scrollWidth` (`1109px`), and console errors 0.
- QA screenshot: `/Users/taeho/.codex/visualizations/2026/07/18/019f730e-7ff9-7720-b5c6-359d96ca1a4d/futures-macro-conditional-branches-qa.png` (generated, not staged).
- Verification: pattern feature / validation modules passed 18 tests; selected Futures Macro React and thermometer contracts passed 30 tests; Vite build, py_compile, and diff check passed.
- Broader `OverviewAutomationContractTests` discovery has one pre-existing unrelated Sentiment source-string failure (`payload.summary.metrics.map`); the four selected Futures Macro React contracts and all `FuturesMacroThermometerContractTests` pass.
- Pre-commit integration review added a short-history RED/GREEN guard: 5D / 20D anchors are omitted unless that many prior rows exist, so a single current row is never mislabeled as `20D 전`.

## 2026-07-18 Empirical Conditional Path Follow-up Design

- Reproduced the reported 5D / 20D switch against the actual local app.
- Confirmed horizon selection, probabilities, sample count, stroke width, and outcome radius change correctly.
- Confirmed all four SVG branch `d` coordinates are identical because `REGIME_TARGETS` is horizon-independent.
- Inspected the service and found completed historical outcomes already retain as-of-volatility-scaled family endpoint and path statistics, while the current payload does not expose stepwise two-dimensional paths.
- User approved replacing fixed categorical branches with historical-analog stepwise median movement and a 25~75% uncertainty area.
- Wrote the follow-up statistical, leakage, validation, payload, UI, fallback, and acceptance contract in `DESIGN.md`; no implementation code was changed.
- User approved the written spec and requested continuation.
- Added `EMPIRICAL_PATH_PLAN.md` with four sequential TDD tasks: stepwise coordinates, chronological path validation, payload / React UI, and actual QA / documentation closeout.
- Plan self-review covers the written spec requirements, exact interfaces, RED/GREEN commands, type consistency, unavailable suppression, and 5D / 20D actual-coordinate comparison.

## 2026-07-18 Empirical Path Task 1 — Stepwise Coordinates

- Baseline linked-worktree check: `codex/sub-dev`; pattern suites passed 18 tests and thermometer contracts passed 26 tests.
- RED: two coordinate tests failed on missing `build_forward_coordinate_frame`; aggregate tests failed on missing `_conditional_path_payload`.
- GREEN: outcome class passed 9 tests in 3.193s and current-pattern regression passed 7 tests in 0.444s.
- Completed-origin stability excludes incomplete forward rows; adding later candles does not change an already completed 20D coordinate path.
- The service now emits 1..5 / 1..20 standardized `delta_x / delta_y` rows and aggregates current-location-adjusted median plus q25/q75 bounds. Below 30 episodes exposes no coordinates.
