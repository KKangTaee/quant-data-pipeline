# Overview Market Interest News / SEC Split Runs

| Time | Command | Result |
|---|---|---|
| 2026-07-09 | `git status --short` | Existing untracked research bundle and generated QA PNGs only before this task |
| 2026-07-09 | `.venv/bin/python -m pytest tests/test_service_contracts.py -k 'market_interest' -q` | Failed: `.venv` has no pytest module |
| 2026-07-09 | `.venv/bin/python -m unittest tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests` | RED after test change: expected missing `news_catalysts` / `sec_filing_catalysts`; GREEN after implementation: 137 tests OK |
| 2026-07-09 | `.venv/bin/python -m py_compile app/services/overview/market_interest.py app/web/overview/market_movers_helpers.py` | OK |
| 2026-07-09 | `git diff --check` | OK |
| 2026-07-09 | Browser QA on temporary renderer harness | OK: `뉴스 리스트` and `SEC 공시 촉매` render separately; Form 144 row displays `SEC Form 144 · 제한/지배주식 매각 예정 통지` |
