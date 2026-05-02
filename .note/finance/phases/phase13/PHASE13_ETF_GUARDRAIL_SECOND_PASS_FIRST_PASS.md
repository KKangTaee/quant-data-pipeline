# Phase 13 ETF Guardrail Second Pass First Pass

## What Changed

- Added second-pass ETF guardrail inputs to:
  - `GTAA`
  - `Risk Parity Trend`
  - `Dual Momentum`
- The ETF strategy UI now exposes:
  - `Underperformance Guardrail`
  - `Drawdown Guardrail`
- These values now round-trip through:
  - single strategy forms
  - compare overrides
  - history / `Load Into Form`
  - saved portfolio compare context

## Easy Explanation

- `Underperformance Guardrail`
  - 기본 뜻:
    최근 몇 개월 동안 전략 수익률이 benchmark보다 너무 약하면 다음 리밸런싱은 현금으로 쉬게 하는 규칙
  - 왜 필요한가:
    ETF 전략이 장기적으로는 괜찮아 보여도, 최근 상대 약세가 너무 심하면 바로 실전에 넣기 부담스럽기 때문
- `Drawdown Guardrail`
  - 기본 뜻:
    최근 낙폭이 너무 깊거나 benchmark보다 낙폭이 지나치게 나쁘면 다음 리밸런싱은 현금으로 쉬게 하는 규칙
  - 왜 필요한가:
    단순 CAGR만 보고 실전형으로 올리면, 실제 운용 중 큰 손실 구간을 방치할 수 있기 때문

## Runtime Contract

- ETF runtime wrappers now accept:
  - `underperformance_guardrail_enabled`
  - `underperformance_guardrail_window_months`
  - `underperformance_guardrail_threshold`
  - `drawdown_guardrail_enabled`
  - `drawdown_guardrail_window_months`
  - `drawdown_guardrail_strategy_threshold`
  - `drawdown_guardrail_gap_threshold`
- These values are passed through:
  - `finance/sample.py`
  - `finance/strategy.py`
  - `app/web/runtime/backtest.py`

## Strategy Behavior

- `GTAA`
  - if ETF guardrail is in `risk_off`, the next rebalance goes to cash
  - this is stricter than the existing `defensive_bond_preference` fallback
  - reason:
    guardrail is treated as a stronger protection rule than normal ETF risk-off preference
- `Risk Parity Trend`
  - if ETF guardrail is in `risk_off`, the next rebalance goes to cash
- `Dual Momentum`
  - if ETF guardrail is in `risk_off`, the next rebalance goes to cash

## Result Surface

- ETF result rows now include:
  - `Underperformance Guardrail State`
  - `Underperformance Guardrail Triggered`
  - `Underperformance Guardrail Excess Return`
  - `Drawdown Guardrail State`
  - `Drawdown Guardrail Triggered`
  - `Drawdown Guardrail Strategy Drawdown`
  - `Drawdown Guardrail Benchmark Drawdown`
  - `Drawdown Guardrail Gap`
- `build_backtest_result_bundle(...)` and `_apply_real_money_hardening(...)` now pick up ETF guardrail trigger counts in the same way as strict annual

## Important Boundary

- This is a second-pass ETF guardrail layer.
- It does **not** solve:
  - point-in-time ETF operability history
  - AUM/spread actual block rule
  - full probation workflow
- Current meaning:
  - ETF strategies can now be reviewed with actual guardrail-trigger behavior, not only with read-only promotion overlays

## Verification

- `py_compile`
  - `finance/strategy.py`
  - `finance/sample.py`
  - `app/web/runtime/backtest.py`
  - `app/web/pages/backtest.py`
- import smoke:
  - `app.web.pages.backtest`
  - `app.web.runtime.backtest`
- DB-backed ETF smoke:
  - `GTAA`
  - `Risk Parity Trend`
  - `Dual Momentum`
- Verified:
  - ETF result rows contain guardrail columns
  - runtime meta contains ETF guardrail trigger counts
  - single/compare/history prefill payloads now carry ETF guardrail values
