# Runs

## 2026-06-29

- `PYTHONWARNINGS=ignore uv run python -m unittest tests.test_service_contracts -k market_movers_followup`
  - RED: failed before implementation because `_render_market_movers_universe_action` was missing and sector map still rendered `ov-sector-breadth-leader-strip`.
  - GREEN: passed after implementation.
- `git diff --check`
  - Passed.
- `uv run python -m py_compile app/web/overview/market_movers.py app/web/overview/market_movers_helpers.py app/web/overview/components/market_movers.py app/web/overview/components/common.py app/services/overview/market_movers.py app/services/overview/why_it_moved.py`
  - Passed.
- `uv run python -m pytest tests/test_service_contracts.py -q -k "market_mover or market_movers or why_it_moved"`
  - Failed because `pytest` is not installed in the current `.venv`.
- `PYTHONWARNINGS=ignore uv run python -m unittest tests.test_service_contracts -k market_mover`
  - Passed, 62 tests.
- `PYTHONWARNINGS=ignore uv run python -m unittest tests.test_service_contracts -k why_it_moved`
  - Passed, 6 tests.
- Browser QA on `http://localhost:8525`
  - SP500 daily: intraday refresh, universe refresh, reload controls visible; no Top universe caption; duplicate sector leader strip count 0.
  - Top 1000 daily: intraday refresh, disabled `유니버스 기준`, reload controls visible; no Top universe caption; duplicate sector leader strip count 0.
  - NASDAQ daily: intraday refresh, `Nasdaq 목록 갱신`, reload controls visible; no Top universe caption.
  - Narrow viewport 390x844: no horizontal overflow.
  - Screenshot: `.aiworkspace/note/finance/run_artifacts/market-movers-polish-v3-followup-top1000-qa.png`
