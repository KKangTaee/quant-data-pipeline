# UI Engine Boundary Cleanup Integration

Status: Active
Created: 2026-05-27

## Integration Order

1. Task 0: phase/task audit docs.
2. Task 6: remove Practical Validation service/runtime -> web helper imports.
3. Task 7: split Practical Validation diagnostics helpers after advisory imports are gone.
4. Task 8: map and safely clean runtime wrapper responsibilities.
5. Task 9: harden lint/test/docs and close phase.

## Verification Ladder

Use the smallest relevant checks first, then broaden near task closeout.

```bash
.venv/bin/python .aiworkspace/plugins/quant-finance-workflow/scripts/check_ui_engine_boundary.py
.venv/bin/python -m unittest tests.test_service_contracts
git diff --check
git status --short --untracked-files=all
```

For UI-visible task changes, additionally start the Streamlit app and use the browser to inspect the affected Backtest / Practical Validation screen.

## Files Likely To Conflict

- `app/services/backtest_practical_validation_diagnostics.py`
- `app/services/backtest_practical_validation_replay.py`
- `app/services/backtest_practical_validation_curve.py`
- `app/services/backtest_practical_validation_provider_context.py`
- `app/runtime/backtest.py`
- `tests/test_service_contracts.py`
- `.aiworkspace/plugins/quant-finance-workflow/scripts/check_ui_engine_boundary.py`
- `.aiworkspace/note/finance/docs/PROJECT_MAP.md`
- `.aiworkspace/note/finance/docs/architecture/SCRIPT_STRUCTURE_MAP.md`
- `.aiworkspace/note/finance/docs/flows/BACKTEST_UI_FLOW.md`

## Generated Artifacts Policy

Do not stage registry / saved / run history / run artifacts / Playwright output unless the user explicitly asks.
