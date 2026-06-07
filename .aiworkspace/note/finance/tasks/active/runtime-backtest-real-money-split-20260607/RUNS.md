# Runtime Backtest Real-Money Split Runs

## RED

Command:

```bash
.venv/bin/python -m unittest tests.test_service_contracts.BoundaryContractHardeningTests.test_backtest_runtime_facade_delegates_real_money_helpers_to_dedicated_module tests.test_service_contracts.BoundaryContractHardeningTests.test_real_money_runtime_module_owns_facade_helper_contracts
```

Result:

- Failed as expected.
- `app.runtime.backtest_real_money` did not exist.
- `app/runtime/backtest.py` still defined `_apply_real_money_hardening` and related helper functions.

## GREEN

Command:

```bash
.venv/bin/python -m py_compile app/runtime/backtest.py app/runtime/backtest_real_money.py tests/test_service_contracts.py
```

Result:

- Passed.

Command:

```bash
.venv/bin/python -m unittest tests.test_service_contracts.BoundaryContractHardeningTests.test_backtest_runtime_facade_delegates_real_money_helpers_to_dedicated_module tests.test_service_contracts.BoundaryContractHardeningTests.test_real_money_runtime_module_owns_facade_helper_contracts
```

Result:

- Passed. Existing `edgar` deprecation warnings appeared during import-only test execution.

## Focused Regression

Command:

```bash
.venv/bin/python -m unittest tests.test_service_contracts.BacktestRuntimeContractTests
.venv/bin/python -m unittest tests.test_service_contracts.BoundaryContractHardeningTests
```

Result:

- `BacktestRuntimeContractTests`: passed, `13` tests.
- `BoundaryContractHardeningTests`: passed, `7` tests.
- Existing `edgar` deprecation warnings and Streamlit no-runtime cache warning appeared during test startup.

## Final Verification

Command:

```bash
.venv/bin/python -m py_compile app/runtime/backtest.py app/runtime/backtest_real_money.py app/runtime/backtest_risk_on_momentum.py app/runtime/__init__.py tests/test_service_contracts.py
```

Result:

- Passed.

Command:

```bash
.venv/bin/python -m unittest tests.test_service_contracts
```

Result:

- Passed: `Ran 281 tests ... OK`.
- Existing `edgar` deprecation warnings and Streamlit no-runtime cache warnings appeared during test startup.

Command:

```bash
.venv/bin/python .aiworkspace/plugins/quant-finance-workflow/scripts/check_ui_engine_boundary.py
```

Result:

- Passed: `Hard violations: none`, `Advisories: none`, `Result: PASS`.
- Boundary checker saw `44` boundary files and `14` runtime files after adding `app/runtime/backtest_real_money.py`.

Command:

```bash
git diff --check
curl -fsS http://localhost:8501/_stcore/health
find .aiworkspace/note/finance/tasks/active -mindepth 1 -maxdepth 1 -type d | wc -l
```

Result:

- `git diff --check` passed.
- Streamlit health returned `ok`.
- Active task directory count returned `177`.

Command:

```bash
.venv/bin/python - <<'PY'
from app.runtime import backtest
from app.runtime.backtest_real_money import (
    ETF_REAL_MONEY_DEFAULT_BENCHMARK,
    _apply_real_money_hardening,
    _apply_transaction_cost_postprocess,
    _build_deployment_readiness_contract,
)
print(backtest._apply_real_money_hardening is _apply_real_money_hardening)
print(backtest._apply_transaction_cost_postprocess is _apply_transaction_cost_postprocess)
print(backtest._build_deployment_readiness_contract is _build_deployment_readiness_contract)
print(backtest.ETF_REAL_MONEY_DEFAULT_BENCHMARK == ETF_REAL_MONEY_DEFAULT_BENCHMARK)
PY
```

Result:

- Returned `True` for all four compatibility checks.
