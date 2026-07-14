# Overview Market Context US Stock Valuation V1 Runs

Last Updated: 2026-07-14

## Design Feasibility Audit

- Inspected current Market Context combined service, Nasdaq adapter, React valuation component, price loader, SEC detailed statement pipeline, symbol lifecycle, and ingestion actions.
- Confirmed the user-facing Nasdaq replacement can reuse the existing instrument-scoped React surface.
- Queried actual MySQL price and diluted-EPS coverage for AAPL, MSFT, NVDA, AMZN, META, and TSLA.
- Confirmed common large-cap samples have sufficient raw history for a selected-symbol bounded calculator.
- Confirmed the unrelated untracked research folder remains the only dirty-tree entry before design documentation.

## External Method Check

- Federal Reserve SEP describes economy-wide real GDP, unemployment, PCE inflation, and policy-rate projections.
- BEA PCE describes prices paid for U.S. consumer goods and services.
- Decision: GDP+PCE is retained as an explicitly labeled macro proxy, not a company EPS identity.

## Design Documentation

- Created compact active-task shell with PLAN, DESIGN, STATUS, NOTES, RUNS, and RISKS.
- Self-review found and fixed an ambiguous input window: valuation price/SEP is bounded to 119 months, while SEC statement loading includes up to 18 additional months solely to form the first four-quarter TTM.
- Placeholder, contradiction, scope, and `git diff --check` review passed after the correction.
- Required-file checks, staged-path audit, and `git diff --cached --check` passed; the unrelated untracked research folder remains unstaged.
- Implementation commands/tests have not been run because code implementation has not started.

## 2026-07-14 Implementation Baseline

- Confirmed current path is an existing linked worktree on `codex/sub-dev`; no new worktree was created.
- `pytest` is not installed in `.venv`; repository `unittest` runner is used instead.
- Baseline: `83 tests` across Nasdaq, S&P, and combined Market Context passed.

## 1차 Calculation Correctness

- RED reproduced a comparative FY fact creating a false `-0.77` Q4.
- GREEN: true fiscal year-end predicate fixed the regression; two resolver tests and full Nasdaq file passed.
- RED/GREEN: split-neutral, monthly carry-forward, future filing, non-positive EPS, and missing-price tests passed.
- Fresh 1차 verification: `76 tests` across Nasdaq, U.S. stock pure calculation, and S&P passed; both changed Python modules compiled; `git diff --check` passed.

## 2차 US Stock Valuation Engine

- RED/GREEN loader tests proved current active SEC-linked identity plus one-symbol bounded price/statement/SEP queries.
- RED/GREEN engine tests covered 59/60-month Graph 1 boundary, 36-month sensitivity, applicable SEP, Tukey clipping, eight-observation gate, scenario formulas, 60-month historical warmup, and readiness taxonomy.
- RED/GREEN service tests covered NOT_SELECTED no-load behavior, READY JSON safety, exact COLLECTABLE action ranges, NOT_APPLICABLE action suppression, and stable ERROR shape.
- Fresh 2차 verification: all `16` U.S. stock tests passed; data/loader/service modules compiled; `git diff --check` passed.

## 3차 Search And Collection

- RED/GREEN search tests covered no-query DB silence, ticker/name ranking, and non-common/inactive exclusion.
- RED/GREEN preflight tests covered exact price/SEC gaps, structural short listing, negative EPS, and READY inputs.
- RED/GREEN ingestion tests covered exact synchronous price/SEC calls, progress order, and pre-provider CIK mismatch rejection.
- Overview action tests covered partial-success after-state, narrowed statement-only resume, and READY no-op idempotency.
- Main readiness regression proves 60 complete months can be READY even when the optional 119-month history window remains incomplete.

## 4차 Market Context UI Replacement

- RED/GREEN combined-model tests prove the exact `sp500/us_stock` key set, selected/search argument forwarding, stock failure isolation, and unchanged S&P payload.
- RED/GREEN event tests prove read-only search/selection, selected-symbol validation, once-only collection nonce handling, and rejection of former Nasdaq repair action IDs.
- Static UI contract tests prove the new selector, stock search/selection actions, readiness states, explicit collection action, macro/company-growth evidence, 1/3/5-year history, and target-price disclaimer.
- Source scan found no `Nasdaq-100`, `QQQ`, or `repair_nasdaq` token in the new React/Streamlit/combined user path.
- Fresh React production build passed; focused U.S. stock, S&P, Nasdaq-backend, and combined regression passed `113 tests`.

## 5차 Actual DB And Edge Audit

- Initial actual read reproduced AAPL/NVDA/META/TSLA as ERROR because the local DB had active listing/profile rows but no current SEC lifecycle rows. Regression-driven fallback restored all four to READY without remote calls.
- Actual READY evidence: all four had 60 positive P/E months; AAPL/NVDA/META/TSLA calculations each completed in about 2.5 seconds uncached. AAPL/NVDA/META/TSLA current P/E values were approximately 38.26/40.19/21.07/503.62 on stored evidence.
- Actual history evidence: all four had READY 1-year scenario history; META also had READY 3-year history, while missing 3/5-year warmup remained explicit rather than synthesized.
- Actual edge evidence: LCID returned NON_POSITIVE_EPS; RDDT returned 29-month and RIVN 57-month STRUCTURALLY_SHORT_LISTING; none exposed collection.
- Actual split evidence: NVDA stored 10:1 on 2024-06-10 and 4:1 on 2021-07-20, covered by the split-neutral calculation regression.
- Actual SEC-missing evidence: Visa returned COLLECTABLE with `sec_identity + sec_statements`; TSM initially exposed an ADR gap, then returned ADR_UNIT_UNVERIFIED after country-based share-unit hardening.
- Fresh focused individual-stock suite passed `35 tests` after identity, CIK-first collection, listing-duration, and foreign-issuer regressions.

## 5차 Browser QA

- Started the actual Streamlit app at `127.0.0.1:8509` and exercised the React component through browser automation.
- Desktop QA searched `AAPL`, selected `Apple Inc.`, and rendered current P/E `38.26x`, 60-month Graph 1, FOMC/company-growth Graph 2, and 1/3/5-year controls from stored DB evidence.
- Desktop horizontal overflow was false for both the outer document (`1345/1345`) and component iframe (`1174/1174`).
- 420px QA kept the outer document at `420/420` and component iframe at `377/377`, both with horizontal overflow false.
- Browser console reported `0` errors. The 3-year AAPL state now explains `positive PER 원자료 107개월` versus complete filing/SEP evaluation points `24/36개월` instead of showing a contradictory raw-month count.
- Representative 420px screenshot was moved outside the repository to `/tmp/market-context-us-stock-mobile-qa.png` and was not staged.

## 5차 Full Verification Evidence

- A single-process `unittest discover -s tests` collected 1,030 tests but produced Streamlit singleton cascades after test-local module replacement; this runner is not process-isolated.
- Re-ran all 23 `tests/test_*.py` modules in independent Python processes. All 1,030 tests executed: 1,026 passed and 4 unrelated existing contract assertions failed.
- The unrelated failures are two Practical Validation exact-call-string assertions that omit the current `source=source` argument, one Market Movers expected `rows_written=65` versus current `2`, and one Sentiment React source-token assertion for `payload.summary.metrics.map`.
- Market Context copy/history contract drift found by the full run was corrected; the five affected Market Context service-contract tests pass.
- Fresh component production build passed (`170 modules transformed`) and generated `component_static/assets/index-BOxsSxTV.js`.
