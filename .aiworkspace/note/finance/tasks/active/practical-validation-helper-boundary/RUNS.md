# Practical Validation Helper Boundary Runs

Status: Complete
Created: 2026-05-27

## Initial Commands

```bash
rg -n "backtest_practical_validation_(curve|connectors)|build_provider_context|curve_records_from_df|build_benchmark_parity|build_curve_provenance|optional_float" app tests .aiworkspace/note/finance/docs -g '*.py' -g '*.md'
sed -n '1,260p' app/web/backtest_practical_validation_curve.py
sed -n '1,220p' app/web/backtest_practical_validation_connectors.py
sed -n '1,60p' app/services/backtest_practical_validation_diagnostics.py
sed -n '1,40p' app/services/backtest_practical_validation_replay.py
```

## Initial Result

- Code references to the old web helper modules are limited to diagnostics / replay services.
- Durable docs also reference the old web helper paths and need alignment.

## Verification Commands

```bash
rg -n "from app\\.web\\.|import app\\.web\\." app/services app/runtime -g '*.py'
.venv/bin/python .aiworkspace/plugins/quant-finance-workflow/scripts/check_ui_engine_boundary.py
.venv/bin/python -m unittest tests.test_service_contracts
git diff --check
```

## Verification Results

- Service/runtime `app.web` import check: no matches.
- Boundary lint: PASS, hard violations none, advisories none.
- Service contract tests: PASS.
- Browser QA: not applicable because only helper module ownership/import paths changed.
