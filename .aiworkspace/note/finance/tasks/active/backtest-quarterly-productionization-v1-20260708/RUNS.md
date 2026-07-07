# Runs

## 2026-07-08

- `cat /Users/taeho/.codex/skills/finance-task-intake/SKILL.md`
- `cat /Users/taeho/.codex/skills/finance-backtest-web-workflow/SKILL.md`
- `cat /Users/taeho/.codex/skills/finance-factor-pipeline/SKILL.md`
- `cat /Users/taeho/.codex/skills/finance-db-pipeline/SKILL.md`
- `sed -n '1,220p' .aiworkspace/note/finance/docs/INDEX.md`
- `sed -n '1,220p' .aiworkspace/note/finance/docs/ROADMAP.md`
- `sed -n '1,240p' .aiworkspace/note/finance/docs/PROJECT_MAP.md`
- `sed -n '530,805p' .aiworkspace/note/finance/docs/flows/BACKTEST_UI_FLOW.md`
- `git status --short`
- `.venv/bin/python -m unittest tests.test_backtest_quarterly_productionization -v` (initial TDD failures, then passing after implementation)
- `.venv/bin/python -m py_compile app/runtime/backtest/runners/strict_factor.py app/services/backtest_execution.py app/services/backtest_compare_catalog.py app/services/backtest_strategy_catalog.py app/runtime/backtest/runner_catalog.py app/services/backtest_strategy_evidence_inventory.py app/web/backtest_common.py app/web/backtest_result_display.py app/web/backtest_analysis.py app/web/backtest_history_helpers.py app/web/backtest_single_forms/strict_factor.py app/web/backtest_single_forms/__init__.py app/web/backtest_compare/page.py`
- `.venv/bin/python -m unittest tests.test_backtest_quarterly_productionization tests.test_backtest_strategy_evidence_inventory tests.test_backtest_strategy_bridge -v` (12 tests passed)
- `.venv/bin/python -m unittest tests.test_service_contracts -v` (529 tests passed)
- Browser QA on `http://localhost:8526/backtest`: selected `Quality -> Strict Quarterly`, confirmed `Quality Snapshot (Strict Quarterly)`, `Run Strict Quarterly Quality Backtest`, no visible `Prototype` label, and caught residual `Research-only defaults` copy.
- `.venv/bin/python -m py_compile app/web/backtest_single_forms/strict_factor.py app/web/backtest_compare/page.py`
- `.venv/bin/python -m unittest tests.test_service_contracts.BacktestCandidateAnalysisHardeningTests.test_strict_factor_window_limit_blocks_more_than_five_years tests.test_service_contracts.BacktestCandidateAnalysisHardeningTests.test_strict_factor_single_annual_forms_apply_five_year_window_guard tests.test_service_contracts.BacktestCandidateAnalysisHardeningTests.test_strict_factor_single_quarterly_forms_apply_five_year_window_guard tests.test_service_contracts.BacktestCandidateAnalysisHardeningTests.test_strict_ui_exposes_pit_monthly_snapshot_universe_contract -v` (4 tests passed)
- `git diff --check`
- `.venv/bin/python -m unittest tests.test_service_contracts -v` (530 tests passed)
- Restarted Streamlit on `http://localhost:8526/backtest` after file-watcher-off QA, selected `Quality -> Strict Quarterly`, and confirmed the visible form shows formal quarterly copy, `2021/07/08` start date, `Defaults: quarterly statement snapshots...`, and no `Research-only defaults` / `Strict Quarterly Prototype` copy.
- Browser QA screenshot saved as local generated artifact `backtest-quarterly-productionization-v1-qa.png` and left untracked.
