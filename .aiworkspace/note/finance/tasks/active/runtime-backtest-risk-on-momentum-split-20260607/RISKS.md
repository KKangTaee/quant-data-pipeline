# Runtime Backtest Risk-On Momentum Split Risks

## Remaining Risks

- `app/runtime/backtest.py` is still a large runtime facade after 8A.
- The new Risk-On Momentum module still calls shared `backtest.py` validation/freshness helpers at execution time.
- No actual DB-backed Risk-On Momentum run was executed in this task because it can create generated swing artifacts.

## Mitigations

- Contract tests preserve the public compatibility import path.
- Full service contracts and boundary checker are part of final verification.
- Generated `backtest_artifacts` remain out of commit scope unless explicitly requested.
