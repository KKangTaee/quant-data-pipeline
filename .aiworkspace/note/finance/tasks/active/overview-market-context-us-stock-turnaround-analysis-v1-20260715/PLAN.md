# Overview Market Context US Stock Turnaround Analysis V1 Implementation Plan

Status: Approved Implementation Plan
Last Updated: 2026-07-15

> **For agentic workers:** REQUIRED SUB-SKILL: use `superpowers:executing-plans` for inline execution. Every feature/bugfix task below follows RED -> GREEN -> regression and ends with focused verification plus a coherent Korean commit.

**Goal:** 현재 미국 개별주식 선택 흐름 안에 `PER 상대가치 | 전환 분석`을 추가하고, P/E가 성립하지 않는 기업도 filing-aware discrete-quarter 근거로 영업·현금 전환과 survival/valuation readiness를 분석한다.

**Architecture:** 기존 `Ingestion -> DB -> Loader -> Service -> Streamlit event bridge -> React` 경계를 그대로 확장한다. 새 pure calculator가 SEC duration/instant fact를 분리해 discrete quarter와 TTM을 만들고, selected-symbol loader/service가 이를 JSON-safe read model로 조립하며, 기존 PER payload에는 `turnaround_analysis`와 `recommended_analysis`만 추가해 S&P/PER 계약을 보존한다.

**Tech Stack:** Python 3, pandas, MySQL raw ledger, unittest, Streamlit custom component, React 18, TypeScript, Vite.

## 이걸 하는 이유?

현재 PER 화면은 negative/zero EPS를 올바르게 제외하지만, 적자·전환기업을 선택한 사용자가 같은 종목 흐름에서 매출, margin, OCF/FCF, cash runway, debt/interest, dilution을 판단할 수 없다. 이 계획은 negative P/E를 꾸며내지 않고 실제 quarterly filing evidence로 그 빈틈을 채운다.

## Global Constraints

- authoritative specification은 같은 task의 `DESIGN.md`다.
- 새 worktree/branch/schema/materialization table을 만들지 않는다.
- unrelated untracked `researches/active/2026-07-market-interest-free-source-benchmark/`는 수정·stage·commit하지 않는다.
- 화면 진입, 검색, 분석 selector 전환은 DB read-only이며 provider 호출은 명시적인 selected-symbol 수집 action에서만 허용한다.
- missing quarter는 원래 시간축 slot에 남기고 보간·연결·대체하지 않는다.
- future filing/restatement/split을 과거 point에 소급하지 않는다.
- target price, peer-relative fair value, buy/sell signal을 만들지 않는다.
- generated build output은 제품 component static bundle만 기존 정책대로 포함하고, screenshot/run history/temp artifact는 commit하지 않는다.

## File Ownership Map

- Create `finance/data/us_stock_turnaround.py`: raw fact normalization, discrete-quarter resolver, TTM series, milestone/risk/valuation pure logic.
- Create `finance/loaders/us_stock_turnaround.py`: one-symbol/7-fiscal-year bounded DB reads and exact collection preflight.
- Create `app/services/overview/us_stock_turnaround.py`: JSON-safe turnaround read model and section readiness.
- Modify `finance/data/asset_profile.py`: optional selected-symbol profile collection without changing default broad collection behavior.
- Modify `app/jobs/ingestion_jobs.py`: validated selected-symbol `asset_profile/prices/sec_statements` synchronous collector.
- Modify `app/jobs/overview_actions.py`: turnaround preflight, partial-success preservation, retry-scope narrowing.
- Modify `app/services/overview/market_context_valuation.py`: independently isolate PER and turnaround and attach recommended analysis without changing S&P payload.
- Modify `app/web/overview/market_context_helpers.py`: consume explicit turnaround collection event and preserve DB-only selector switching.
- Create `app/web/streamlit_components/market_context_valuation/src/TurnaroundAnalysis.tsx`: milestone rail, two charts, risk/valuation cards.
- Modify `app/web/streamlit_components/market_context_valuation/src/MarketContextValuation.tsx`: inner selector/default routing and existing PER handoff.
- Modify `app/web/streamlit_components/market_context_valuation/src/style.css`: desktop/420px analysis layout and color-independent statuses.
- Create `tests/test_us_stock_turnaround.py`: pure resolver/engine/loader/service/collection tests.
- Modify `tests/test_market_context_valuation.py`: combined-service, event, React source contracts and S&P/PER regression.
- Modify task/docs/root handoff files only after implementation evidence exists.

---

## 1차 — 분기 계산 정확도

### Task 1.1: Real-like raw fact fixtures and direct/cumulative resolver

**Files:** Create `tests/test_us_stock_turnaround.py`; Create `finance/data/us_stock_turnaround.py`.

**Interfaces:**

```python
def resolve_discrete_quarters(
    statement_rows: Iterable[Mapping[str, Any]],
    *,
    metric: str,
    concepts: Sequence[str],
    units: Collection[str],
    as_of_date: str,
) -> list[dict[str, Any]]:
    """Return primary-period direct/derived quarters with provenance and no look-ahead."""
```

Each resolved row exposes `symbol`, `metric`, `concept`, `unit`, `fiscal_year`, `fiscal_quarter`, `period_start`, `period_end`, `value`, `available_at`, `accession_no`, `derivation`, and `provenance`.

- [x] Write LCID/RIVN/PLTR/AAPL-like failing tests for direct Q, `H1-Q1`, `9M-H1`, and `FY-Q1-Q2-Q3`.
- [x] Assert later comparative facts cannot replace the original primary quarter and every derived `available_at` equals the latest operand date.
- [x] Assert concept/unit/fiscal-year mismatch and a missing operand leave the target quarter missing.
- [x] Run `.venv/bin/python -m unittest tests.test_us_stock_turnaround.TurnaroundQuarterResolverTests -v`; expect import/assertion failures.
- [x] Implement duration classification from `period_start/period_end`, primary-period ownership from `report_date/period_end`, ordered concept priority, deterministic dedupe, and provenance.
- [x] Re-run the resolver class; expect PASS.

### Task 1.2: Instant separation and split-neutral diluted shares

**Interfaces:**

```python
def resolve_instant_facts(
    statement_rows: Iterable[Mapping[str, Any]],
    *,
    metric: str,
    concepts: Sequence[str],
    units: Collection[str],
    as_of_date: str,
) -> list[dict[str, Any]]: ...

def build_split_neutral_share_series(
    quarter_rows: Iterable[Mapping[str, Any]],
    price_rows: Iterable[Mapping[str, Any]],
    *,
    as_of_date: str,
) -> list[dict[str, Any]]: ...
```

- [x] Write failing tests that duration rows never enter instant facts, instant rows never enter quarter arithmetic, and a future split/restatement cannot change an earlier as-of result.
- [x] Assert split-adjusted diluted-share basis is unchanged by a pure stock split; 5%/10% risk classification remains in Task 2.2.
- [x] Run the two focused tests; expect RED.
- [x] Implement PIT cutoff filters and reuse the existing split-factor semantics without applying splits after `as_of_date`.
- [x] Run the full turnaround test file plus `tests.test_us_stock_valuation.UsStockValuationCalculationTests`; expect PASS.
- [x] Update `STATUS.md`/`RUNS.md` with 1차 evidence and commit `전환 분석 분기 계산 정확도 구현`.

**1차 완료 조건:** fake quarter, comparative overwrite, future filing/restatement/split, instant/duration mixing이 모두 test로 차단되고 real-like fixtures가 deterministic discrete quarter를 만든다.

---

## 2차 — 전환 분석 엔진

### Task 2.1: Canonical metric families and quarterly/TTM series

**Files:** Modify `finance/data/us_stock_turnaround.py`; Modify `tests/test_us_stock_turnaround.py`.

**Interfaces:**

```python
TURNAROUND_CONCEPT_FAMILIES: dict[str, tuple[str, ...]]

def build_turnaround_quarterly_series(
    statement_rows: Iterable[Mapping[str, Any]],
    price_rows: Iterable[Mapping[str, Any]],
    *,
    as_of_date: str,
) -> dict[str, Any]: ...
```

The result contains full calendar-quarter `timeline`, valid metric `series`, per-quarter raw/TTM values, `available_at`, provenance, and metric-level missing reasons.

- [x] Write failing tests for revenue, direct/derived gross profit, operating income, net income, OCF, positive CapEx magnitude, FCF proxy, EPS, and diluted shares.
- [x] Assert gross profit fallback uses same-quarter/same-unit compatible revenue-cost only; assert TTM margins sum numerator/denominator before division.
- [x] Assert a missing quarter remains a `MISSING` timeline slot and breaks TTM rather than borrowing another quarter.
- [x] Implement ordered canonical families and TTM/YoY helpers; run focused tests to GREEN.

### Task 2.2: Milestones and independent risk overlays

**Interfaces:**

```python
def classify_turnaround_milestones(series: Mapping[str, Any], *, per_status: str) -> dict[str, Any]: ...
def evaluate_turnaround_risks(series: Mapping[str, Any]) -> dict[str, Any]: ...
```

- [x] Write failing tests for `LOSS_BASELINE`, `OPERATING_IMPROVEMENT`, two-consecutive-TTM `CASH_FLOW_TURN`, `EARNINGS_TURN`, `PER_CANDIDATE`, and `PER_READY`.
- [x] Assert milestone statuses are independent: earnings turn does not pass cash-flow turn, burn improvement is not cash-flow turn, quarterly EPS turn is not positive TTM EPS.
- [x] Write failing tests for runway 4/8-quarter boundaries, interest coverage meaningfulness, net debt with negative OCF, and 5%/10% split-neutral dilution.
- [x] Implement raw deltas plus 1.0pp/2-of-3 rules and independent overlays; run tests to GREEN.

### Task 2.3: Fresh-input valuation router and section readiness

**Interfaces:**

```python
def route_turnaround_valuation(
    *,
    series: Mapping[str, Any],
    profile: Mapping[str, Any],
    latest_price: Mapping[str, Any] | None,
    per_status: str,
    as_of_date: str,
) -> dict[str, Any]: ...

def build_turnaround_analysis(... ) -> dict[str, Any]: ...
```

- [x] Write failing tests for method priority `P/E handoff -> FCF -> OCF -> EBITDA -> gross profit -> sales -> survival only`.
- [x] Assert stale market cap (>7 calendar days from latest price basis), missing cash/debt, non-USD unit, unsupported sector, and non-positive denominator suppress numeric output with exact reason codes.
- [x] Assert a blocked D&A/valuation section does not hide READY operating/cash charts.
- [x] Implement EV/equity numerator consistency, basis-date disclosure, `READY/PARTIAL/BLOCKED` section statuses, and limitations.
- [x] Run `tests.test_us_stock_turnaround` and existing `tests.test_us_stock_valuation`; expect PASS.
- [x] Update task evidence and commit `전환 분석 엔진과 가치평가 경계 구현`.

**2차 완료 조건:** milestone, risk, valuation, section readiness가 pure tests로 고정되고 negative/zero/stale input이 숫자로 노출되지 않는다.

---

## 3차 — Loader · Service · Collection

### Task 3.1: One-symbol bounded loader

**Files:** Create `finance/loaders/us_stock_turnaround.py`; Modify `tests/test_us_stock_turnaround.py`.

**Interfaces:**

```python
def load_us_stock_turnaround_inputs(
    symbol: str,
    *,
    as_of_date: str | None = None,
    visible_quarters: int = 20,
    query_fn: QueryFn | None = None,
) -> dict[str, Any]: ...

def build_us_stock_turnaround_collection_plan(
    symbol: str,
    *,
    as_of_date: str | None = None,
    loaded_inputs: Mapping[str, Any] | None = None,
    input_loader: Callable[..., dict[str, Any]] = load_us_stock_turnaround_inputs,
) -> dict[str, Any]: ...
```

- [x] Write RED query-spy tests requiring exact symbol predicate, `available_at <= as_of`, duration+instant separation, relevant concept/unit filters, maximum seven fiscal years, and bounded price/profile rows.
- [x] Assert identity mismatch is ERROR, raw gaps map only to `asset_profile/prices/sec_statements`, and intrinsic economic/sector limitations never become collection scopes.
- [x] Implement loader/preflight and run focused tests to GREEN.

### Task 3.2: JSON-safe service and combined failure isolation

**Files:** Create `app/services/overview/us_stock_turnaround.py`; Modify `app/services/overview/market_context_valuation.py`; Modify tests.

**Interfaces:**

```python
def build_us_stock_turnaround_read_model(
    *,
    selected_symbol: str | None,
    loaded_inputs: Mapping[str, Any] | None = None,
    per_model: Mapping[str, Any] | None = None,
) -> dict[str, Any]: ...
```

- [x] Write RED tests that no symbol returns `NOT_SELECTED` without loader/provider calls; selected symbol produces JSON-safe timeline/sections and exact action scopes.
- [x] Write RED combined-service tests: S&P stays byte-equivalent, PER result fields stay unchanged, turnaround failure is isolated, and `recommended_analysis` is `per` only when current positive TTM EPS plus existing Graph 1 READY contract holds.
- [x] Implement the service and attach `turnaround_analysis`/`recommended_analysis` to the existing U.S.-stock payload; bump only combined schema version.
- [x] Run service and Market Context tests to GREEN.

### Task 3.3: Selected profile/price/SEC synchronous collection and resume

**Files:** Modify `finance/data/asset_profile.py`, `app/jobs/ingestion_jobs.py`, `app/jobs/overview_actions.py`, `app/web/overview/market_context_helpers.py`, and tests.

**Interfaces:**

```python
def collect_and_store_asset_profiles(..., symbols: Iterable[str] | None = None): ...
def run_collect_us_stock_turnaround_inputs(..., collect_profile: bool, collect_prices: bool, collect_statements: bool, ... ) -> JobResult: ...
def run_overview_us_stock_turnaround_collection(symbol: str, ...) -> JobResult: ...
```

- [x] Write RED tests that selected-symbol profile collection never expands to the full stock universe and existing default broad collection remains unchanged.
- [x] Assert symbol/CIK mismatch fails before all runners, exact scopes call each runner at most once, partial successes persist, and recheck narrows the retry scopes.
- [x] Assert search/render/local analysis-tab switch perform zero action/provider calls.
- [x] Implement selected-symbol filtering, the validated low-level job, overview facade, Streamlit event id `collect_us_stock_turnaround`, cache clear, and result reflection.
- [x] Run turnaround, existing U.S.-stock valuation, and Market Context regression tests.
- [x] Update task evidence and commit `전환 분석 로더와 선택 종목 수집 연결`.

**3차 완료 조건:** read path는 provider call 0회이고, 명시 action만 identity-validated one-symbol scopes를 수집하며 partial retry가 이미 충족된 scope를 반복하지 않는다.

---

## 4차 — 내부 selector와 UI

### Task 4.1: Inner analysis routing and negative-PER protection

**Files:** Create `TurnaroundAnalysis.tsx`; Modify `MarketContextValuation.tsx`; Modify `tests/test_market_context_valuation.py`.

- [ ] Write RED source/contract tests for `PER 상대가치`, `전환 분석`, `recommended_analysis`, selected-symbol-only selector, and no negative P/E rendering on the turnaround default.
- [ ] Implement symbol-keyed local analysis state: a new symbol adopts the service recommendation; user choice persists for the same symbol across rerenders.
- [ ] Keep current `ReadyValuation` and PER `StockState` unchanged inside the PER branch; render turnaround independently even when PER is NOT_APPLICABLE/COLLECTABLE.
- [ ] Run Market Context tests to GREEN.

### Task 4.2: Milestone rail, charts, risk and valuation cards

- [ ] Write RED contracts for 8/12/20-quarter selector, Graph 1 revenue YoY plus separate margin scale, Graph 2 TTM OCF/FCF, zero axes, gap segments, runway/debt/dilution cards, and valuation blocked reasons.
- [ ] Implement `TurnaroundAnalysis.tsx` with color-independent labels, keyboard-operable buttons, semantic SVG labels, and inspector fields for raw quarter/TTM/available_at.
- [ ] Ensure the period selector slices visible slots only and never recomputes metric definitions.
- [ ] Add responsive CSS: charts stack, risk cards become one column, and no component width exceeds the 420px viewport.
- [ ] Run TypeScript/Vite build; expect success and update the existing `component_static` product bundle.
- [ ] Run existing S&P/PER React source contracts and focused Python tests.
- [ ] Update task evidence and commit `미국 개별주식 전환 분석 화면 추가`.

**4차 완료 조건:** 적자/PER-history 부족 종목은 전환 분석이 기본이고, 사용자는 같은 종목에서 기존 PER로 전환할 수 있으며 S&P/PER 화면은 회귀하지 않는다.

---

## 5차 — Actual QA · Docs · Final Verification

### Task 5.1: Actual DB and edge-case verification

- [ ] Run read-only services for RIVN, LCID, PLTR and record discrete-quarter counts, headline, section readiness, missing reasons, and latency.
- [ ] Run AMD/AAPL and confirm `recommended_analysis=per`, existing Graph 1 READY, and unchanged current PER payload values.
- [ ] Exercise fixture cases for missing gross profit, stale profile, dilution, debt/interest, split, future filing/restatement, and intrinsic unsupported sector.
- [ ] Do not collect externally unless an actual selected-symbol gap explicitly requires the approved action; record any unrun collection accurately.

### Task 5.2: Focused/full regression and Browser QA

- [ ] Run `.venv/bin/python -m unittest tests.test_us_stock_turnaround tests.test_us_stock_valuation tests.test_market_context_valuation -v`.
- [ ] Run isolated full regression with the repository's established unittest command; record pass/fail and unrelated failures separately.
- [ ] Run `npm run build` in `app/web/streamlit_components/market_context_valuation`.
- [ ] Run target `py_compile`, `git diff --check`, and `git status --short`.
- [ ] Start the Finance app and perform actual Browser QA for desktop and 420px: RIVN/LCID/PLTR turnaround, AMD/AAPL PER handoff, selector switching, collection CTA presence only, console errors 0, horizontal overflow 0.
- [ ] Save one generated QA screenshot outside staged files and attach it in the final report.

### Task 5.3: Documentation alignment and closeout

- [ ] Update `STATUS.md`, `NOTES.md`, `RUNS.md`, `RISKS.md` with actual evidence and remaining gaps.
- [ ] Use `finance-doc-sync` to align `docs/INDEX.md`, `docs/ROADMAP.md`, `docs/PROJECT_MAP.md`, relevant architecture/flow/data docs, and concise root handoff logs.
- [ ] Fresh-run completion verification under `superpowers:verification-before-completion`.
- [ ] Stage only owned source/tests/docs/static bundle; exclude research folder, screenshot, run history, temp files, and Playwright artifacts.
- [ ] Commit coherent closeout as `전환 분석 QA와 문서 정렬`.

**5차 완료 조건:** fresh focused/full/build/browser evidence가 남고, actual DB에서 RIVN/LCID/PLTR 전환 분석과 AMD/AAPL PER handoff를 검증하며 문서와 코드 상태가 일치한다.

## Stop Condition

- roadmap 5/5차 완료 또는 검증 불가 항목을 이유와 함께 명확히 기록한다.
- S&P/PER regression, PIT correctness, collection boundary, mobile overflow 중 하나라도 실패하면 전체 완료로 표현하지 않는다.
- `git status --short`에서 의도한 변경과 지정된 unrelated research folder만 남아야 한다.

## Plan Self-Review

- Spec coverage: DESIGN의 resolver, engine, loader/service, collection, UI, QA/docs 요구를 1차~5차에 모두 매핑했다.
- Placeholder scan: 미정 표식이나 추상적인 후속 구현 단계가 없다.
- Type consistency: loader -> service -> combined payload -> React, collection plan -> ingestion job -> overview facade -> event bridge 인터페이스를 단일 이름으로 고정했다.
- Scope check: V1 selected-company 분석만 포함하며 screener/peer/target-price/new table은 제외했다.
