# Runs

Status: Completed
Last Verified: 2026-06-07

## RED

```bash
.venv/bin/python -m unittest \
  tests.test_service_contracts.BoundaryContractHardeningTests.test_backtest_runtime_facade_delegates_strict_family_to_dedicated_module \
  tests.test_service_contracts.BoundaryContractHardeningTests.test_strict_runtime_module_owns_facade_runner_contracts
```

Result: expected failure before implementation.

- `app.runtime.backtest_strict` import was absent.
- `app/runtime/backtest.py` still owned strict function bodies.

## Implementation Checks

```bash
.venv/bin/python -m py_compile app/runtime/backtest.py app/runtime/backtest_strict.py tests/test_service_contracts.py
```

Result: passed.

```bash
.venv/bin/python -m unittest \
  tests.test_service_contracts.BoundaryContractHardeningTests.test_backtest_runtime_facade_delegates_strict_family_to_dedicated_module \
  tests.test_service_contracts.BoundaryContractHardeningTests.test_strict_runtime_module_owns_facade_runner_contracts
```

Result: passed.

```bash
.venv/bin/python - <<'PY'
from app.runtime import backtest
from app.runtime.backtest_strict import (
    inspect_strict_annual_price_freshness,
    run_quality_snapshot_strict_annual_backtest_from_db,
    run_value_snapshot_strict_annual_backtest_from_db,
    run_quality_value_snapshot_strict_annual_backtest_from_db,
)
print({
    "freshness": backtest.inspect_strict_annual_price_freshness is inspect_strict_annual_price_freshness,
    "quality": backtest.run_quality_snapshot_strict_annual_backtest_from_db is run_quality_snapshot_strict_annual_backtest_from_db,
    "value": backtest.run_value_snapshot_strict_annual_backtest_from_db is run_value_snapshot_strict_annual_backtest_from_db,
    "quality_value": backtest.run_quality_value_snapshot_strict_annual_backtest_from_db is run_quality_value_snapshot_strict_annual_backtest_from_db,
})
PY
```

Result: all values were `True`.

## Closeout Verification

```bash
.venv/bin/python -m py_compile app/runtime/backtest.py app/runtime/backtest_strict.py app/runtime/backtest_real_money.py app/runtime/backtest_risk_on_momentum.py tests/test_service_contracts.py
```

Result: passed.

```bash
.venv/bin/python .aiworkspace/plugins/quant-finance-workflow/scripts/check_ui_engine_boundary.py
```

Result: passed. Hard violations: none. Advisories: none.

```bash
.venv/bin/python -m unittest tests.test_service_contracts.BoundaryContractHardeningTests
```

Result: passed, 9 tests.

```bash
.venv/bin/python -m unittest tests.test_service_contracts.BacktestRuntimeContractTests
```

Result: passed, 13 tests.

```bash
.venv/bin/python -m unittest tests.test_service_contracts
```

Result: passed, 283 tests.

```bash
git diff --check
```

Result: passed.

```bash
curl -fsS http://localhost:8501/_stcore/health
```

Result: `ok`.

Browser screenshot QA was not run because this task changed runtime module boundaries, docs, and tests only; no Streamlit UI surface was changed.
