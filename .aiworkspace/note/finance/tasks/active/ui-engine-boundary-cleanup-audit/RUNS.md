# UI Engine Boundary Cleanup Audit Runs

Status: Complete
Created: 2026-05-27

## Commands

```bash
sed -n '1,220p' .aiworkspace/note/finance/docs/PROJECT_MAP.md
sed -n '1,220p' .aiworkspace/note/finance/docs/architecture/SCRIPT_STRUCTURE_MAP.md
sed -n '1,180p' .aiworkspace/note/finance/docs/flows/BACKTEST_UI_FLOW.md
.venv/bin/python .aiworkspace/plugins/quant-finance-workflow/scripts/check_ui_engine_boundary.py
rg -n "from app\\.web\\.|import app\\.web\\." app/services app/runtime -g '*.py'
wc -l app/web/backtest_practical_validation_curve.py app/web/backtest_practical_validation_connectors.py app/services/backtest_practical_validation_diagnostics.py app/services/backtest_practical_validation_replay.py app/runtime/backtest.py app/runtime/final_selected_portfolios.py app/runtime/candidate_library.py tests/test_service_contracts.py
find app/services app/runtime app/web -maxdepth 1 -type f -name '*.py' | sort
rg -n "^(def|class) " app/web/backtest_practical_validation_curve.py app/web/backtest_practical_validation_connectors.py app/services/backtest_practical_validation_diagnostics.py app/services/backtest_practical_validation_replay.py
rg -n "^(def|class) " app/runtime/backtest.py app/runtime/final_selected_portfolios.py app/runtime/candidate_library.py
```

## Results

- Boundary lint result: PASS.
- Hard violations: none.
- Advisory imports: 3.
- Browser QA: not applicable for this document/audit-only task.
