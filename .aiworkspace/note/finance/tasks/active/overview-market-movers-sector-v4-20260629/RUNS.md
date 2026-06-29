# Overview Market Movers Sector V4 Runs

## 2026-06-29

```bash
PYTHONWARNINGS=ignore uv run python -m unittest tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests.test_market_movers_snapshot_adds_full_sector_breadth_context tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests.test_market_movers_ui_renders_sector_breadth_heatmap_workflow
```

Result: RED first. `sector_breadth` was missing from the snapshot and UI source did not import/render `render_breadth_heatmap_summary`.

```bash
PYTHONWARNINGS=ignore uv run python -m unittest tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests.test_market_movers_snapshot_adds_full_sector_breadth_context tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests.test_market_movers_ui_renders_sector_breadth_heatmap_workflow
```

Result: GREEN after implementation. 2 tests OK.

```bash
git diff --check
uv run python -m py_compile app/web/overview/market_movers.py app/web/overview/market_movers_helpers.py app/web/overview/components/market_movers.py app/services/overview/market_movers.py app/services/overview/why_it_moved.py
PYTHONWARNINGS=ignore uv run python -m unittest tests.test_service_contracts -k market_movers
PYTHONWARNINGS=ignore uv run python -m unittest tests.test_service_contracts -k market_mover
```

Result: implementation check passed.

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

Result: fallback contract verification passed (`40 OK`, `24 OK`, `6 OK`).

```bash
uv run streamlit run app/web/streamlit_app.py --server.port 8525 --server.headless true
```

Browser QA result: Overview > Market Movers showed the 4차 sector breadth / heatmap workflow. Verified S&P 500 Daily heatmap, S&P 500 Weekly EOD heatmap, NASDAQ no-universe empty state, and 390px narrow viewport with 11 sector tiles and fallback table present. Screenshot captured at `.aiworkspace/note/finance/run_artifacts/overview-market-movers-sector-v4-qa.png`.
