# Runs

## 2026-07-19 Baseline

- `.venv/bin/python -m pytest tests/test_backtest_practical_validation_decision_workspace.py tests/test_practical_validation_market_context_visual_contract.py -q`
  - Result: 34 passed, 3 existing edgar deprecation warnings.
- `npm run build` in `app/web/components/practical_validation_decision_workspace/frontend`
  - Result: Vite build passed, 175 modules transformed.
- Worktree detection
  - Result: linked worktree, branch `codex/backtest-dev`.
