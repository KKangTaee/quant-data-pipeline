# Runs

## 2026-07-05 - Intake

Read:

- `finance-task-intake`
- `finance-backtest-web-workflow`
- `finance-doc-sync`
- `superpowers:test-driven-development`
- `.aiworkspace/note/finance/docs/INDEX.md`
- `.aiworkspace/note/finance/docs/ROADMAP.md`
- `.aiworkspace/note/finance/docs/PROJECT_MAP.md`
- `.aiworkspace/note/finance/docs/flows/BACKTEST_UI_FLOW.md`
- `app/web/backtest_practical_validation/page.py`
- `app/web/backtest_practical_validation/components.py`

Outcome:

- Scope classified as focused Backtest Practical Validation UI implementation with small doc/task sync.

## 2026-07-05 - RED Tests

```bash
.venv/bin/python -m unittest tests.test_backtest_refactor_boundaries.BacktestRefactorBoundaryTests.test_practical_validation_entry_surface_removes_context_only_distractions tests.test_backtest_refactor_boundaries.BacktestRefactorBoundaryTests.test_practical_validation_visual_shell_uses_light_square_surfaces
.venv/bin/python -m unittest tests.test_backtest_refactor_boundaries.BacktestRefactorBoundaryTests.test_practical_validation_fix_queue_react_surface_is_square
```

Outcome:

- First command failed because Practical Validation still rendered Reference help, market sentiment overlay, old command title, and dark rounded CSS tokens.
- Second command failed because the React Fix Queue CSS still used a gradient background and `8px` radius cards.

## 2026-07-05 - GREEN Implementation And QA

Implemented:

- Removed default `render_reference_contextual_help("practical_validation")` call.
- Removed default market sentiment overlay render and unused Practical Validation overlay helper.
- Updated command center copy to `Final Review 이동 전 검증 상태`.
- Updated Practical Validation CSS helper to white square surfaces.
- Updated Practical Validation Fix Queue React CSS to white square surfaces.
- Rebuilt the React bundle.

QA:

```bash
npm install && npm run build
.venv/bin/python -m py_compile app/web/backtest_practical_validation/page.py app/web/backtest_practical_validation/components.py app/web/components/practical_validation_fix_queue/component.py
.venv/bin/python -m unittest tests.test_backtest_refactor_boundaries.BacktestRefactorBoundaryTests
.venv/bin/python -m unittest tests.test_service_contracts.BacktestRuntimeContractTests.test_practical_validation_fix_queue_react_component_is_ui_only tests.test_service_contracts.PracticalValidationServiceContractTests
git diff --check
```

Browser QA:

```bash
http://localhost:8525/backtest
```

Checked in browser:

- Practical Validation opens.
- `Reference help - Backtest > Practical Validation` is not visible.
- `시장 심리 Context Overlay` / `CNN Fear & Greed` are not visible.
- Old title `검증 근거를 위한 후보 통제 화면` is not visible.
- New title `Final Review 이동 전 검증 상태` is visible.
- Practical Validation command / step surfaces have white backgrounds and `0px` radius.
- React Fix Queue root / status surfaces have white backgrounds and `0px` radius.
- screenshot saved as `backtest-practical-validation-entry-simplification-v1-qa.png`.

Outcome:

- focused tests passed
- frontend build passed after local `npm install`
- `npm audit` reported 2 dependency warnings
- py_compile passed
- `BacktestRefactorBoundaryTests`: 17 tests passed
- Practical Validation service plus component contract tests: 23 tests passed
- diff check passed
- Browser QA passed
