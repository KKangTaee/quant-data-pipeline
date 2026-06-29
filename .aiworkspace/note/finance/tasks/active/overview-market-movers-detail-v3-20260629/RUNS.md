# Overview Market Movers Detail V3 Runs

## 2026-06-29

```bash
PYTHONWARNINGS=ignore uv run python -m unittest tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests.test_market_mover_why_it_moved_read_model_carries_relative_volume_context tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests.test_market_movers_detail_panel_model_integrates_selected_mode_and_status_strip tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests.test_market_movers_ui_why_it_moved_is_selected_symbol_workflow
```

Result: RED first, then GREEN after implementation. Final targeted run: 3 tests, OK.

```bash
uv run python -m py_compile app/web/overview/market_movers.py app/web/overview/market_movers_helpers.py app/web/overview/components/market_movers.py app/services/overview/market_movers.py app/services/overview/why_it_moved.py
git diff --check
```

Result: both exit 0 during implementation check.

Final verification and Browser QA evidence will be appended before commit.

```bash
git status --short
```

Result before staging: source/test/task docs changed; pre-existing/local generated items remained unstaged (`finance/.DS_Store`, `.aiworkspace/note/finance/run_history/BACKTEST_RUN_HISTORY.jsonl`, `.superpowers/`).

```bash
git diff --check
```

Result: exit 0.

```bash
uv run python -m py_compile app/web/overview/market_movers.py app/web/overview/market_movers_helpers.py app/web/overview/components/market_movers.py app/services/overview/market_movers.py app/services/overview/why_it_moved.py
```

Result: exit 0.

```bash
uv run python -m pytest tests/test_service_contracts.py -q -k "market_mover or market_movers or why_it_moved"
```

Result: failed because local uv environment does not have `pytest` installed (`No module named pytest`).

```bash
PYTHONWARNINGS=ignore uv run python -m unittest tests.test_service_contracts -k market_mover
PYTHONWARNINGS=ignore uv run python -m unittest tests.test_service_contracts -k market_movers
PYTHONWARNINGS=ignore uv run python -m unittest tests.test_service_contracts -k why_it_moved
```

Result: fallback contract verification passed (`38 OK`, `22 OK`, `6 OK`).

```bash
uv run streamlit run app/web/streamlit_app.py --server.port 8525 --server.headless true
```

Browser QA result: Overview > Market Movers showed the 3차 selected-symbol workflow. Verified S&P 500 Daily, Top Losers mode, S&P 500 Weekly, NASDAQ empty coverage state, and 390px narrow viewport. Screenshot captured at `.aiworkspace/note/finance/run_artifacts/overview-market-movers-detail-v3-qa.png`.
