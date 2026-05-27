# Runtime Wrapper Cleanup Design

Status: Complete
Created: 2026-05-27

## Current File Shape

`app/runtime/backtest.py`는 5191 line runtime wrapper다.

초기 함수군 map:

| Line Range | Function Family | Notes |
| --- | --- | --- |
| 77-111 | public errors / constants | `BacktestInputError`, `BacktestDataError`, Real-Money / strict policy constants |
| 110-192 | basic input helpers | strategy family inference, ticker normalization, date validation, summary frequency |
| 194-337 | preflight / weight helpers | DB price preflight, list/float coercion, weight map, turnover estimate |
| 337-620 | transaction cost / benchmark helpers | transaction cost postprocess, candidate universe EW benchmark, benchmark result frame |
| 621-1753 | Real-Money / policy surface builders | validation, rolling/OOS review, promotion, shortlist, probation, deployment readiness, benchmark/liquidity/validation/guardrail/ETF policy |
| 1753-2084 | Real-Money hardening orchestration | applies transaction cost, benchmark, policy surfaces, meta warnings |
| 2084-2420 | strict preflight / freshness helpers | dynamic universe price pool, strict statement preflight, price freshness diagnosis |
| 2420-2598 | result bundle builder | UI-facing result bundle shape and metadata contract |
| 2598-3294 | ETF strategy public wrappers | Equal Weight, GTAA, Global Relative Strength, Risk Parity Trend, Dual Momentum |
| 3294-3944 | quality / statement quality wrappers | Quality Snapshot, shared statement quality bundle, strict annual quality, statement prototype |
| 3944-5191 | strict value / quality+value wrappers | annual / quarterly strict value and quality+value wrappers |

## Boundary Direction

Keep public wrappers in `app/runtime/backtest.py` for now.
Split only low-risk helper modules that do not change runtime behavior.

Preferred split order:

1. Result bundle contract helper
2. Public runtime contract constants / errors
3. Policy surface / Real-Money hardening, only after characterization coverage improves
4. Strategy-family wrappers, only after smoke tests and caller migration plan exist

## 8-04 First Split Candidate

The safest first split is the result bundle helper because:

- It is already a pure transformation over `result_df` and `input_params`.
- It is imported by `app/services/backtest_weighted_portfolio.py` as a public helper.
- Keeping `build_backtest_result_bundle` re-exported from `app.runtime.backtest` preserves caller compatibility.
- It does not call DB loaders or strategy engines.

Candidate file:

```text
app/runtime/backtest_result_bundle.py
```

Expected responsibility:

- `build_backtest_result_bundle`
- strategy family inference used by bundle metadata

Public compatibility:

- `app.runtime.backtest.build_backtest_result_bundle` remains available.
- `app.runtime.build_backtest_result_bundle` remains available through package export.

## Applied Split

`app/runtime/backtest_result_bundle.py` now owns the result bundle construction helper.
`app/runtime/backtest.py` imports and re-exports `build_backtest_result_bundle` so existing callers do not need to change.

Characterization coverage:

- `app.runtime.backtest.build_backtest_result_bundle` identity matches the helper module function.
- `app.runtime.build_backtest_result_bundle` identity matches the helper module function.
- Bundle construction sorts dates, keeps summary/chart/meta shape, and rejects missing required columns.
