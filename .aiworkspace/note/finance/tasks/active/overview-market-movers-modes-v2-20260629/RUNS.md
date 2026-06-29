# Overview Market Movers Modes V2 Runs

## 2026-06-29

```bash
PYTHONWARNINGS=ignore uv run python -m unittest tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests.test_market_movers_snapshot_builds_context_only_exploration_mode_views tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests.test_market_movers_unusual_volume_view_explains_missing_baseline tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests.test_market_movers_ui_controls_include_explicit_exploration_mode
```

Result: RED first, then GREEN after implementation. Final targeted run: 3 tests, OK.

```bash
uv run python -m py_compile app/web/overview/market_movers.py app/web/overview/market_movers_helpers.py app/web/overview/components/market_movers.py app/services/overview/market_movers.py app/services/overview/why_it_moved.py
```

Result: exit 0.

Final verification and Browser QA evidence will be appended before commit.

```bash
git status --short
```

Result: intended code/test/task docs changed; existing `finance/.DS_Store`, `run_history/BACKTEST_RUN_HISTORY.jsonl`, and `.superpowers/` are dirty/untracked and must not be staged.

```bash
git diff --check
```

Result: exit 0.

```bash
uv run python -m pytest tests/test_service_contracts.py -q -k "market_mover or market_movers or why_it_moved"
```

Result: failed because this local environment does not have `pytest` installed: `No module named pytest`.

```bash
PYTHONWARNINGS=ignore uv run python -m unittest tests.test_service_contracts -k market_mover
PYTHONWARNINGS=ignore uv run python -m unittest tests.test_service_contracts -k market_movers
PYTHONWARNINGS=ignore uv run python -m unittest tests.test_service_contracts -k why_it_moved
```

Result: fallback contract tests passed.

- `market_mover`: 35 tests, OK.
- `market_movers`: 20 tests, OK.
- `why_it_moved`: 4 tests, OK.

```bash
uv run streamlit run app/web/streamlit_app.py --server.port 8526 --server.headless true
```

Result: Browser QA completed on port 8526 because 8525 was already in use.

Browser QA checks:

- SP500 Daily: command strip, five exploration modes, Top Gainers, Top Losers, and Unusual Volume transitions visible.
- SP500 Weekly: EOD DB read model, selected mode, and command strip visible.
- NASDAQ coverage: local DB showed `No Universe`; empty state explained Symbol Directory refresh need and showed `Nasdaq 목록 갱신`.
- Narrow viewport: controls, command strip, and NASDAQ empty state remained visible without incoherent overlap.
- Screenshot: `.aiworkspace/note/finance/run_artifacts/overview-market-movers-modes-v2-qa.png`.
