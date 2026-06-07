# Runtime Backtest Risk-On Momentum Split Design

Status: Completed
Date: 2026-06-07

## Boundary

| File | Responsibility After 8A |
|---|---|
| `app/runtime/backtest.py` | Backtest runtime public compatibility facade and shared ETF / strict family runtime helpers |
| `app/runtime/backtest_risk_on_momentum.py` | Risk-On Momentum 5D universe resolution, futures macro / swing execution orchestration, comparison suite wiring, generated swing artifact writer |
| `finance/swing.py` | Streamlit-free Risk-On Momentum scanner / trade loop |
| `finance/swing_analysis.py` | Streamlit-free comparison, sensitivity, stability, trade-cause, quality warning analysis |

## Compatibility Contract

Existing callers continue to import the runner from `app.runtime.backtest`.

```python
from app.runtime.backtest import run_risk_on_momentum_5d_backtest_from_db
```

The actual implementation now lives in:

```python
from app.runtime.backtest_risk_on_momentum import run_risk_on_momentum_5d_backtest_from_db
```

`tests/test_service_contracts.py` asserts that the two imported objects are identical.

## Not Changed

- No strategy math changes.
- No trade log / scanner / artifact schema changes.
- No generated artifact staging.
- No registry / saved JSONL rewrite.
- No Practical Validation / Final Review / Portfolio Monitoring governance link.
