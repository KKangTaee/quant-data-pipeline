# Risk-On Momentum 5D V1 Design

Status: Draft

## Implementation Direction

- Core swing logic lives outside Streamlit in `finance/`.
- DB-backed adapter lives in `app/runtime/backtest.py`.
- UI form / rendering stays in `app/web/backtest_*.py`.
- Generated full trade / scanner details are written under `.aiworkspace/note/finance/run_artifacts/`.

## Runtime Contract

- Required price fields: `symbol`, `date`, `open`, `high`, `low`, `close`, `volume`.
- Required frequency: daily OHLCV.
- Decision timing: D close signal, D+1 open execution.
- Position sizing: equal slot, `portfolio_value / max_total_positions`.
- Macro score scale: futures macro `Mean Z`.
- First executable exit mode: `fixed_pct`.

## Deferred

- `atr_based` actual exits
- `intraday_trigger`
- trailing stop
- `macro_filter_mode=ranking_penalty`
- dedicated scanner-only page
