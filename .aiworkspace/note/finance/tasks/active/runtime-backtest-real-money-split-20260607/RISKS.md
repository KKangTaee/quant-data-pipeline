# Runtime Backtest Real-Money Split Risks

## Residual Risks

- `app/runtime/backtest.py` remains large because strict quality / value strategy wrappers still live there.
- Private helper imports from `app.runtime.backtest` are preserved for compatibility, but future code should prefer `app.runtime.backtest_real_money` for real-money helper ownership.
- The real-money helper module still depends on DB-backed loader functions for benchmark and ETF operability policy surfaces.

## Mitigations

- Contract tests assert facade delegation and object identity for representative helper contracts.
- Full service contract tests are required before closeout.
- 8C should target strict quality / value family wrappers rather than broad mixed helper movement.
