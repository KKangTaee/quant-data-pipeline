# Overview Market Context Turnaround Stage Semantics Fix V1 Runs

Last Updated: 2026-07-16

## Diagnosis

- `build_market_context_valuation_read_model(selected_symbol="AAPL")` read-only actual: PER READY/current P/E `39.324x`; turnaround `CASH_FLOW_TURN`, EPS null, PER_READY NOT_MET.
- DB read-only EPS audit: latest AAPL diluted EPS `2.84`, unit `USD per share`, period end `2025-12-27`, available `2026-01-30`.
- Runtime-only allowlist hypothesis test: TTM EPS `7.90`, headline `PER_READY`, PER_CANDIDATE/PER_READY MET.
- No provider call, DB write, registry append, source edit, or generated artifact was produced during diagnosis.

## Detailed Plan And Baseline

- Confirmed existing linked worktree `/Users/taeho/Project/quant-data-pipeline-worktrees/sub-dev` on `codex/sub-dev`; no nested worktree was created.
- Preserved unrelated untracked `researches/active/2026-07-market-interest-free-source-benchmark/`.
- Focused baseline `.venv/bin/python -m unittest tests.test_us_stock_turnaround tests.test_us_stock_valuation tests.test_market_context_valuation` -> 100 tests passed.
- Expanded `PLAN.md` into 1차 EPS reader/evidence, 2차 six-rail semantic display, 3차 actual/Browser QA/docs with exact RED/GREEN commands and commits.
- Self-review found no placeholder, uncovered spec requirement, class-name mismatch, or interface/type contradiction.

## 1차 EPS Reader And Operating Evidence

- Loader RED: `TurnaroundLoaderTests.test_loader_reads_canonical_usd_per_share_eps_rows` failed because no timeline row was available while `USD per share` was absent from duration query params.
- Loader GREEN: added canonical `USD per share` to `_DURATION_UNITS`; the same public-loader test passed with latest TTM EPS `6.2` and no diluted-EPS coverage gap.
- Evidence RED: `TurnaroundMilestoneAndRiskTests.test_profitable_but_below_threshold_operating_margin_exposes_context` errored with missing `current_operating_margin_pct`.
- Evidence GREEN: exposed current operating margin, latest YoY delta, and recent threshold-hit count without changing the existing `>= 1.0pp`/2-of-3 threshold.
- Focused regression: `.venv/bin/python -m unittest tests.test_us_stock_turnaround tests.test_us_stock_valuation tests.test_market_context_valuation` -> 102 tests passed.
- Compile and scope checks: `py_compile` for both changed Python modules and `git diff --check` exited 0.

## 2차 Six-Rail Semantic Display

- React contract RED: both new tests failed because `ESTABLISHED`, the revised rail copy, and its styles did not exist.
- React contract GREEN: added typed UI-local display state, Korean headline/status labels, distinct established-state styles, and six independent display rows.
- A profitable-but-below-threshold operating state now reads `흑자 · 개선폭 미달`; positive TTM EPS reads `이미 양수`; neither changes backend milestone statuses.
- Focused regression: `.venv/bin/python -m unittest tests.test_market_context_valuation tests.test_us_stock_turnaround tests.test_us_stock_valuation` -> 104 tests passed.
- Production asset build: `npm run build` transformed 171 modules and emitted new hashed JS/CSS assets; `git diff --check` exited 0.

## 3차 Actual, Regression, And Browser QA

- Actual AAPL DB-only read: PER TTM EPS and turnaround latest TTM EPS both `7.90`; headline `PER_READY`; `PER_READY=MET`; current operating margin `32.38%` with latest YoY delta `+0.63pp` and 0 recent threshold hits.
- Actual RIVN DB-only read: TTM EPS `-3.07`; `EARNINGS_TURN`, `PER_CANDIDATE`, and `PER_READY` remain `NOT_MET`; recommended analysis remains `turnaround`.
- Focused final scope: calendar/freshness/turnaround/valuation/Market Context 118 tests passed; four changed Python modules compiled.
- Repository discovery: 1100 tests, 4 failures, 154 errors. This matches the pre-task baseline after adding four new passing tests: the same two Practical Validation source-contract failures, one Market Movers contract failure, one Sentiment contract failure, and the same Streamlit reimport isolation errors.
- Browser QA after restarting the no-file-watcher local server: AAPL showed `PER 적용 가능 / 분석 가능`, `흑자 · 개선폭 미달`, `이미 양수`, and `적용 가능`; PER tab retained `상대적 고평가`.
- RIVN at 420px showed operating improvement only while OCF/FCF/EPS/PER remained independent and unconfirmed. Desktop and 420px outer/component horizontal overflow were 0; no new console errors occurred after restart.
- Representative screenshot: `/Users/taeho/.codex/visualizations/2026/07/15/019f65a4-445f-79b2-8e17-0e3b374b88b3/turnaround-stage-aapl-desktop-20260716.png` (generated artifact, not staged).
