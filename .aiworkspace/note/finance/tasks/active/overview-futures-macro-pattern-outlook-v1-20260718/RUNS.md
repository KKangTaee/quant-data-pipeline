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

## 2026-07-18 Empirical Path Task 2 — Chronological Validation

- RED: path publication cases failed on missing `path_publication_status`; horizon integration failed because `conditional_path` was absent.
- A 760-day fixture produced only 25 independent 20D episodes and correctly remained unavailable. The fixture was extended to 900 days; the 30-episode gate was not changed.
- GREEN: publication class passed 8 tests in 4.555s; full validation passed 17 tests in 8.066s and current-pattern regression passed 7 tests in 0.446s.
- Added chronological terminal Euclidean error, unconditional median baseline error, empirical 50% rectangle coverage, evaluated-fold count, and conservative probability/path status combination.
- Actual uncached snapshot: 9.491s. 5D `120 episodes / PROVISIONAL / 5 points`, 20D `42 episodes / PROVISIONAL / 20 points`.
- Actual 5D terminal `(-0.5625, 0.0169)`, 20D terminal `(-0.4364, 0.0579)`; terminals differ. Both path errors trail baseline and coverage is near 0.30, so neither path is promoted above `PROVISIONAL`.
- Bumped cache / method algorithm version to `pattern_outlook_v2_empirical_path` through a dedicated RED/GREEN contract.

## 2026-07-18 Empirical Path Task 3 — Payload And React UI

- RED: payload contracts failed because normalized horizon cards had no `conditional_path`; React source contract failed on the old fixed `REGIME_TARGETS` branch renderer.
- GREEN: two payload contracts and the empirical-map source contract passed; Vite production build completed in 459ms.
- Python copies only finite service-owned coordinates and suppresses all points / terminal when either horizon or path status is unavailable.
- React removed the four fixed categorical branches. It renders the selected horizon's median polyline, sparse 50% rectangles at first / midpoint / terminal, and one `유사 패턴 중앙 위치` marker.
- Probability rows remain in the right reading; the graph badge uses the more conservative conditional-path status.
- Corrected the detailed plan's payload-test owner from `OverviewAutomationContractTests` to `FuturesMacroThermometerContractTests` after a loader-only failure exposed the mismatch.

## 2026-07-18 Empirical Path Task 4 — Actual QA, Docs, And Closeout

- Fresh read-only actual snapshot as of `2026-07-17`: 5D `120 episodes / PROVISIONAL / 5 points`, terminal `(-0.562496, 0.016876)`, x bounds `[-1.095877, 0.083559]`, y bounds `[-0.339070, 0.331853]`; median error `0.905672` vs baseline `0.888603`, 50% rectangle coverage `0.307692`, 6 folds.
- 20D: `42 episodes / PROVISIONAL / 20 points`, terminal `(-0.436401, 0.057898)`, x bounds `[-1.098152, 0.011524]`, y bounds `[-0.254529, 0.498148]`; median error `1.061827` vs baseline `0.942778`, coverage `0.304348`, 6 folds.
- Current cache-version build measured `8.882s` uncached and `0.031s` for the same daily marker; the cached load returned the identical object.
- Browser QA at `http://localhost:8512`: 5D rendered one six-coordinate polyline, uncertainty steps `1/3/5`, and one terminal; 20D rendered one 21-coordinate polyline, steps `1/10/20`, and one terminal. The coordinates differed, and `관측만` removed line/ranges/terminal.
- Responsive QA at 420px measured iframe/root `377px`, `clientWidth == scrollWidth`; desktop also had no overflow. Console errors were 0.
- Screenshot: `/Users/taeho/.codex/visualizations/2026/07/18/019f730e-7ff9-7720-b5c6-359d96ca1a4d/futures-macro-empirical-path-qa.png` (generated, not staged).
- Durable Futures Macro flow, architecture, project ownership, milestone, and decision docs now describe observed anchors plus empirical median path / middle-50% range and the `current location + standardized conditional movement` meaning.
- Final fresh verification: pattern / path suites passed 25 tests in 8.659s; `FuturesMacroThermometerContractTests` passed 26 tests in 3.099s; four selected React/source contracts passed in 0.108s; Vite production build passed in 482ms; py_compile and `git diff --check` exited cleanly.
- Full `OverviewAutomationContractTests` was not used as a completion gate because its previously recorded unrelated Sentiment source-string case still expects `payload.summary.metrics.map`; every Futures Macro-selected Overview contract passed separately.

## 2026-07-18 Conditional Path Readability Implementation And QA

- Baseline linked-worktree contract passed before implementation. Task 1 RED failed on the existing first/midpoint/terminal range selection; GREEN replaced it with the selected path terminal only and updated graph/legend/caveat copy.
- Task 2 RED failed on the endpoint marker. GREEN added fixed 9-unit `userSpaceOnUse` observed/forecast markers on inset screen-space segments, current/terminal radii 10/8, separated leader labels, and the rebuilt production bundle.
- Focused verification passed: pattern/path suites 25 tests, thermometer contracts 26 tests, selected React/source contracts 6 tests; Vite build, helper py_compile, and `git diff --check` passed.
- Browser QA at `http://localhost:8512`: observed state had forecast layers `0/0/0/0`; 5D had step-5 range/path/direction/terminal `1/1/1/1`; 20D had step-20 range/path/direction/terminal `1/1/1/1`. 5D/20D probability rows and `PROVISIONAL` remained unchanged.
- Current/terminal labels did not overlap either circle. At 420px the workbench and document both measured `clientWidth == scrollWidth` (`377px`), all graph labels remained within the canvas, and browser console errors were 0.
- Screenshot: `/Users/taeho/.codex/visualizations/2026/07/18/019f730e-7ff9-7720-b5c6-359d96ca1a4d/futures-macro-single-range-qa.png` (generated, not staged).

## 2026-07-18 Stable Coordinate Follow-up

- Root cause: selected `forecastPoints`, including visually hidden intermediate q25/q75, owned `xBound / yBound`. The raw observed anchors were unchanged, but the 5D x-bound `1.503856` and 20D x-bound `2.003118` projected them to different SVG positions.
- RED: the shared-scale source contract failed because `scalePaths` did not exist. GREEN: both available horizon median paths and terminal ranges now own one bound; hidden intermediate ranges are excluded. Four selected map contracts passed and Vite rebuilt the production bundle in commit `766dada9`.
- Actual Browser QA: `관측만 / 5D / 20D` all returned anchor circles `(456.896630, 175.952879)`, `(306.165738, 130.959194)`, `(193.173735, 206.159142)`. Equality was exact.
- 5D used uncertainty step `5` with terminal `(226.801050, 192.529943)`; 20D used step `20` with terminal `(256.660352, 186.525904)`. Forecast polylines and terminals differed while observed anchors remained fixed.
- At 420px the iframe, workbench, and map had no horizontal overflow (`377px == 377px`), labels stayed inside the canvas, and console errors were 0.
- Screenshot: `/Users/taeho/.codex/visualizations/2026/07/18/019f730e-7ff9-7720-b5c6-359d96ca1a4d/futures-macro-stable-coordinate-qa.png` (generated, not staged).

## 2026-07-19 Net Direction Implementation And QA

- Root cause: React connected every step's independently aggregated x/y median as one polyline. The data was valid for stepwise validation, but the visual suggested one coherent daily route and exposed median switching as repeated reversals.
- RED: the new source contract failed on missing direct `x1/y1/x2/y2`, existing `forecastPolyline`, and `scaleForecastPoints`. The shared-scale contract also failed because hidden intermediate medians still owned chart bounds.
- GREEN: `9e40341c` renders one current-to-terminal SVG `line`, changes the legend to `5일/20일 예상 순이동`, explains that it is not an intermediate daily route, and derives the common bound from anchors plus both terminal/ranges. Five selected map contracts and Vite production build passed.
- Actual 5D: line start/current `(193.173735, 206.159142)`, line end/terminal `(226.801050, 192.529943)`, step-5 range/path/direction/terminal `1/1/1/1`.
- Actual 20D: the same start/current, line end/terminal `(256.660352, 186.525904)`, step-20 range/path/direction/terminal `1/1/1/1`. Both lines had no polyline `points` attribute and the three anchor tuples matched 5D/20D/observed exactly.
- `관측만` forecast/range/direction/terminal was `0/0/0/0`. Desktop root/workbench measured `1280/1109px` with equal client/scroll widths; 420px root/iframe/workbench/map measured `420/377/377/371px`, again with equal client/scroll widths. All four graph labels remained inside the canvas and console errors were 0.
- Screenshot: `/Users/taeho/.codex/visualizations/2026/07/18/019f730e-7ff9-7720-b5c6-359d96ca1a4d/futures-macro-net-direction-qa.png` (generated, not staged).
