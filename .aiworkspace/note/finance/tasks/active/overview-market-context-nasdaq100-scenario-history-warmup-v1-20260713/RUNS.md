# Overview Market Context Nasdaq-100 Scenario History Warmup V1 Runs

Last Updated: 2026-07-13

## Design Stage

- Verified branch `codex/sub-dev` and clean tracked state.
- Preserved unrelated untracked research bundle without reading, editing, staging, or committing it.
- Reviewed finance documentation map, existing 60-month repair design/status, valuation service ownership, and current action/UI contracts.
- User approved the written design; created and self-reviewed the detailed five-stage inline TDD plan.

## 1차 — Rolling Warmup Contract

- Baseline Nasdaq/S&P/Market Context: 76 tests, `OK`.
- RED: 60 positive PER months produced one point but lacked `reason_code`; targeted test failed with `KeyError`.
- GREEN: history payload now reports requested/rolling/required/available/missing month counts and `INSUFFICIENT_ROLLING_PER_WARMUP`.
- S&P valuation regression: 38 tests, `OK`; existing 12/36/60-point READY behavior remains unchanged.

## 2차 — 119-Month Repair Contract

- RED: `NASDAQ100_SCENARIO_HISTORY_REPAIR_MONTHS` import failed and Overview result lacked `requested_months`.
- GREEN: the inclusive window is 2016-09-01 through 2026-07-31 for 119 months.
- Overview facade forwards `months=119` and records dynamic valuation/history repair purpose without changing its 60-month default.
- Nasdaq 30 tests and Market Context 11 tests, `OK`.

## 3차 — History Action / EPS Provenance

- RED: the 60-month READY Nasdaq model lacked `history_repair_action` and calculated earnings provenance.
- GREEN: rolling-warmup insufficiency exposes `repair_nasdaq100_history_119m`; blocked valuation retains the separate 60-month coverage action.
- EPS source is now `QQQ 구성종목 실제 희석 EPS 재구성`, quality `reconstructed_actual`, with the actual evidence basis date.
- Market Context 11 tests, `OK`.

## 4차 — Python / React Repair UX

- RED: the 119-month event was rejected and the UI still blamed missing SEP.
- GREEN: approved action ids map to exact 60/119 month calls with nonce dedup; result reflection records requested months.
- The selected period now shows required/current history months and an explicit repair action; history labels follow SPX or QQQ dynamically.
- Missing EPS source no longer defaults to Robert Shiller; the neutral fallback is `EPS 출처 미확정`.
- Market Context 13 tests and two focused service contracts, `OK`; React Vite build and Python compile passed.
- A first focused service-contract command used the wrong unittest class name; rerun under `OverviewAutomationContractTests` passed.

## 5차 — Actual Repair / QA / Closeout

- Read-only 119-month plan: 2016-09 through 2026-07, before 62 READY / 57 BLOCKED, 63 total targets, 1 unsupported target.
- Canonical `run_overview_nasdaq100_valuation_repair(months=119)` completed as `partial_success`; EPS 63/63 and price 26/26 batches ran, 172,240 rows were written, and READY/BLOCKED moved to 66/53.
- 23 symbols failed collection: `ALXN ANSS ATVI CA CELG CERN CTXS DISH LLTC MYL SGEN SPLK SYMC VIAB WBA XLNX YHOO MXIM QRTEA QVCA SHPG SRCL WFM`.
- Post-run plan has 50 targets: 49 quarterly diluted-EPS gaps, 23 EOD gaps, 2 unsupported free-source rows, and 1 missing-identity row.
- Service parity after the partial-window status fix: 1y 71/66/5, 3y 95/66/29, 5y 119/66/53; each has 7 computed points and remains `INSUFFICIENT_HISTORY`.
- Browser QA after restarting the local Streamlit process: graph 1 visible, graph 2 uses actual QQQ EPS source/basis, all three period tabs show exact requirement/current counts and the 119-month action.
- Desktop and 420x900 viewport passed; outer/iframe horizontal overflow was 0 and current port 8501 console error count was 0. Screenshot was stored at `/tmp/codex-nasdaq100-history-warmup-desktop.png` and not staged.
- Final task regression: Nasdaq/S&P/Market Context 83 tests `OK`; Python compile, React Vite build, and `git diff --check` passed.
- Full `tests.test_service_contracts`: 805 tests ran, 803 passed, and 2 unrelated existing contracts failed. Both reproduce alone and are outside this task's modified paths: Market Movers EOD history expected 65 rows but returned 2, and Sentiment React expected the obsolete literal `payload.summary.metrics.map`.
