# Risk-On Momentum 5D Productionization Design

State: active
Last Updated: 2026-07-26

## Approved Product Direction

사용자는 2026-07-26에 다음 단계형 방향을 승인했다.

1. 전략 계산과 반복 분석을 최적화한다.
2. Daily Swing 전용 compact validation evidence와 Level2 handoff를 구현한다.
3. 수동 검토 / stale / no-auto-order 정책을 연결한 뒤 production maturity로 전환한다.

성능만 고치고 `개발 중`을 유지하거나, 근거 없이 catalog label만 바꾸는 것은 완료안이 아니다.

## Current State

### Implemented

- S&P 500 / Top1000 / Top2000 / manual universe
- daily OHLCV warmup과 D close decision / D+1 open execution
- annual statement shadow의 point-in-time financial hard exclude
- futures macro Mean-Z `hard_filter` / `ranking_penalty` / `off`
- fixed percentage / ATR exit
- equal-slot position sizing
- trade log, scanner, monthly/yearly return, ticker contribution
- macro-off, random ranking, SPY/QQQ, V2 comparison/sensitivity/stability evidence
- result bundle, history replay, Swing Detail UI

### Intentionally Deferred

- Daily Swing Practical Validation module
- Final Review selected-route rule
- Portfolio Monitoring daily cadence / stale policy
- compact artifact evidence storage boundary
- current membership와 historical PIT membership의 구분 / survivorship review

### Why The UI Says Development

`app/services/backtest_strategy_catalog.py`는 Risk-On을 유일한 `development`
strategy로 분류한다. 이 maturity는 presentation label만이 아니라
`build_level1_technical_handoff_readiness(...)`의 Level2 차단 조건이다.
따라서 production label 변경은 downstream contract가 준비된 뒤 마지막에 수행한다.

## Performance Evidence

실측 조건:

- universe: Top1000
- backtest range: 2024-07-26 through 2026-07-24
- warmup: start minus 180 calendar days
- price rows: 610,253
- prepared candidate feature rows: 609,005
- trading dates: 500

실측:

| Stage | Elapsed |
|---|---:|
| Universe resolution | 0.034s |
| Price DB load | 3.006s |
| Statement DB load | 0.250s |
| Futures macro load / score | 0.055s |
| Feature preparation | 3.008s |
| Primary simulation | 18.616s |
| Three random simulations | 55.631s |

Default runtime repeats the full simulation 57 times:

- primary: 1
- separately computed macro-off: 1
- random ranking: 50
- comparison suite additional variants: 5

Sensitivity adds 11 more runs. The comparison suite recomputes a macro-off result that
the wrapper already owns.

The single-run hot path builds a dict for every universe row on every date with
`day_rows.iterrows()`. A 500-day Top1000 run performs roughly 500,000 Series-to-dict
conversions. Profiling observed about 15.7 million `Series.__getitem__` calls and
about 496,000 `DataFrame.iterrows` rows in the measured process.

## Architecture

### 1. Prepared Simulation Data

Introduce a strategy-owned immutable prepared simulation object in `finance/swing.py`.
It will contain:

- the feature frame with required ATR column
- ordered in-range trading dates
- date-to-frame lookup
- date-to-position integer lookup
- per-date symbol index or equivalent O(1) access for held/pending symbols

The runtime wrapper prepares this object once and passes it to primary, macro,
random, comparison and sensitivity variants. Public callers that only supply
`prepared_features` remain compatible.

The prepared object must not contain portfolio state, RNG state or mutable result rows.
Each variant still owns independent cash, positions, pending orders and RNG.

### 2. Simulation Hot Path

Replace whole-day `iterrows()` conversion with indexed access:

- keep the per-date DataFrame for vectorized eligibility/ranking
- use indexed lookup only for held symbols and pending orders
- scanner row iteration remains bounded by `scanner_top_n_per_day`
- compute holding days from date positions instead of scanning the complete date list

These changes must preserve:

- D close signal and D+1 open execution
- entry/exit prices and fees
- rank ordering and seeded random ordering
- trade log fields
- result balance and return values

### 3. Variant Execution Plan

Build one explicit execution plan before running variants. Each plan entry identifies:

- analysis role
- effective config
- whether full scanner evidence is required
- cache key excluding presentation-only fields

Identical effective variants reuse an existing result. In particular, the wrapper's
macro-off result is reused by the comparison suite.

### 4. Analysis Intensity

Expose a user-facing analysis intensity rather than making users infer cost from
three advanced controls.

| Intensity | Contract | Intended use |
|---|---|---|
| 빠른 실행 | primary + SPY/QQQ; no random/comparison/sensitivity variants | settings iteration |
| 표준 검증 | primary + macro-off + 10 random + comparison variants; sensitivity off | default candidate review |
| 정밀 검증 | 50 random + comparison + sensitivity variants | explicit deep research |

The primary settings schema defaults to `표준 검증`. It projects the three modes to
`(random_iterations, run_comparison_suite, run_sensitivity_suite)` as
`(0, false, false)`, `(10, true, false)`, and `(50, true, true)`.
The result metadata records requested intensity, actual distinct simulation count and
reused-variant count. Existing saved/history payloads without the new field preserve
their explicit three controls and are reported as `custom_legacy`.

The UI may show estimated relative workload before execution, but it will not add
a run/job/row diagnostic panel.

### 5. Daily Swing Compact Evidence

The result bundle will expose a compact, JSON-safe Daily Swing evidence packet containing:

- period and universe source
- universe membership mode and PIT/survivorship status
- trade count, win rate, average/max holding period
- turnover or a clearly named unavailable status
- fees, slippage assumptions and high-cost sensitivity
- benchmark and random-ranking comparison
- macro mode/coverage
- concentration, year dependency and failed-trade causes
- raw artifact identity and row counts, not raw rows

Full trade log and scanner rows remain generated artifacts.

### 6. Practical Validation

Daily Swing validation is a distinct module, not a monthly/annual module relabel.
It interprets the compact packet with explicit states:

- `READY`: evidence is present and required thresholds are satisfied
- `REVIEW`: evidence exists but needs Final Review judgment
- `NEEDS_INPUT`: required data/evidence was not run or is missing
- `BLOCKED`: PIT/survivorship or execution evidence prevents promotion

Thresholds are policy inputs owned by the validation module. Missing data is never a pass.

### 7. Final Review And Monitoring

Final Review can only receive a saved Practical Validation result from an explicit user action.
The Daily Swing selected route:

- starts as manual review
- records strategy horizon and evidence limitations
- never implies live approval

Portfolio Monitoring, when selected:

- treats the strategy as a reviewed research/monitoring candidate
- has a defined daily review cadence
- expires stale signals
- requires a manual scenario/recheck action
- never creates broker orders or automatic rebalancing

### 8. Maturity Transition

The catalog stays `development` during 1차 and 2차. It moves to `production` only when:

- the 2-year performance acceptance test passes
- result parity tests pass
- Daily Swing validation can consume compact evidence
- Level2 handoff is explicit and fail-closed
- Final Review selected-route policy exists
- monitoring boundary is implemented or explicitly excluded without a false CTA

## Error Handling

- Invalid intensity or incompatible legacy controls fails input validation.
- Empty/insufficient price, statement or macro evidence keeps existing typed errors/warnings.
- Missing PIT membership is an evidence status, not silently treated as historical membership.
- Variant failures report the exact analysis role and do not relabel a partial deep run as complete.
- Artifact write failure must not silently mark downstream evidence as durable.

## Testing

### TDD Requirements

- Every production behavior change starts with a focused failing test.
- Each test must fail for the intended missing behavior before implementation.

### Core Tests

- baseline result parity for fixed and ATR exits
- seeded random parity
- indexed symbol lookup preserves missing-row handling
- O(1) holding-day calculation preserves current trade log values
- prepared simulation data is reused without leaking portfolio state
- duplicate variant plan entries execute once
- legacy payload mapping is deterministic

### Performance Test

- use actual Top1000 DB data when available
- same 2024-07-26 through 2026-07-24 acceptance range
- default standard mode target: at most 60 seconds on the current development machine
- record row count, distinct simulation count and elapsed time
- do not make a fragile wall-clock unit test part of the normal small test suite

### Workflow Tests

- compact evidence is JSON-safe and excludes raw trade/scanner rows
- PIT/current-universe status is explicit
- missing required evidence fails closed
- development strategy remains blocked before governance completion
- production transition enables only the approved handoff
- Final Review and Monitoring keep manual/no-order boundaries

### Browser QA

- strategy no longer appears under a misleading group after final maturity transition
- analysis intensity and cost implication are understandable
- two-year standard execution completes and result remains visible
- Level2 CTA appears only when fresh result and Daily Swing gate permit it
- attach one generated screenshot to final response; do not commit it

## Alternatives Considered

### Performance-only patch

Rejected as the final outcome because it leaves the user-visible `개발 중` state and
downstream gap unresolved.

### Label-only production promotion

Rejected because it would enable generic Level2 behavior before Daily Swing validation
and survivorship policy exist.

### Fully vectorized rewrite

Deferred unless indexed reuse cannot meet the acceptance target. It has larger semantic
risk for order timing, seeded ranking and trade-log parity.
