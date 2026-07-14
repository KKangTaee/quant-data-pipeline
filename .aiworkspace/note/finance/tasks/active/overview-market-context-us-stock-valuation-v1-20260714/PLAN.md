# Overview Market Context US Stock Valuation V1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:executing-plans` to implement this plan task-by-task in the current `codex/sub-dev` worktree. Do not create a new worktree and do not dispatch subagents.

Status: Implemented — 1차~5차 Complete
Last Updated: 2026-07-14

**Goal:** Market Context의 Nasdaq-100 사용자 화면을 DB 기반 미국 개별주식 검색·filing-aware 상대가치 화면으로 교체하면서 S&P 500 화면과 기존 Nasdaq 원천/collector를 보존한다.

**Architecture:** 선택 종목 하나의 bounded DB row를 loader가 읽고, pure calculator가 filing-aware quarterly TTM EPS·월말 PER·split-neutral 시계열·FOMC/기업 초과성장 시나리오를 계산한다. Overview service는 readiness와 JSON-safe read model을 만들고, React는 검색·수집 action·그래프·비적용 사유만 렌더링한다. 검색/렌더는 read-only이고 외부 호출은 사용자의 동기 `가치평가 자료 수집` action에만 둔다.

**Tech Stack:** Python 3, pandas, MySQL loader/query contracts, unittest/pytest, Streamlit component bridge, React 19, TypeScript, Vite.

## Global Constraints

- `DESIGN.md`가 authoritative specification이다.
- selector는 정확히 `S&P 500 | 미국 개별주식`이다.
- true FY Q4는 해당 filing의 실제 fiscal year-end fact에서만 파생한다. later filing의 comparative FY fact로 Q4를 만들지 않는다.
- split adjustment는 valuation 시점까지 발생한 split만 가격과 EPS 양쪽에 같은 share basis로 적용한다. future split을 과거 as-of 계산에 소급하지 않는다.
- 월별 EPS를 보간·합성하지 않고 `available_at <= month_end`인 최신 four discrete quarters만 합산한다.
- positive finite price와 positive TTM EPS에서만 P/E와 log(P/E)를 계산한다.
- Graph 1 official window는 60개월, sensitivity는 36개월이다.
- Graph 2는 FOMC real GDP + PCE macro proxy와 최근 3년 기업 quarterly TTM EPS 초과성장 P25/P50/P75를 결합한다.
- READY Graph 2에는 최소 8개 distinct positive-to-positive quarterly YoY observation과 applicable SEP vintage가 필요하다.
- price/SEC raw gap만 COLLECTABLE이다. 적자, 구조적으로 짧은 상장기간, per-share 불일치는 NOT_APPLICABLE이다.
- ETF, fund, preferred, warrant, unit, right는 검색 대상에서 제외한다. ADR은 per-share/ADR ratio 검증 전 NOT_APPLICABLE이다.
- V1에 새 valuation materialization table을 추가하지 않는다.
- `Ingestion -> DB -> Loader -> Service -> UI` 경계를 유지한다.
- S&P 500 service payload와 화면은 회귀시키지 않는다.
- 기존 Nasdaq DB, schema, collector, automation은 삭제하지 않고 사용자 화면 연결만 제거한다.
- `.aiworkspace/note/finance/researches/active/2026-07-market-interest-free-source-benchmark/`는 수정·stage·commit하지 않는다.
- screenshot, run history, 임시 파일은 commit하지 않는다.

## File Responsibility Map

- Modify `finance/data/nasdaq100_valuation.py`: shared SEC diluted-EPS quarter resolver correctness only.
- Create `finance/data/us_stock_valuation.py`: split-aware pure quarterly/monthly valuation, log multiple, excess-growth scenario, readiness primitives.
- Create `finance/loaders/us_stock_valuation.py`: current common-stock search, selected identity, bounded price/statement/SEP DB reads and gap summary.
- Create `app/services/overview/us_stock_valuation.py`: selected-symbol orchestration and JSON-safe UI read model.
- Modify `app/services/overview/market_context_valuation.py`: `nasdaq100` user-facing instrument을 `us_stock`으로 교체하고 S&P isolation 유지.
- Modify `app/jobs/ingestion_jobs.py`: selected-symbol exact-range price + SEC quarterly ingestion runner.
- Modify `app/jobs/overview_actions.py`: Overview synchronous action facade and rerun result contract.
- Modify `app/web/overview/market_context_helpers.py`: search/selection/action event bridge, nonce guard, cache clear/rerun.
- Modify `app/web/overview/market_context_react_component.py`: selected symbol/search query args와 component height/event contract.
- Modify `app/web/streamlit_components/market_context_valuation/src/MarketContextValuation.tsx`: stock selector, state cards, generic graph/scenario copy.
- Modify `app/web/streamlit_components/market_context_valuation/src/style.css`: search/results/state/responsive styles.
- Regenerate `app/web/streamlit_components/market_context_valuation/component_static/*`: verified Vite build output only.
- Modify `tests/test_nasdaq100_valuation.py`: real-like shared resolver and split regressions.
- Create `tests/test_us_stock_valuation.py`: pure calculator/loader/service/action tests.
- Modify `tests/test_market_context_valuation.py`: combined service, event bridge, React static contract, S&P isolation regression.
- Update active task docs, durable data/architecture/project docs, and root handoff logs in 5차.

---

## 1차 — 계산 정확도

### Task 1: True fiscal year-end Q4 resolver regression

**Files:**
- Modify: `tests/test_nasdaq100_valuation.py`
- Modify: `finance/data/nasdaq100_valuation.py`

**Interfaces:**
- Consumes: `derive_filing_aware_ttm_eps(statement_rows, as_of_date=...)` existing public function.
- Produces: same return schema, with `quarters[].derivation`, while comparative FY rows can never create Q4.

- [ ] **Step 1 RED:** Add `test_ttm_resolver_ignores_later_filing_comparative_fy_fact` using an AMZN-like 10-K fixture where a 2025 filing contains both the true FY 2024 fact (`period_end == report_date`) and comparative FY 2023 fact (`period_end != report_date`). Assert the 2023 comparative row is absent from derived quarters.
- [ ] **Step 2 RED:** Add `test_ttm_resolver_derives_q4_only_from_true_fiscal_year_end` using AAPL-like non-calendar fiscal year rows with Q1/Q2/Q3 plus FY and explicit `report_date`; assert Q4 equals `FY - Q1 - Q2 - Q3` exactly once.
- [ ] **Step 3 Verify RED:** Run `.venv/bin/python -m pytest tests/test_nasdaq100_valuation.py -k 'comparative_fy or true_fiscal_year_end' -q`; expected failure is the comparative FY row being treated as derivable or missing true-year-end predicate.
- [ ] **Step 4 GREEN:** Add a focused `_is_true_fiscal_year_end_fact(row)` predicate. Prefer `report_date == period_end`; for legacy normalized rows without report date, require a plausible first filing lag and reject FY facts whose `available_at - period_end` exceeds 180 days. Keep Q1/Q2/Q3 matching within the same fiscal year and use the FY filing availability for derived Q4.
- [ ] **Step 5 Verify GREEN:** Re-run the two tests, then `.venv/bin/python -m pytest tests/test_nasdaq100_valuation.py -q`.

### Task 2: Split-neutral price/EPS and monthly no-look-ahead contract

**Files:**
- Create: `finance/data/us_stock_valuation.py`
- Create: `tests/test_us_stock_valuation.py`
- Modify: `tests/test_nasdaq100_valuation.py` only if the shared resolver needs fixture coverage.

**Interfaces:**
- Produces `build_monthly_pit_valuation(statement_rows, price_rows, *, start_month, end_month) -> list[dict[str, Any]]`.
- Each point contains `month`, `price`, `price_basis_date`, `ttm_eps`, `eps_basis_date`, `trailing_pe`, `quarter_ends`, `split_factor`, `quality`.
- Produces `split_factor_between(price_rows, *, after, through) -> float` using positive `stock_splits` events only.

- [ ] **Step 1 RED:** Add an NVDA-like 10-for-1 fixture with pre-split raw close/EPS and post-split raw close/restated EPS. Assert adjacent monthly P/E does not jump approximately 10x and pre-split as-of does not use the later split.
- [ ] **Step 2 RED:** Add `test_monthly_ttm_carries_forward_without_interpolation` with two months between filings; assert identical TTM EPS and distinct month-end prices.
- [ ] **Step 3 RED:** Add `test_monthly_ttm_does_not_use_future_filing` where a high EPS filing is available one day after month-end; assert the prior month retains the old four-quarter sum.
- [ ] **Step 4 RED:** Add zero/negative EPS and missing-month fixtures; assert `trailing_pe is None` and no substitute month is created.
- [ ] **Step 5 Verify RED:** Run `.venv/bin/python -m pytest tests/test_us_stock_valuation.py -k 'split or carry or future or non_positive' -q`; expected import failure for the new module.
- [ ] **Step 6 GREEN:** Implement pure date normalization, actual month-end trading row selection, as-of resolver calls, per-quarter split normalization through each observation month, positive-only P/E, and explicit missingness. Do not read DB or providers.
- [ ] **Step 7 Verify GREEN:** Re-run focused tests and `.venv/bin/python -m pytest tests/test_nasdaq100_valuation.py tests/test_us_stock_valuation.py -q`.
- [ ] **Step 8 Commit:** Stage only the resolver/calculator/tests and commit `개별주 TTM과 분할 계산 정확도 보강`.

**1차 완료 조건:** comparative FY, true Q4, split, carry-forward, `available_at` no-look-ahead fixtures가 모두 통과하고 기존 S&P/Nasdaq focused tests가 통과한다.

## 2차 — 개별주 가치평가 엔진

### Task 3: Bounded selected-symbol loader

**Files:**
- Create: `finance/loaders/us_stock_valuation.py`
- Modify: `tests/test_us_stock_valuation.py`

**Interfaces:**
- Produces `load_us_stock_identity(symbol, *, query_fn=None) -> dict[str, Any] | None`.
- Produces `load_us_stock_valuation_inputs(symbol, *, as_of_date=None, valuation_months=119, statement_lookback_months=18, query_fn=None) -> dict[str, Any]`.
- Returned keys: `identity`, `price_rows`, `statement_rows`, `sep_rows`, `window`, `coverage`.

- [ ] **Step 1 RED:** Assert identity SQL is parameterized, requires current active `kind=stock`, and chooses deterministic SEC CIK/exchange evidence.
- [ ] **Step 2 RED:** Assert price query is one symbol, `timeframe='1d'`, bounded to 119 months, and selects raw `close`, `adj_close`, `stock_splits` without changing table schema.
- [ ] **Step 3 RED:** Assert statement query is one symbol, diluted-EPS concepts only, `available_at <= as_of`, and includes the extra 18-month construction lookback without exposing it as valuation history.
- [ ] **Step 4 RED:** Assert SEP query preserves all bounded release vintages required for historical as-of matching.
- [ ] **Step 5 Verify RED:** Run `.venv/bin/python -m pytest tests/test_us_stock_valuation.py -k loader -q`; expected import/attribute failures.
- [ ] **Step 6 GREEN:** Implement three database-group queries with injected query seam for tests, strict uppercase symbol normalization, and JSON-safe date normalization at the service boundary rather than silently widening windows.
- [ ] **Step 7 Verify GREEN:** Re-run loader tests.

### Task 4: Graph 1, Graph 2, historical scenarios, readiness

**Files:**
- Modify: `finance/data/us_stock_valuation.py`
- Modify: `tests/test_us_stock_valuation.py`

**Interfaces:**
- Produces `calculate_stock_multiple_regime(monthly_rows, *, official_window=60, sensitivity_window=36) -> dict[str, Any]`.
- Produces `calculate_company_excess_growth(quarterly_ttm_rows, sep_rows, *, as_of_date) -> dict[str, Any]`.
- Produces `calculate_stock_scenarios(current_ttm_eps, multiple_regime, excess_growth) -> dict[str, Any]`.
- Produces `calculate_historical_stock_scenario(monthly_rows, quarterly_ttm_rows, sep_rows, *, visible_months) -> dict[str, Any]`.
- Produces `classify_us_stock_readiness(identity, coverage, monthly_rows, growth_evidence) -> dict[str, Any]`.

- [ ] **Step 1 RED:** Assert Graph 1 rejects 59 complete positive months, accepts exactly 60, uses log(P/E), and reports 36-month sensitivity separately.
- [ ] **Step 2 RED:** Assert current negative/zero TTM EPS is NOT_APPLICABLE and no log/price scenario exists.
- [ ] **Step 3 RED:** Build 12 quarterly TTM observations and SEP vintages; assert each growth observation uses only `release_date <= observation available_at`, then Tukey-clips and returns deterministic P25/P50/P75.
- [ ] **Step 4 RED:** Assert fewer than 8 positive-to-positive YoY observations blocks Graph 2 without inventing observations.
- [ ] **Step 5 RED:** Assert conservative/baseline/optimistic growth equals current macro plus P25/P50/P75 excess and prices use `-1σ / center / +1σ` multiples; non-positive projected EPS has no price.
- [ ] **Step 6 RED:** Assert 1y/3y/5y historical results require exactly 12/36/60 complete visible points and each point recalculates with only historical filing and SEP evidence.
- [ ] **Step 7 RED:** Cover READY, COLLECTABLE price gap, COLLECTABLE SEC gap, NOT_APPLICABLE short listing, NOT_APPLICABLE ADR/unit, and ERROR schema mismatch.
- [ ] **Step 8 Verify RED:** Run `.venv/bin/python -m pytest tests/test_us_stock_valuation.py -k 'multiple or excess or scenario or readiness or history' -q`.
- [ ] **Step 9 GREEN:** Implement the minimal pure functions, reusing statistical semantics from the S&P service where behavior is identical but keeping company EPS/PIT logic in the new data module.
- [ ] **Step 10 Verify GREEN:** Re-run all pure tests.

### Task 5: Selected-stock service read model

**Files:**
- Create: `app/services/overview/us_stock_valuation.py`
- Modify: `tests/test_us_stock_valuation.py`

**Interfaces:**
- Produces `build_us_stock_valuation_read_model(*, selected_symbol=None, loaded_inputs=None) -> dict[str, Any]`.
- Payload keys: `schema_version`, `status`, `instrument`, `search`, `selection`, `readiness`, `multiple_regime`, `earnings_scenario`, `index_scenario`, `collection_action`, `sources`, `limitations`.

- [ ] **Step 1 RED:** Assert no selected symbol returns NOT_SELECTED without invoking the loader.
- [ ] **Step 2 RED:** Assert READY payload exposes price date, EPS basis date, formula evidence, Graph 1/2, and 1y/3y/5y history in JSON-safe primitives.
- [ ] **Step 3 RED:** Assert COLLECTABLE exposes exact price/SEC missing ranges and one `collect_us_stock_valuation` action; NOT_APPLICABLE never exposes it.
- [ ] **Step 4 RED:** Assert errors become ERROR with stable last-screen/S&P isolation compatible shape.
- [ ] **Step 5 Verify RED:** Run `.venv/bin/python -m pytest tests/test_us_stock_valuation.py -k service -q`.
- [ ] **Step 6 GREEN:** Implement service orchestration and Korean product copy using `상대가치 시나리오`, never `공식 적정가/목표주가/매매 신호`.
- [ ] **Step 7 Verify GREEN:** Re-run service tests and commit `미국 개별주 상대가치 엔진 추가`.

**2차 완료 조건:** selected-symbol bounded loader와 pure/service 엔진이 READY·적자·신규상장·raw gap·outlier를 구분하고 60/36 및 FOMC/기업 초과성장 계약을 통과한다.

## 3차 — 검색·수집

### Task 6: Current U.S. common-stock DB search

**Files:**
- Modify: `finance/loaders/us_stock_valuation.py`
- Modify: `app/services/overview/us_stock_valuation.py`
- Modify: `tests/test_us_stock_valuation.py`

**Interfaces:**
- Produces `search_us_common_stocks(query, *, limit=12, query_fn=None) -> list[dict[str, Any]]`.
- Result keys: `symbol`, `name`, `exchange`, `cik`, `instrument_type`, `adr_unit_status`.

- [ ] **Step 1 RED:** Assert empty/one-character queries return no rows and never call a provider.
- [ ] **Step 2 RED:** Assert ticker-prefix ranks ahead of name substring and output is deterministic.
- [ ] **Step 3 RED:** Assert inactive/delisted, ETF/fund/preferred/warrant/unit/right rows are excluded; NYSE/Nasdaq/NYSE American common stocks with CIK remain.
- [ ] **Step 4 GREEN:** Implement a parameterized lifecycle/current-profile query and defensive evidence parsing, limited to 12 results.
- [ ] **Step 5 Verify GREEN:** Run search tests.

### Task 7: Missing-range preflight and synchronous selected-symbol collection

**Files:**
- Modify: `finance/loaders/us_stock_valuation.py`
- Modify: `app/jobs/ingestion_jobs.py`
- Modify: `app/jobs/overview_actions.py`
- Modify: `tests/test_us_stock_valuation.py`

**Interfaces:**
- Produces `build_us_stock_valuation_collection_plan(symbol, *, as_of_date=None) -> dict[str, Any]`.
- Produces `run_collect_us_stock_valuation_inputs(symbol, *, price_start, price_end, collect_prices, collect_statements, progress_callback=None) -> JobResult`.
- Produces `run_overview_us_stock_valuation_collection(...) -> JobResult`.

- [ ] **Step 1 RED:** Assert preflight distinguishes exact price range, SEC statement gap, and structural listing-age gap.
- [ ] **Step 2 RED:** Assert runner calls canonical `run_collect_ohlcv([symbol], start, provider-exclusive-end, interval='1d')` and `run_collect_financial_statements([symbol], freq='quarterly', periods=0, period='quarterly')` only for requested missing scopes.
- [ ] **Step 3 RED:** Assert rerun after partial success narrows plan; already satisfied scopes are skipped; stable DB UPSERT writers make retry idempotent.
- [ ] **Step 4 RED:** Assert NOT_APPLICABLE plan cannot enter the collector and invalid symbol/CIK mismatch fails closed.
- [ ] **Step 5 RED:** Assert progress reports `preflight -> prices -> sec -> complete` synchronously and result retains partial successes.
- [ ] **Step 6 Verify RED:** Run `.venv/bin/python -m pytest tests/test_us_stock_valuation.py -k 'preflight or collection or idempotent' -q`.
- [ ] **Step 7 GREEN:** Implement the one-symbol runner/facade with injected seams, exact scopes, no new table, and partial-success result.
- [ ] **Step 8 Verify GREEN:** Re-run all stock tests and commit `개별주 검색과 동기 자료수집 연결`.

**3차 완료 조건:** 검색은 DB-only이며 explicit action만 외부 수집기를 호출하고, partial success/retry가 동일 business key를 안전하게 재사용한다.

## 4차 — UI 교체

### Task 8: Combined service and Streamlit event bridge

**Files:**
- Modify: `app/services/overview/market_context_valuation.py`
- Modify: `app/web/overview/market_context_helpers.py`
- Modify: `app/web/overview/market_context_react_component.py`
- Modify: `tests/test_market_context_valuation.py`

**Interfaces:**
- Combined payload becomes `market_context_valuation_v3` with instruments `sp500`, `us_stock`.
- Component events: `search_us_stock`, `select_us_stock`, `collect_us_stock_valuation`; collection includes symbol and nonce.

- [ ] **Step 1 RED:** Assert combined model keys are exactly `sp500/us_stock`, default remains `sp500`, and stock failure cannot alter the S&P payload.
- [ ] **Step 2 RED:** Assert search/selection events only update session-backed query/symbol and rerun; no ingestion runner is called.
- [ ] **Step 3 RED:** Assert collection event validates selected symbol, consumes each nonce once, waits synchronously, stores result, clears valuation/search cache, and reruns.
- [ ] **Step 4 RED:** Assert old Nasdaq repair IDs are no longer handled by Market Context UI while Nasdaq job functions remain importable.
- [ ] **Step 5 GREEN:** Implement isolated stock builder and generic event bridge, preserving fallback rendering for S&P.
- [ ] **Step 6 Verify GREEN:** Run `.venv/bin/python -m pytest tests/test_market_context_valuation.py -q`.

### Task 9: React search, readiness states, generic charts, responsive layout

**Files:**
- Modify: `app/web/streamlit_components/market_context_valuation/src/MarketContextValuation.tsx`
- Modify: `app/web/streamlit_components/market_context_valuation/src/style.css`
- Modify: `tests/test_market_context_valuation.py`
- Regenerate: `app/web/streamlit_components/market_context_valuation/component_static/*`

**Interfaces:**
- Selector labels: `S&P 500`, `미국 개별주식`.
- Stock flow: query input -> result buttons -> selected summary -> READY or actionable/non-actionable state.

- [ ] **Step 1 RED:** Update static contract test to require stock selector/search/result/status tokens and forbid user-facing `Nasdaq-100`, `QQQ`, Nasdaq coverage/repair copy.
- [ ] **Step 2 RED:** Require READY summary tokens `현재 TTM EPS`, `FOMC 거시 기준`, `기업 초과성장`, `예상 EPS`, plus 1년/3년/5년 history controls.
- [ ] **Step 3 RED:** Require COLLECTABLE button only when `collection_action.enabled`, NOT_APPLICABLE reason without button, and ERROR/NOT_SELECTED accessible states.
- [ ] **Step 4 GREEN:** Generalize title/copy from index-only to instrument-aware relative value, add controlled search selection and synchronous pending/retry behavior.
- [ ] **Step 5 GREEN:** Add desktop/mobile CSS with min-width-safe grid, wrapping selectors/results, and 420px single-column states.
- [ ] **Step 6 Verify GREEN:** Run Python static tests, then `npm run build` in the component directory; expected exit 0 with regenerated static assets.
- [ ] **Step 7 Verify S&P:** Run `.venv/bin/python -m pytest tests/test_sp500_valuation.py tests/test_market_context_valuation.py -q`.
- [ ] **Step 8 Commit:** Stage service/bridge/React/static/test files only and commit `Market Context를 미국 개별주 화면으로 교체`.

**4차 완료 조건:** 사용자-facing Nasdaq copy/action이 사라지고 모든 stock readiness state와 history가 렌더되며 S&P service/UI regression이 없다.

## 5차 — QA·문서·커밋

### Task 10: Actual DB matrix, Browser QA, documentation closeout

**Files:**
- Modify: active task `STATUS.md`, `NOTES.md`, `RISKS.md`, `RUNS.md`
- Modify as needed: `.aiworkspace/note/finance/docs/INDEX.md`, `ROADMAP.md`, `PROJECT_MAP.md`, `data/README.md`, `data/TABLE_SEMANTICS.md`, `architecture/DATA_DB_PIPELINE_FLOW.md`
- Modify: `.aiworkspace/note/finance/WORK_PROGRESS.md`, `.aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md`
- Screenshot: outside the repository or ignored generated location; never stage.

- [ ] **Step 1 Actual DB:** Run read-only AAPL/NVDA/META/TSLA service smoke and record status, complete months, current price date, EPS basis date, Graph 2 observation count, and latency. Do not fabricate READY if local DB evidence is insufficient.
- [ ] **Step 2 Edge cases:** Validate at least one negative-EPS, recent-IPO/short-history, split, and SEC-gap fixture/DB case; record READY/COLLECTABLE/NOT_APPLICABLE reason.
- [ ] **Step 3 Focused fresh verification:** Run the three valuation test files plus job/helper-focused tests selected by changed imports.
- [ ] **Step 4 Full regression:** Run the repository's available full Python regression command; if environment/time blocks it, record the exact command, failure, and narrower passing evidence.
- [ ] **Step 5 Frontend:** Run fresh `npm run build`; inspect generated diff and ensure no source map/temp artifact is staged.
- [ ] **Step 6 Browser skill:** Use `browser:control-in-app-browser` to run the actual app at desktop and 420px. Verify S&P and U.S. stock flows, keyboard search, status cards, pending/retry, console errors, and horizontal overflow.
- [ ] **Step 7 Screenshot:** Capture one representative QA screenshot outside staged files and include its absolute path in the final response.
- [ ] **Step 8 Docs:** Apply `finance-doc-sync`; promote only durable contracts, update task/root handoff in compact form, and leave actual run detail in `RUNS.md`.
- [ ] **Step 9 Review:** Apply `finance-integration-review` to the complete diff, verify the unrelated research folder is untouched, then apply `superpowers:requesting-code-review` without spawning subagents by performing the prescribed self-review gate.
- [ ] **Step 10 Fresh completion gate:** Apply `superpowers:verification-before-completion`; run `git status --short`, `git diff --check`, focused/full tests, build, and staged-path audit after the final edits.
- [ ] **Step 11 Final commit:** Commit remaining coherent docs/QA alignment with Korean message `개별주 가치평가 QA와 문서 정렬`; do not amend earlier units.

**5차 완료 조건:** actual/fixture evidence, full available regression, React build, desktop/420px Browser QA, screenshot, docs/root handoff, staged-path audit, and coherent commits are complete.

## Plan Self-Review

- Spec coverage: 1차~5차, true FY, split, PIT, search, collection, UI, S&P regression, actual/edge QA, docs, commits가 각 task에 매핑됐다.
- Placeholder scan: 실행을 미루는 TBD/TODO가 없다. 환경 의존 full regression/actual DB는 실패 시에도 exact evidence를 기록하도록 정의했다.
- Type consistency: `selected_symbol`, `identity`, `monthly_rows`, `multiple_regime`, `earnings_scenario`, `index_scenario`, `collection_action`이 loader→service→combined payload→React에서 동일한 이름으로 연결된다.
- Scope check: 새 materialization table, Nasdaq raw cleanup, analyst consensus, DCF/P/FFO는 포함하지 않는다.

## 2026-07-15 Correctness Follow-up TDD Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:executing-plans` inline in the current `codex/sub-dev` worktree. Do not create a new worktree or dispatch subagents.

**Goal:** comparative quarter fiscal-context drift와 split-year FY→Q4 단위 혼합을 수정하고, Graph 2 evidence 부족이 READY Graph 1을 숨기지 않게 한다.

**Architecture:** shared SEC resolver는 primary filing-period fact만 discrete quarter identity로 사용한다. Individual-stock monthly calculator는 각 month-end까지 공개된 statement fact를 그 month-end share basis로 정규화한 뒤 resolver를 호출한다. Top-level readiness는 P/E 화면 가능 여부를 소유하고 company-growth evidence는 Graph 2 section status로 분리한다.

**Tech Stack:** Python 3.12, pandas, unittest, React/TypeScript static contract, Streamlit Browser QA.

### Global Constraints

- `available_at` 이후에만 filing/restatement를 사용한다.
- split date 이전 month에 future split을 소급하지 않는다.
- missing/negative EPS를 합성하거나 positive P/E로 바꾸지 않는다.
- DB schema, raw rows, collector, S&P, retained Nasdaq backend를 보존한다.
- unrelated research folder와 generated QA artifact를 stage하지 않는다.

### Task 11: Comparative Q fiscal-period identity

**Files:**
- Modify: `tests/test_nasdaq100_valuation.py`
- Modify: `finance/data/nasdaq100_valuation.py`

**Interfaces:**
- Consumes: SEC duration EPS rows with `period_end`, `report_date`, `available_at`, `fiscal_year`, `fiscal_quarter`.
- Produces: `derive_filing_aware_ttm_eps(...)->quarters[]` where later comparative Q/FY facts cannot replace the primary reported period.

- [ ] Add an AMD-like failing regression containing a true FY2023 fact, reported Q1/Q2/Q3, an older comparative Q1 carrying fiscal-year context, and a later Q1 comparative row. Assert the FY2023 Q4 remains `0.42` before and after the later filing.

```python
before = derive_filing_aware_ttm_eps(rows, as_of_date="2024-01-31")
after = derive_filing_aware_ttm_eps(rows, as_of_date="2024-05-31")
self.assertAlmostEqual(before["AMD"]["quarters"][-1]["eps"], 0.42)
self.assertAlmostEqual(after["AMD"]["quarters"][-1]["eps"], 0.42)
```

- [ ] Run the exact test and confirm RED because current Q4 changes to `-0.23`.

```bash
.venv/bin/python -m unittest tests.test_nasdaq100_valuation.Nasdaq100ValuationCoverageTests.test_ttm_resolver_keeps_q4_stable_when_later_filing_repeats_comparative_quarter
```

- [ ] Generalize the true-period predicate to Q and FY. Prefer `report_date == period_end`; keep the bounded 180-day fallback only when report date is absent.

```python
quarter_rows = quarter_rows.loc[
    [_is_primary_filing_period_fact(row) for row in quarter_rows.itertuples()]
]
fy_rows = fy_rows.loc[
    [_is_primary_filing_period_fact(row) for row in fy_rows.itertuples()]
]
```

- [ ] Re-run the regression and full Nasdaq valuation tests; expected GREEN with existing non-calendar FY behavior retained.
- [ ] Commit the resolver unit with Korean message `comparative 분기 TTM 귀속 오류 수정`.

### Task 12: Split-normalized FY-derived Q4

**Files:**
- Modify: `tests/test_us_stock_valuation.py`
- Modify: `finance/data/us_stock_valuation.py`

**Interfaces:**
- Consumes: raw statement `value/available_at` plus price split rows.
- Produces: month-end TTM quarters whose direct Q and FY-derived Q4 are on the same share basis before summation.

- [ ] Add an NVDA-like failing fixture with Q1 `5.98` before a 10:1 split, Q2 `0.67`, Q3 `0.78`, FY `2.94`; assert Q4 `0.892` and TTM `2.94` at FY availability.

```python
row = build_monthly_pit_valuation(
    statements,
    prices,
    start_month="2025-02-01",
    end_month="2025-02-28",
)[0]
self.assertAlmostEqual(row["quarters"][-1]["eps"], 0.892)
self.assertAlmostEqual(row["ttm_eps"], 2.94)
```

- [ ] Assert a month before the split does not use the future 10:1 factor.

```python
self.assertAlmostEqual(pre_split_row["split_factor"], 1.0)
self.assertAlmostEqual(post_split_row["split_factor"], 10.0)
```

- [ ] Run the exact test and confirm RED because current resolver derives Q4 before share-basis normalization.

```bash
.venv/bin/python -m unittest tests.test_us_stock_valuation.UsStockValuationCalculationTests.test_split_year_normalizes_quarters_before_deriving_q4
```

- [ ] Normalize every eligible statement fact to the valuation month-end share basis before resolving discrete quarters; remove the later double adjustment of resolved quarters.

```python
normalized_statements = [
    {
        **row,
        "value": float(row["value"])
        / split_factor_between(prices, after=str(row["available_at"]), through=month_end),
    }
    for row in statements
]
resolved = derive_filing_aware_ttm_eps(
    normalized_statements,
    as_of_date=month_end.strftime("%Y-%m-%d"),
)
```

- [ ] Re-run U.S. stock calculation tests plus the resolver suite; expected GREEN for split/no-look-ahead/carry-forward cases.
- [ ] Commit with Korean message `분할 연도 FY와 분기 EPS 단위 일치`.

### Task 13: Graph 1 and Graph 2 readiness isolation

**Files:**
- Modify: `tests/test_us_stock_valuation.py`
- Modify: `finance/data/us_stock_valuation.py`
- Modify: `app/services/overview/us_stock_valuation.py`
- Modify as needed: `tests/test_service_contracts.py`

**Interfaces:**
- Top-level `status=READY` means the selected stock's Graph 1 P/E screen is renderable.
- `earnings_scenario.status` and `index_scenario.status` independently return `BLOCKED` with `INSUFFICIENT_GROWTH_HISTORY` and exact `observation_count/required_observations` evidence.

- [ ] Add a failing classifier test: 60 complete positive P/E months plus 7/8 growth observations returns top-level READY.

```python
result = classify_us_stock_readiness(
    identity,
    complete_coverage,
    ready_rows,
    {"status": "INSUFFICIENT_HISTORY", "observation_count": 7},
)
self.assertEqual(result["status"], "READY")
```

- [ ] Add a failing service test: the same input keeps `multiple_regime.status=READY`, while earnings/index scenarios are BLOCKED and contain `7/8` evidence.

```python
self.assertEqual(result["status"], "READY")
self.assertEqual(result["multiple_regime"]["status"], "READY")
self.assertEqual(result["earnings_scenario"]["status"], "BLOCKED")
self.assertEqual(result["earnings_scenario"]["observation_count"], 7)
self.assertEqual(result["earnings_scenario"]["required_observations"], 8)
self.assertEqual(result["index_scenario"]["status"], "BLOCKED")
```

- [ ] Run both tests and confirm RED because current classifier/service returns whole-model NOT_APPLICABLE.
- [ ] Remove growth from intrinsic P/E applicability, preserve section-specific reason/evidence, and keep COLLECTABLE/NOT_APPLICABLE action rules unchanged.
- [ ] Re-run U.S. stock, combined Market Context, S&P, and static UI contract tests.
- [ ] Commit with Korean message `개별주 그래프별 준비 상태 분리`.

### Task 14: Actual DB, Browser, docs, final verification

**Files:**
- Modify: active task `STATUS.md`, `NOTES.md`, `RISKS.md`, `RUNS.md`
- Modify if stale: `docs/data/TABLE_SEMANTICS.md`, `docs/architecture/DATA_DB_PIPELINE_FLOW.md`, `docs/INDEX.md`, `docs/ROADMAP.md`
- Modify: `WORK_PROGRESS.md`, `QUESTION_AND_ANALYSIS_LOG.md`

- [ ] Run AMD/AAPL/MSFT/NVDA/META/TSLA read-only actual DB comparison; record latest TTM, P/E, growth observation count, and section statuses.

```bash
.venv/bin/python -m unittest tests.test_us_stock_valuation tests.test_nasdaq100_valuation tests.test_market_context_valuation tests.test_sp500_valuation
```

- [ ] Verify AMD Q4 stability and NVDA split-year identity with exact stored facts; verify current non-positive EPS remains NOT_APPLICABLE.
- [ ] Run focused valuation/service tests, independent full regression, Python compile, `git diff --check`, and React production build.

```bash
.venv/bin/python -m py_compile finance/data/nasdaq100_valuation.py finance/data/us_stock_valuation.py app/services/overview/us_stock_valuation.py
npm run build --prefix app/web/streamlit_components/market_context_valuation
git diff --check
```
- [ ] Run actual Streamlit desktop and 420px Browser QA. Confirm AMD Graph 1 renders, Graph 2 section status is accurate, S&P remains unchanged, console errors are zero, and horizontal overflow is absent.
- [ ] Store one screenshot outside the repository and include it in the final report.
- [ ] Apply `finance-doc-sync`, audit staged paths, leave the unrelated research folder untouched, and create the final Korean closeout commit.

### Follow-up Plan Self-Review

- Spec coverage: comparative Q, split-before-Q4, no-look-ahead, section isolation, actual symbols, S&P/Nasdaq preservation, Browser QA, docs, commits are mapped.
- Placeholder scan: no TBD/TODO or unspecified implementation step remains.
- Type consistency: existing `status`, `readiness`, `multiple_regime`, `earnings_scenario`, and `index_scenario` keys are retained; no new DB/materialization contract is introduced.
- Scope check: no blanket comparative-row deletion, provider fetch on read, schema migration, raw backfill, or unrelated valuation metric is included.
