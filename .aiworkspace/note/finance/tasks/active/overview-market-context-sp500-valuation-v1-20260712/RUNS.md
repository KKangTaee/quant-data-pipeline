# Overview Market Context S&P 500 Valuation V1 Runs

Status: Active
Last Updated: 2026-07-12

## Design Research

- Read finance INDEX, ROADMAP, PROJECT_MAP, PRODUCT_DIRECTION, architecture/flow docs, and Market Context ownership files.
- Inspected current Market Context entrypoint, helpers, component, service, tests, and recent git history.
- Verified official Federal Reserve SEP accessible materials and definitions.
- Verified S&P Index Earnings discoverability and index/divisor methodology.
- Downloaded and inspected the official Shiller workbook outside the repository.
- Compared 3y, 5y, and 10y log(PER) windows using latest complete Shiller earnings data.
- Rewrote the UI design section in Korean and added explicit before/after UI trees during written-spec review.
- Converted the approved design into a five-task TDD implementation plan with exact file ownership, interfaces, verification commands, and commit boundaries.

## Repository Mutation

- Added valuation DDL, Shiller/S&P EPS/SEP source normalization, workbook readers, and parameterized UPSERT collectors.
- Added `openpyxl`/`xlrd` dependency declarations and regenerated `uv.lock`.

## 1차 Verification

- `.venv/bin/python -m unittest tests.test_sp500_valuation`: 8 tests passed.
- `.venv/bin/python -m py_compile finance/data/sp500_valuation.py finance/data/db/schema.py`: passed.
- Official Fed calendar discovery returned `fomcprojtabl20260617.htm`; parser emitted 18 GDP/PCE rows for vintage `2026-06-17`.
- `git diff --check`: passed.
- The repository environment does not include pytest, so plan test selectors are executed with equivalent `unittest` commands.

## 2차 Verification

- Initial loader/service imports failed as expected before implementation.
- `.venv/bin/python -m unittest tests.test_sp500_valuation`: 10 tests passed after implementation.
- `.venv/bin/python -m py_compile finance/loaders/sp500_valuation.py app/services/overview/sp500_valuation.py`: passed.
- Full `tests.test_service_contracts` run executed 749 tests and exposed one unrelated pre-existing Sentiment React source-string contract failure (`payload.summary.metrics.map`). The failing Sentiment source is outside this task's diff.

## 3차 Verification

- Scenario/read-model imports failed as expected before implementation; stale SEP test failed before the guard was added.
- `.venv/bin/python -m unittest tests.test_sp500_valuation`: 14 tests passed.
- `.venv/bin/python -m py_compile app/services/overview/sp500_valuation.py finance/loaders/sp500_valuation.py`: passed.
- `git diff --check`: passed.

## 4차 Verification

- New React scaffold contract failed before component creation as expected.
- `npm install`: 0 vulnerabilities.
- `npx tsc --noEmit`: passed after declaring React type dependencies and explicit Streamlit callback boundary types.
- `npm run build`: Vite production build passed; compiled assets generated under `component_static/`.
- `.venv/bin/python -m unittest tests.test_service_contracts -k market_context`: 31 tests passed.
- Focused entrypoint/component plus valuation suite: 17 tests passed.
- Python compile for Market Context entrypoint/helpers/component wrapper: passed.

## 5차 Verification

- Job/automation and schema-bootstrap tests followed RED-to-GREEN; valuation suite now has 18 passing tests.
- Daily `sp500_valuation` automation spec checks the latest official SEP accessible-material vintage outside market-hours restrictions.
- `uv sync` installed the locked XLS/XLSX readers.
- Live ingestion stored 1,863 Shiller monthly rows, 18 latest SEP rows, and 40 SPX/SPY EOD rows; S&P earnings stayed explicitly skipped without a configured workbook.
- Browser QA found and fixed missing optional-table bootstrap and dark-theme text inheritance issues.
- Browser DOM confirmed both React sections and blocked-state copy; browser console errors: 0.
- QA screenshot: `market-context-sp500-valuation-qa.png` (generated, not committed).
- Durable index/roadmap/project/architecture/data/flow docs and root handoff logs synchronized.
- Final full service-contract run: 759 tests, 2 out-of-scope failures. Sentiment still expects removed `payload.summary.metrics.map`; Market Movers EOD repair test reads persisted limited-history DB state and returns the first mocked 2-row repair only instead of isolated 65-row expectation.
- Final scoped gates passed after that run: 18 valuation tests, 31 Market Context contracts, Python compile, TypeScript check, Vite build, and `git diff --check`.

## V1.1 Data Activation Verification

- Baseline reproduced: existing 18 valuation tests and 31 Market Context contracts passed, while the DB-backed read model returned graph 1/2 `BLOCKED` because official EPS rows were zero.
- TDD RED confirmed graph 1 required current SPX/EPS, resolver functions were absent, SEP used compounded growth, and React omitted source/fallback/macro input fields.
- GREEN: 24 valuation tests and 32 Market Context contracts passed; `npx tsc --noEmit` and Vite production build passed.
- DB-backed smoke returned both graphs `READY`: Shiller PER `25.4254x`, Shiller EPS `261.723` at `2026-03-01`, SEP `2026-06-17`, expected EPS `276.902934`, SPX band `6266.55 / 6958.23 / 7726.27`, current-vs-baseline gap `+8.87%`.
- Browser QA at desktop and 420px confirmed both charts, source/basis/fallback copy, no horizontal overflow, and zero browser console errors. Screenshot: `market-context-sp500-valuation-v1-1-qa.png` (generated, not committed).
- Fresh final gates repeated 24 valuation tests, 32 Market Context contracts, Python compile, DB assertions, TypeScript, Vite build, and `git diff --check` successfully.
- Full `tests.test_service_contracts` ran 742 tests with the same 2 out-of-scope failures already tracked here: Sentiment source-string expectation and Market Movers persisted limited-history isolation.
- Final integration review added an explicit canonical Shiller source predicate to the fallback loader and repeated the 24-test valuation/DB smoke successfully.

## V1.2 Visual And Historical Scenario Verification

- TDD RED reproduced missing price-only Shiller rows, missing SEP-history discovery/collector, missing all-vintage loader, missing `minus_2sigma`, missing historical service, and missing React history contracts.
- GREEN targeted/full runs reached 31 valuation tests and 33 Market Context contracts; Python compile, TypeScript `tsc --noEmit`, and Vite production build passed.
- Official backfill stored four missing releases: 2025-06-18, 2025-09-17, 2025-12-10, 2026-03-18. DB now contains five SEP vintages including 2026-06-17.
- Latest Shiller refresh wrote 1,867 rows and preserved 2026-04~07 price-only rows; latest positive EPS/PER remains 2026-03.
- DB-backed history returned 12 points (2025-08~2026-07), four visible SEP markers, current SPX 7,575, baseline 6,958, lower/upper 6,267/7,726, and current-vs-baseline +8.9%.
- Browser QA on `http://localhost:8527` verified both charts, hover transition from 2026-07 to 2025-10, symmetric 2σ labels, 12-month band, desktop and 420px layout, current-app console errors 0, outer/iframe horizontal overflow 0.
- QA screenshot: `market-context-sp500-valuation-v1-2-qa.png` (generated, not committed).
- Fresh final scoped gates: 31 valuation tests, 33 Market Context contracts, Python compile, TypeScript, Vite build, 5-vintage/12-point DB assertions, and `git diff --check` passed.
- Full `tests.test_service_contracts`: 743 tests, 2 pre-existing out-of-scope failures. Sentiment still expects removed `payload.summary.metrics.map`; Market Movers still reads persisted limited-history DB state and reports 2 instead of isolated 65 rows.

## V1.3 Graph 1 Provisional Extension Verification

- TDD RED reproduced the missing `current_spx` input/provisional quality fields and missing React provisional/inspector contracts.
- GREEN focused/full runs reached 33 valuation tests and 34 Market Context contracts; TypeScript and Vite production build passed.
- DB-backed read model returned current provisional PER `28.9443x` at SPX EOD `2026-07-10`, latest complete PER `25.4254x` at `2026-03-01`, distribution basis `2021-04` through `2026-03`, and display through `2026-07`.
- Browser QA on `http://localhost:8528` confirmed solid complete/dashed provisional line, `2026.07` x-axis/current inspector, point-adjacent right-edge-flipped card, desktop layout, 420px outer/iframe horizontal overflow 0, and browser warning/error log 0.
- QA screenshot: `market-context-sp500-valuation-v1-3-qa.png` (generated, not committed).
- Fresh final gates: 33 valuation tests, 34 Market Context contracts, Python compile, TypeScript, Vite build, live DB assertions, and `git diff --check` passed.
- Full `tests.test_service_contracts`: 744 tests, the same 2 out-of-scope failures remained: Sentiment source-string expectation and Market Movers persisted limited-history isolation (`2` vs `65`).

## V1.4 Graph 2 1·3·5-Year Verification

- Baseline: 33 valuation tests and 34 Market Context contracts passed in the existing linked `codex/sub-dev` worktree.
- TDD RED/GREEN covered calendar-discovered missing-vintage fetch, dynamic 12/36/60-month metadata, read-model `history_options`, React selector/sparse labels, and the 120-month loader warmup regression.
- All 21 current official Federal Reserve projection pages parsed successfully before DB mutation. Live backfill wrote 326 rows for 16 missing releases; DB now has 21 release vintages from `2021-03-17` through `2026-06-17`.
- Initial live read-model smoke exposed the 84-month loader warmup gap: 3y/5y returned only 25 points. After the TDD fix, DB-backed options returned 12 points (`2025-08~2026-07`), 36 (`2023-08~2026-07`), and 60 (`2021-08~2026-07`).
- Browser QA on `http://localhost:8529` switched 1y→3y→5y and verified dynamic headings/aria labels. The 5y chart kept 19 SEP marker lines while limiting SEP/x-axis text labels to 7 each.
- Desktop and 420px Browser QA returned outer/iframe horizontal overflow 0 and current-app warning/error log 0. Screenshot: `market-context-sp500-valuation-v1-4-qa.png` (generated, not committed).
- Fresh scoped gates: 37 valuation tests, 35 Market Context contracts, Python compile, TypeScript, Vite build, live DB assertions, and `git diff --check` passed.
- Full `tests.test_service_contracts`: 745 tests with the same 2 out-of-scope failures: Sentiment source-string expectation and Market Movers persisted limited-history isolation (`2` vs `65`).
