# Runtime Backtest Real-Money Split Design

Status: Completed
Date: 2026-06-07

## Boundary

| File | Responsibility After 8B |
|---|---|
| `app/runtime/backtest.py` | Backtest runtime public compatibility facade, DB-backed strategy runner wrappers, shared preflight helpers |
| `app/runtime/backtest_real_money.py` | Real-money constants, ticker normalization compatibility helper, cost / turnover postprocess, benchmark overlay builder, validation / promotion / shortlist / probation / monitoring / deployment readiness contracts, ETF operability policy, `_apply_real_money_hardening` |
| `app/runtime/backtest_risk_on_momentum.py` | Risk-On Momentum 5D runtime slice from 8A |
| `app/runtime/backtest_result_bundle.py` | UI-facing result bundle creation |

## Compatibility Contract

Existing callers can still import constants and helper functions from `app.runtime.backtest`.

```python
from app.runtime.backtest import _apply_real_money_hardening
from app.runtime.backtest import _build_deployment_readiness_contract
```

The actual implementation now lives in:

```python
from app.runtime.backtest_real_money import _apply_real_money_hardening
from app.runtime.backtest_real_money import _build_deployment_readiness_contract
```

`tests/test_service_contracts.py` asserts that the facade and dedicated module objects are identical for representative helper contracts.

## Implementation Notes

- `_normalize_tickers` moved with the helper family because benchmark / ETF policy helpers need it and strategy runners already consume it through the facade.
- Empty ticker input still raises `app.runtime.backtest.BacktestInputError` through a lazy import, preserving the existing user-facing exception type without creating a top-level import cycle.
- The `cost_model_source` metadata string remains the legacy facade path for result-history compatibility.

## Not Changed

- No result bundle schema change.
- No warning text change.
- No cost / benchmark / promotion threshold behavior change.
- No live trading, broker approval, account sync, or auto-rebalance behavior.
