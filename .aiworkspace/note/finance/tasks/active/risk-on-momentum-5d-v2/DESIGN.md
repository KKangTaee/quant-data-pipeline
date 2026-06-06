# Risk-On Momentum 5D V2 Design

Status: Active

## Implementation Direction

- Indicator logic: `finance/indicators.py`
- Macro mode logic: `finance/swing_macro.py`
- Swing simulation: `finance/swing.py`
- Repeated analysis suites: `finance/swing_analysis.py`
- DB-backed orchestration and artifact payload: `app/runtime/backtest.py`
- Form / result / history UI: `app/web/backtest_single_forms.py`, `app/web/backtest_result_display.py`, `app/web/backtest_history_helpers.py`

## Runtime Contract

- ATR method: simple rolling mean, matching V1 `atr14` behavior.
- ATR exit timing: use signal-date ATR captured in the D close candidate row, then enter at D+1 open and keep the entry ATR fixed.
- Execution timing: still `close_based` D close decision and D+1 open execution / exit.
- `ranking_penalty`: `risk_on_min` remains a hard gate; pressure scores above thresholds subtract from `ranking_score` but do not block entry by themselves.
- Missing or stale macro evidence blocks entries when macro filtering is enabled.

## Deferred

- Daily Swing Practical Validation module.
- Final Review route values for paper / monitor / reject.
- Selected Dashboard Daily Signal / Paper Strategy Monitor lane.
- Wilder ATR, intraday trigger, trailing stop, broker/order/auto-trading behavior.
