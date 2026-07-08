# Runs

Status: Active
Last Updated: 2026-06-29

## RED

```bash
PYTHONWARNINGS=ignore uv run python -m unittest tests.test_service_contracts.OverviewAutomationContractTests.test_market_movers_redesign_v2_uses_market_ranking_language tests.test_service_contracts.OverviewAutomationContractTests.test_market_movers_command_strip_model_summarizes_active_workbench_context tests.test_service_contracts.OverviewAutomationContractTests.test_market_movers_ui_controls_include_explicit_exploration_mode tests.test_service_contracts.OverviewAutomationContractTests.test_market_movers_detail_panel_model_integrates_selected_mode_and_status_strip
```

Result: failed as expected. The implementation still used `변동종목 작업대`, `탐색 모드`, and English mode labels. Two direct test paths were in a different unittest class, so follow-up focused `-k` runs were used.

## Focused GREEN

```bash
PYTHONWARNINGS=ignore uv run python -m unittest tests.test_service_contracts -k market_movers_redesign_v2
PYTHONWARNINGS=ignore uv run python -m unittest tests.test_service_contracts -k market_movers_command_strip_model
PYTHONWARNINGS=ignore uv run python -m unittest tests.test_service_contracts -k market_movers_ui_controls_include_explicit
PYTHONWARNINGS=ignore uv run python -m unittest tests.test_service_contracts -k market_movers_detail_panel_model
```

Result: all 4 focused tests passed.

## Common Verification

```bash
git status --short
git diff --check
uv run python -m py_compile app/web/overview/market_movers.py app/web/overview/market_movers_helpers.py app/web/overview/components/market_movers.py app/services/overview/market_movers.py app/services/overview/why_it_moved.py
uv run python -m pytest tests/test_service_contracts.py -q -k "market_mover or market_movers or why_it_moved"
```

Result:

- `git status --short`: working tree contains intended code/docs changes plus local generated artifacts.
- `git diff --check`: passed.
- `py_compile`: passed.
- `pytest`: failed because `.venv/bin/python3` has no `pytest` module.

Fallback:

```bash
PYTHONWARNINGS=ignore uv run python -m unittest tests.test_service_contracts -k market_mover
PYTHONWARNINGS=ignore uv run python -m unittest tests.test_service_contracts -k why_it_moved
```

Result: `market_mover` 44 tests passed; `why_it_moved` 6 tests passed.

## Browser QA

Command:

```bash
uv run streamlit run app/web/streamlit_app.py --server.port 8525 --server.headless true
```

Result:

- App started on `http://localhost:8525`.
- SP500 daily: `변동 종목`, `랭킹 기준`, `보기`, `상승 / 하락 / 거래량 / 이상 거래량 / 섹터` visible; old `변동종목 작업대` and `탐색 모드` absent.
- SP500 weekly: `S&P 500 · Weekly`, `가격 이력 갱신`, `보기`, and new ranking labels visible.
- NASDAQ coverage: `No Universe`, `Nasdaq 목록 갱신`, and context-only trust language visible.
- Narrow viewport `390x844`: no horizontal overflow detected; core controls and ranking labels visible.

Screenshot:

```text
.aiworkspace/note/finance/run_artifacts/market-movers-redesign-v2-01-command-strip-qa.png
```
