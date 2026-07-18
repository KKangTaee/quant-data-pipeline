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
