# Runtime Backtest Risk-On Momentum Split Runs

## RED

Command:

```bash
.venv/bin/python -m unittest tests.test_service_contracts.BoundaryContractHardeningTests.test_backtest_runtime_facade_delegates_risk_on_momentum_to_dedicated_module tests.test_service_contracts.BoundaryContractHardeningTests.test_risk_on_momentum_runtime_module_owns_public_entrypoint
```

Result:

- Failed as expected.
- `app.runtime.backtest_risk_on_momentum` did not exist.
- `app/runtime/backtest.py` still defined `run_risk_on_momentum_5d_backtest_from_db`.

## GREEN

Command:

```bash
.venv/bin/python -m py_compile app/runtime/backtest.py app/runtime/backtest_risk_on_momentum.py tests/test_service_contracts.py
```

Result:

- Passed.

Command:

```bash
.venv/bin/python -m unittest tests.test_service_contracts.BoundaryContractHardeningTests.test_backtest_runtime_facade_delegates_risk_on_momentum_to_dedicated_module tests.test_service_contracts.BoundaryContractHardeningTests.test_risk_on_momentum_runtime_module_owns_public_entrypoint
```

Result:

- Passed. Existing `edgar` deprecation warnings appeared during import-only test execution.

## Regression Sweep

Command:

```bash
.venv/bin/python -m unittest tests.test_service_contracts
```

Result:

- Passed: `Ran 279 tests ... OK`.
- Existing `edgar` deprecation warnings and Streamlit no-runtime cache warnings appeared during test startup.

During the first sweep after extraction, two Risk-On Momentum tests still patched the old `app.runtime.backtest` facade dependency. The tests now patch `app.runtime.backtest_risk_on_momentum`, while keeping the public `BacktestDataError` assertion on the facade contract.

## Final Verification

Command:

```bash
.venv/bin/python -m py_compile app/runtime/backtest.py app/runtime/backtest_risk_on_momentum.py app/runtime/__init__.py tests/test_service_contracts.py
```

Result:

- Passed.

Command:

```bash
.venv/bin/python -m unittest tests.test_service_contracts
```

Result:

- Passed: `Ran 279 tests ... OK`.
- Existing `edgar` deprecation warnings and Streamlit no-runtime cache warnings appeared during test startup.

Command:

```bash
.venv/bin/python .aiworkspace/plugins/quant-finance-workflow/scripts/check_ui_engine_boundary.py
```

Result:

- Passed: `Hard violations: none`, `Advisories: none`, `Result: PASS`.

Command:

```bash
git diff --check
curl -fsS http://localhost:8501/_stcore/health
find .aiworkspace/note/finance/tasks/active -mindepth 1 -maxdepth 1 -type d | wc -l
```

Result:

- `git diff --check` passed.
- Streamlit health returned `ok`.
- Active task directory count returned `176`.

Command:

```bash
.venv/bin/python - <<'PY'
from app.runtime import run_risk_on_momentum_5d_backtest_from_db as public_runner
from app.runtime.backtest import run_risk_on_momentum_5d_backtest_from_db as facade_runner
from app.runtime.backtest_risk_on_momentum import run_risk_on_momentum_5d_backtest_from_db as module_runner
print(public_runner is facade_runner is module_runner)
PY
```

Result:

- Returned `True`.
