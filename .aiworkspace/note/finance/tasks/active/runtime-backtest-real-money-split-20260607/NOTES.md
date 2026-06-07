# Runtime Backtest Real-Money Split Notes

## Key Decisions

- The split is helper-family based, not strategy-family based.
- `app/runtime/backtest_real_money.py` owns cost / turnover / benchmark / policy / readiness contracts together because `_apply_real_money_hardening` needs those helpers as one coherent unit.
- `app/runtime/backtest.py` remains the compatibility facade for existing imports from UI, services, and tests.

## Compatibility Notes

- The facade re-exports representative private helper functions used by existing tests and callers.
- Real-money metadata intentionally keeps the legacy `app.runtime.backtest._apply_transaction_cost_postprocess` source label because result-history readers may compare that string.
- The split does not reinterpret `Real-Money` or `Deployment Readiness` as live trading approval.

## Follow-Up Candidate

The largest remaining runtime body is the strict quality / value family wrapper set. That is better handled as 8C because it includes strategy family orchestration, DB preflight, and result bundle wiring rather than only contract helpers.
