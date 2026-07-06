# Runs

Commands and QA evidence will be appended per task.

## 2026-07-07 0차 Price Freshness Preflight

- RED: `.venv/bin/python -m unittest tests.test_service_contracts.BacktestCandidateAnalysisHardeningTests.test_price_freshness_preflight_react_component_is_ui_only -v` failed because `base: "./"` was missing from the preflight Vite config.
- Build: `npm run build` in `app/web/components/backtest_price_freshness_preflight/frontend` completed successfully.
- GREEN: the same focused unittest passed after rebuild.
- Compile: `.venv/bin/python -m py_compile app/web/backtest_common.py app/web/backtest_single_strategy.py app/web/backtest_single_forms/*.py app/web/components/backtest_price_freshness_preflight/component.py` completed successfully.
- Browser QA: Selenium opened `/backtest`, selected `Quality`, inspected the component iframe, and confirmed `Price Freshness Preflight` text rendered with `./assets/...` paths. Previous component asset MIME error was not present.
- Screenshot: `backtest-price-freshness-preflight-fixed-qa.png` generated locally and not intended for commit.

## 2026-07-07 1차 Strategy Detail Read Model

- RED: focused read-model tests failed with `ModuleNotFoundError` because `app/services/backtest_strategy_detail.py` did not exist yet.
- GREEN: focused read-model tests passed after adding `build_backtest_strategy_detail_model`.
- Compile: `.venv/bin/python -m py_compile app/services/backtest_strategy_detail.py` completed successfully.
- Diff check: `git diff --check -- app/services/backtest_strategy_detail.py tests/test_service_contracts.py .aiworkspace/note/finance/tasks/active/backtest-strategy-detail-react-v1-20260707` completed successfully.
