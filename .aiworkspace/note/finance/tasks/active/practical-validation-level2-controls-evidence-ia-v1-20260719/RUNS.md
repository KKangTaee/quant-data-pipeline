# Runs

## 2026-07-19 Baseline

- `.venv/bin/python -m pytest tests/test_backtest_practical_validation_decision_workspace.py tests/test_practical_validation_market_context_visual_contract.py -q`
  - Result: 34 passed, 3 existing edgar deprecation warnings.
- `npm run build` in `app/web/components/practical_validation_decision_workspace/frontend`
  - Result: Vite build passed, 175 modules transformed.
- Worktree detection
  - Result: linked worktree, branch `codex/backtest-dev`.

## 2026-07-19 TDD / Build

- Python read model / intent tests
  - Red: 3 expected failures before implementation.
  - Green: `28 passed`, 3 existing edgar deprecation warnings.
- Visual / boundary contract tests
  - Red: 5 expected failures before implementation.
  - Green focused suite: `91 passed`, 3 existing edgar deprecation warnings.
- React production build
  - Result: passed, 175 modules transformed.
- `git diff --check`
  - Result: passed.

## 2026-07-19 Actual Browser QA

- Desktop 1440px
  - Step 1 profile adjustment, Step 2 recheck mode, bottom audit disclosure placement confirmed.
  - Drawdown answer update projected MDD `-10%`; stored-period mode became selected; replay/result remained `NOT_RUN` as designed.
  - Audit disclosure exposed exactly `후보 원본 / 재검증 원본 / 판정 원본` and no editable settings.
- Responsive 760px
  - Outer / context iframe / decision iframe horizontal overflow: all false.
  - Profile question and recheck mode grids: one column each.
- Browser console errors: 0.
- QA artifact: `practical-validation-level2-controls-evidence-ia-desktop-qa.png` (local generated artifact, not committed).

## 2026-07-19 Final Verification

- Focused Python suite: `91 passed`, 3 existing edgar deprecation warnings.
- Target `py_compile`: passed.
- React production build: passed, 175 modules transformed.
- `git diff --check`: passed.
